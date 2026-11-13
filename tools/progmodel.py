"""Rebuild/query the static L0 program model. No execution and no build mutation.

python tools/progmodel.py [--check | routine NAME | site FRAME:OFF | var NAME | scc | candidates]
See docs/program-model.md for the abstract domains and, especially, their limits.
"""
import argparse
from bisect import bisect_right
from collections import Counter, defaultdict, deque
import json
import re
import sys

from capstone import Cs, CS_ARCH_X86, CS_MODE_16, CS_AC_READ, CS_AC_WRITE
from capstone import x86_const as X
import cgen
import symtab as S
from common import ROOT, sha256
from where import mnemonic

OUT = ROOT / 'metadata/program-model.json'
FLAGS = ('cf', 'pf', 'af', 'zf', 'sf', 'tf', 'if', 'df', 'of')
FULL = ('ax', 'bx', 'cx', 'dx', 'si', 'di', 'bp', 'sp', 'cs', 'ds', 'es', 'ss')
TRACK = FULL + FLAGS
HALVES = {r: (r[0]+'l', r[0]+'h') for r in ('ax', 'bx', 'cx', 'dx')}
ATOMS = set(FLAGS) | set(FULL[4:]) | {x for v in HALVES.values() for x in v}
UNKNOWN = frozenset(('?',))
REG = X.X86_OP_REG
IMM = X.X86_OP_IMM
MEM = X.X86_OP_MEM


def address(frame, off):
    return f'{frame:04X}:{off:04X}'


def atoms(reg):
    return set(HALVES.get(reg, (reg,))) & ATOMS


def union(values):
    out = frozenset().union(*values)
    return UNKNOWN if '?' in out or len(out) > 12 else out


def display(values):
    return sorted(values, key=str)


def rw(ins):
    """Byte-register atoms; flags independently. Undefined flags are may writes.

    A may-write must not kill a live input (e.g. a variable zero shift count).
    """
    rr, ww = ins.regs_access()
    reads = set().union(*(atoms(ins.reg_name(r)) for r in rr))
    writes = set().union(*(atoms(ins.reg_name(r)) for r in ww))
    for flag in FLAGS:
        for action in ('TEST', 'PRIOR'):
            if ins.eflags & getattr(X, 'X86_EFLAGS_'+action+'_'+flag.upper(), 0):
                reads.add(flag)
        for action in ('MODIFY', 'RESET', 'SET', 'UNDEFINED'):
            if ins.eflags & getattr(X, 'X86_EFLAGS_'+action+'_'+flag.upper(), 0):
                writes.add(flag)
    m = mnemonic(ins).split()[-1]
    ops = ins.operands
    if m in ('xor', 'sub') and len(ops) == 2 and ops[0].type == ops[1].type == REG and ops[0].reg == ops[1].reg:
        reads -= atoms(ins.reg_name(ops[0].reg))
    for op in ops:
        if op.type == MEM and m != 'lea':
            reads.add(ins.reg_name(op.mem.segment) if op.mem.segment else
                      ('ss' if ins.reg_name(op.mem.base) in ('bp', 'sp') else 'ds'))
    if m in ('pushf', 'pushfd'):
        reads |= set(FLAGS)
    if m in ('popf', 'popfd', 'iret'):
        writes |= set(FLAGS)
    # Capstone 5 omits carry input for ADC/SBB and rotates through carry.
    if m in ('adc', 'sbb', 'rcl', 'rcr', 'cmc'):
        reads.add('cf')
    if m in ('push', 'pop', 'pushf', 'popf', 'call', 'lcall', 'ret', 'retf', 'iret', 'enter', 'leave'):
        reads |= {'ss', 'sp'}
    if m in ('pushaw', 'popaw'):
        reads |= {'ss', 'sp'}
    if m in ('lodsb', 'lodsw', 'movsb', 'movsw', 'stosb', 'stosw', 'scasb', 'scasw', 'cmpsb', 'cmpsw'):
        reads.add('df')
    must = set(writes)
    if m in ('rcl', 'rcr', 'rol', 'ror', 'shl', 'shr', 'sar', 'sal'):
        # A variable/zero count can preserve the operand and flags.
        if len(ops) > 1 and (ops[1].type != IMM or ops[1].imm == 0):
            reads |= writes
            must.clear()
    return reads, writes, must


def tarjan(graph):
    index = {}; low = {}; active = set(); stack = []; groups = []
    def visit(v):
        index[v] = low[v] = len(index); stack.append(v); active.add(v)
        for w in sorted(graph[v]):
            if w not in index:
                visit(w); low[v] = min(low[v], low[w])
            elif w in active:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            group = []
            while True:
                w = stack.pop(); active.remove(w); group.append(w)
                if w == v: break
            groups.append(sorted(group))
    for v in sorted(graph):
        if v not in index: visit(v)
    return sorted(groups, key=lambda g: (-len(g), g))


class Model:
    def __init__(self):
        self.mz, self.symbols = cgen.read_symbols()  # validates source receipt, image and relocations
        self.relocs = set(self.mz.sites)
        self.rs = sorted(S.routines(), key=lambda r: (r['frame'], r['offset']))
        if len(self.rs) != 284:
            raise ValueError('routine census changed; review the model boundary')
        self.names = S.names()['symbols']
        self.layout = S.load_json('data-layout.json')
        self.byaddr = {address(r['frame'], r['offset']): r for r in self.rs}
        self.rid = {a: r['module']+':'+r['name'] for a, r in self.byaddr.items()}
        self.entry = {v: k for k, v in self.rid.items()}
        self.ins = {}; self.site = {}; self.lines = {}; self.edges = defaultdict(list)
        self.bodies = {}; self.owners = defaultdict(set); self.transfers = {}
        self.summaries = {}; self.states = {}; self.varsites = defaultdict(set)
        self.symbol_at = defaultdict(list)
        self.source_names = defaultdict(dict)
        for rec in self.names.values():
            if rec['kind'] in ('data', 'c-global'):
                self.symbol_at[rec['address']].append(rec['name'])
                for sp in rec['spellings']:
                    self.source_names[sp['module']][sp['name'].lower()] = rec['name']
        self.data_offsets = defaultdict(list)
        self.data_objects = []
        for module in self.layout['modules']:
            for obj in module['objects']:
                self.data_objects.append(dict(id=module['name']+':'+f'{obj["start"]:04X}',
                    start=module['frame']*16+obj['start'], end=module['frame']*16+obj['end'],
                    description=obj.get('comment','')))
        for a in self.symbol_at:
            f, o = (int(x, 16) for x in a.split(':')); self.data_offsets[f].append(o)
        for f in self.data_offsets: self.data_offsets[f] = sorted(set(self.data_offsets[f]))

    def decode(self):
        cs = Cs(CS_ARCH_X86, CS_MODE_16); cs.detail = True
        spans = []
        for module in S.load_json('asm-map.json')['modules']:
            f = module['frame']
            text = (ROOT/f'src/asm/{module["name"]}.ASM').read_text().splitlines()
            for n, line in enumerate(text, 1):
                m = re.search(r';\s*@([0-9A-Fa-f]{4})\b', line)
                if m: self.lines[address(f, int(m[1], 16))] = (f'src/asm/{module["name"]}.ASM:{n}', line.split(';')[0].strip())
            spans += [(f, s['start'], s['end']) for s in module['spans'] if s['kind'] == 'code']
        inv = json.loads((ROOT/'src/c/inventory.json').read_text())['functions']
        spans += [(0x878, int(r['address'].split(':')[1], 16),
                   int(r['address'].split(':')[1], 16)+r['instruction_length']) for r in inv]
        for f, a, b in spans:
            used = 0
            for i in cs.disasm(self.mz.image[f*16+a:f*16+b], a):
                key = address(f, i.address); self.ins[key] = i; used += i.size
                reads, writes, must = rw(i)
                source = self.lines.get(key)
                if source is None:
                    physical = [r for r in self.rs if r['frame'] == f and r['offset'] <= i.address < r['end']]
                    r = physical[-1]
                    source = (r['path'].relative_to(ROOT).as_posix()+':'+str(r['line']),
                              '(compiled C)' if r['module']=='C' else '(listing expansion/padding; physical owner label)')
                self.site[key] = dict(instruction=mnemonic(i)+(' '+i.op_str if i.op_str else ''),
                    size=i.size, source=source[0], reads=sorted(reads), writes=sorted(writes),
                    must_write=sorted(must), relocations=[dict(byte=p-(f*16+i.address),frame=f'{self.mz.word(p):04X}')
                        for p in self.mz.sites if f*16+i.address <= p < f*16+i.address+i.size])
            if used != b-a:
                raise ValueError(f'undecoded classified code {f:04X}:{a:04X}..{b:04X}')
        self.library = {}
        targets = {self.direct(a) for a, i in self.ins.items() if i.mnemonic in ('call','lcall')}
        for target in sorted(t for t in targets if t and t.startswith('0000:')):
            todo = [int(target[5:],16)]; seen = set(); reads = set(); writes = set(); returns = set(); external = False
            while todo:
                off = todo.pop()
                if off in seen: continue
                if not 0 <= off < 0x13B8: external = True; continue
                i = next(cs.disasm(self.mz.image[off:off+16],off,count=1),None)
                if i is None: external = True; continue
                seen.add(off); rr, ww, _ = rw(i); reads |= rr; writes |= ww
                if i.mnemonic in ('ret','retf'):
                    returns.add((i.mnemonic, i.operands[0].imm if i.operands else 0)); continue
                if i.mnemonic in ('int','call','lcall','iret'):
                    external = True
                if i.mnemonic.startswith('j') or i.mnemonic.startswith('loop'):
                    if i.operands[0].type == IMM: todo.append(i.operands[0].imm & 65535)
                    else: external = True
                if i.mnemonic not in ('jmp','ljmp','iret','hlt'): todo.append(off+i.size)
            cleanup = {n for _,n in returns}
            self.library[target] = dict(reads=sorted(reads), may_write=sorted(writes),
                returns=sorted([list(v) for v in returns]), cleanup=next(iter(cleanup)) if len(cleanup)==1 else None,
                instruction_count=len(seen), complete=False, external=external,
                note='static linked library-byte diagnostic, not rewritten source; memory/device effects remain external')

    def direct(self, a):
        i = self.ins[a]; ops = i.operands; f = int(a[:4], 16)
        if len(ops) == 2 and all(o.type == IMM for o in ops):
            return address(ops[0].imm & 65535, ops[1].imm & 65535)
        if len(ops) == 1 and ops[0].type == IMM:
            return address(f, ops[0].imm & 65535)

    def word(self, f, o):
        return self.mz.word(f*16+o)

    def table(self, f, a, count, stride=2, tf=None):
        return [address(tf or f, self.word(f, a+stride*k)) for k in range(count)]

    def indirect(self):
        """Source-audited transfer shapes, with bytes/target words read from the build.

        These are hypotheses with explicit invariants, not a generic points-to proof.
        A new site fails closed into dynamic, never disappears from the census.
        """
        descs = {'actor': (0x7720, 8, 74, range(8, 46, 2)),
                 'enemy': (0x7630, 4, 60, range(8, 34, 2)),
                 'item': (0x7970, 11, 20, (4, 6, 8, 10))}
        self.descriptors = {}
        for family, (base, count, stride, fields) in descs.items():
            self.descriptors[family] = {f'{base+stride*k:04X}':
                {f'{field:02X}': address(0x13B, self.word(0x5C09, base+stride*k+field)) for field in fields}
                for k in range(count)}
        def targets(family, field=None):
            rows = self.descriptors[family].values()
            return sorted({v for row in rows for k, v in row.items() if field is None or int(k, 16) == field})
        # Demo headers are discovered from the four pointer vectors, not from L1.
        scripts = set()
        for start in (0x1020, 0x1792, 0x1E40, 0x24DE):
            p = start
            while self.word(0x5C09, p) != 0xFFFF:
                scripts.add(self.word(0x5C09, p)); p += 2
                if p-start > 64: raise ValueError('demo pointer vector lacks bounded sentinel')
        demos = sorted({address(0x13B, self.word(0x5C09, p+6)) for p in scripts})
        for a, i in self.ins.items():
            if i.mnemonic not in ('call', 'lcall', 'jmp', 'ljmp') or self.direct(a): continue
            f, off = (int(x, 16) for x in a.split(':'))
            rec = dict(classification='dynamic', targets=[], unknown=True, invariants=[],
                       origin='unresolved code pointer', flow=[], kind=i.mnemonic)
            if f == 0x13B:
                if off == 0xA15:
                    rec.update(targets=demos, origin='28 motion-script header callback words (+6), four demo vectors',
                        flow=['DGROUP:1020/1792/1E40/24DE -> header +6',
                              'GAME:0B21 load -> 0B24 store ActorOverlayOrScriptCallbacks[slot]',
                              'GAME:0A15 call slot'],
                        invariants=['DS=DGROUP; slots initialized by InitializeDemoScripts; vector/sentinel and indices in range; no later pointer corruption'])
                elif off in (0x1492, 0x236F, 0x2B8C):
                    fam, cell = {0x1492: ('actor', '2A0D'), 0x236F: ('enemy', '2CF3'), 0x2B8C: ('item', '2D83')}[off]
                    values = targets(fam) if fam != 'item' else sorted(set(targets(fam,6)+targets(fam,10)))
                    rec.update(targets=values, origin=f'{fam} descriptor callback words, copied into DGROUP:{cell} parallel array',
                        flow=[f'{fam} descriptor -> initializer/state transition load', f'load/store -> DGROUP:{cell}[BX] -> {a}'],
                        invariants=[f'DS=DGROUP; active {fam} descriptor belongs to the {len(self.descriptors[fam])} built descriptors; valid slot and initialized callback; mode-specific array interpretation'])
                elif off == 0x2DFE:
                    rec.update(targets=self.table(f, 0x2DB3, 3), origin='CS:2DB3 three near words',
                        flow=['WaterSurfaceFrame -> SI; SHL SI,1 at 2DFC -> CS:[SI+2DB3]'],
                        invariants=['WaterSurfaceFrame in 0..2; table unchanged; shared saved-DS stack frame'])
                else:
                    op = i.operands[0]
                    field = op.mem.disp if op.type == MEM else (0x2C if off == 0x14DB else None)
                    fam = ('item' if off in (0x1AEB, 0x2B3A, 0x2C8E) else
                           'actor' if 0x149C <= off < 0x2195 else 'enemy')
                    if field is not None and f'{field:02X}' in next(iter(self.descriptors[fam].values())):
                        rec.update(targets=targets(fam, field), origin=f'{fam} descriptors +{field:02X} near code words',
                            flow=[f'DGROUP {fam} descriptor pointer -> SI -> [SI+{field:02X}]'+
                                  (' -> AX -> ActorUpdateOrScriptCursor store -> JMP AX' if off == 0x14DB else '')],
                            invariants=[f'DS=DGROUP; SI is one of the {len(self.descriptors[fam])} built {fam} descriptors; descriptor data unmodified'])
            elif (f, off) in ((0x664, 0x15E5), (0x664, 0x177D)):
                base = 0x174B if off == 0x15E5 else 0x1919
                rec.update(targets=self.table(f, base, 16), origin=f'CS:{base:04X} sixteen near words',
                    flow=['AL=stream byte; AH=0; BX=AX; SHR BX,3; AND BX,FFFE; ADD BX,table; JMP CS:[BX]'],
                    invariants=['CS table bytes unchanged (no direct table writer); no arbitrary memory corruption'])
                rec['classification'] = 'fully_resolved'
            elif (f, off) in ((0x878, 0x12C6), (0x878, 0x1B1B)):
                base, count = (0x1483, 7) if off == 0x12C6 else (0x1B95, 8)
                rec.update(targets=self.table(f, base, count), origin=f'compiler switch table CS:{base:04X}, {count} words',
                    flow=(['CX=7; BX=1475; compare case keys; BX+=2; matched key -> JMP CS:[BX+0E]']
                          if off == 0x12C6 else ['opcode high nibble -> BX, even bounded index -> JMP CS:[BX+1B95]']),
                    invariants=['compiler switch table unchanged; no arbitrary memory corruption'])
                rec['classification'] = 'fully_resolved'
            elif (f, off) == (0xA32, 0x9B):
                rec.update(classification='external', origin='INT21 AX=3508 returns ES:BX; stored at DGROUP:7B72/7B74',
                    flow=['TIMER:0024 INT21/3508 -> 0026/002A saved vector', 'STI; PUSHF; CALL FAR saved vector; handler must IRET'],
                    invariants=['prior INT08 vector obeys interrupt ABI'])
            elif (f, off) == (0xA32, 0x145):
                rec.update(classification='partially_resolved', targets=['0A32:0099', '0664:12E5', '0664:1939'],
                    origin='timer far-pointer array; public AX:DX callback input; installed slot zero',
                    flow=['InstallTimerInterrupt -> slot zero = ChainSavedTimerInterrupt',
                          'SOUND:1360/1363 -> RegisterTimerCallback (AdvanceMusicFade)',
                          'SOUND:1B1E/1B21 -> RegisterTimerCallback (TickAdlxPlayback)',
                          'TIMER:01CC/01D0 writes AX:DX -> callback slot',
                          'TIMER:025C..0268 copies with undoubled slot indices (offset/segment word mixing)',
                          'TIMER:0143 doubles slot byte offset -> far CALL [SI+7B2E]'],
                    invariants=['valid slot/handle bounds; callback API can accept other code pointers'],
                    unresolved='public callback parameters and mis-strided removal can produce unknown/mixed seg:off targets')
            if rec['targets'] and rec['classification'] == 'dynamic': rec['classification'] = 'under_invariants'
            if rec['classification'] in ('fully_resolved', 'under_invariants'): rec['unknown'] = False
            rec['targets'] = sorted(set(rec['targets']))
            rec['resolution_scope'] = 'complete target-word set under listed invariants' if rec['classification'] in ('fully_resolved','under_invariants') else 'open target set'
            rec['noncode_targets'] = [t for t in rec['targets'] if t not in self.ins]
            # Null descriptor fields are retained, not silently discarded as impossible.
            if rec['noncode_targets']:
                rec['unresolved'] = 'set includes null/noninstruction targets; type-specific reachability not proved'
            self.transfers[a] = rec

    def flow(self):
        for a, i in self.ins.items():
            f = int(a[:4], 16); nxt = address(f, i.address+i.size); m = i.mnemonic
            if m in ('ret', 'retf', 'iret', 'hlt'):
                self.site[a]['return'] = m
                continue
            isbranch = m.startswith('j') or m.startswith('loop')
            if m in ('call', 'lcall') or isbranch:
                ts = [self.direct(a)] if self.direct(a) else self.transfers.get(a, {}).get('targets', [])
                for t in ts:
                    self.edges[a].append((t, 'call' if m in ('call', 'lcall') else 'jump'))
                if a in self.transfers and self.transfers[a]['unknown']:
                    self.edges[a].append(('UNKNOWN', 'call' if m in ('call', 'lcall') else 'jump'))
            if m not in ('jmp', 'ljmp'):
                self.edges[a].append((nxt if nxt in self.ins else 'OUTSIDE:'+nxt, 'next'))
        for entry, r in self.byaddr.items():
            body = set(); todo = [entry]; tails = set(); calls = set(); bad = set()
            while todo:
                a = todo.pop()
                if a in body: continue
                if a not in self.ins: bad.add(a); continue
                body.add(a); self.owners[a].add(entry)
                for t, kind in self.edges[a]:
                    if kind == 'call': calls.add(t); continue
                    if t in self.byaddr and t != entry:
                        tails.add(t)
                    elif t in self.ins: todo.append(t)
                    else: bad.add(t)
            self.bodies[entry] = dict(nodes=body, tails=tails, calls=calls, bad=bad)
        # Edges to local switch arms do not make those arms independent routines.
        self.graph = {a: {t for t in b['calls'] | b['tails'] if t in self.byaddr} for a, b in self.bodies.items()}
        self.callers = defaultdict(set)
        for a, ts in self.graph.items():
            for t in ts: self.callers[t].add(a)
        self.return_kinds = {a: {self.ins[n].mnemonic for n in b['nodes'] if self.ins[n].mnemonic in ('ret', 'retf', 'iret')}
                             for a, b in self.bodies.items()}
        changed = True
        while changed:
            changed = False
            for a, b in self.bodies.items():
                old = set(self.return_kinds[a])
                for t in b['tails']: self.return_kinds[a] |= self.return_kinds.get(t, set())
                changed |= old != self.return_kinds[a]

    def successors(self, entry, a):
        return [t for t, k in self.edges[a] if k != 'call' and t in self.bodies[entry]['nodes']]

    def effective_rw(self, a, summaries):
        rec = self.site[a]; reads = set(rec['reads']); writes = set(rec['writes']); must = set(rec['must_write'])
        if self.ins[a].mnemonic in ('call', 'lcall'):
            ts = [t for t, k in self.edges[a] if k == 'call']
            defs = []
            for t in ts:
                if t in summaries:
                    reads |= summaries[t]['inputs']; writes |= summaries[t]['may_write']; defs.append(summaries[t]['must_define'])
                else:
                    reads |= ATOMS; writes |= ATOMS; defs.append(set())
            if defs: must |= set.intersection(*defs)
            # Returning CALL does not define/kill the caller's SP.
            must.discard('sp'); writes.discard('sp')
        elif self.ins[a].mnemonic == 'int':
            # External service contracts remain unproved in this application-only graph.
            reads |= ATOMS; writes |= ATOMS; must.clear()
        return reads, writes, must

    def interfaces(self):
        summaries = {a: dict(inputs=set(), may_write=set(), must_define=set()) for a in self.byaddr}
        # Least fixed point for may input/write; must-define uses only locally unavoidable writes.
        for _ in range(100):
            changed = False
            for entry, body in self.bodies.items():
                live = {a: set() for a in body['nodes']}; defs = {a: set(ATOMS) for a in body['nodes']}
                defs[entry] = set(); pred = defaultdict(list)
                for a in body['nodes']:
                    for t in self.successors(entry, a): pred[t].append(a)
                work = deque(sorted(body['nodes'], reverse=True)); queued = set(work)
                while work:
                    a = work.popleft(); queued.discard(a)
                    reads, writes, must = self.effective_rw(a, summaries)
                    after = set().union(*(live[t] for t in self.successors(entry, a)))
                    # Tail routine inputs are live on the transfer, plus unknown transfers.
                    for t, k in self.edges[a]:
                        if k != 'call' and t not in body['nodes']:
                            after |= summaries[t]['inputs'] if t in summaries else ATOMS
                    new = reads | (after-must)
                    if new != live[a]:
                        live[a] = new
                        for p in pred[a]:
                            if p not in queued: work.append(p); queued.add(p)
                # Definite definitions on every terminating path (calls may define conditionally).
                pending = deque([entry]); seen = set()
                while pending:
                    a = pending.popleft(); seen.add(a)
                    if a != entry:
                        incoming = [defs[p] | self.effective_rw(p, summaries)[2] for p in pred[a] if p in seen]
                        new = set.intersection(*incoming) if incoming else set()
                        if new == defs[a]: continue
                        defs[a] = new
                    pending.extend(t for t in self.successors(entry, a) if t not in seen or
                                   not defs[t] <= (defs[a] | self.effective_rw(a, summaries)[2]))
                ends = [a for a in body['nodes'] if not self.successors(entry, a)]
                must_exit = set.intersection(*(defs[a] | self.effective_rw(a, summaries)[2] for a in ends)) if ends else set()
                may = set().union(*(self.effective_rw(a, summaries)[1] for a in body['nodes']))
                for t in body['tails']: may |= summaries.get(t, {'may_write': ATOMS})['may_write']
                new = dict(inputs=live[entry], may_write=may, must_define=must_exit)
                if new != summaries[entry]: summaries[entry] = new; changed = True
            if not changed: break
        else: raise ValueError('interface fixed point did not converge')
        self.summaries = summaries
        # Demand from known caller continuations, propagated into return sites. Unknown
        # entry callers do not imply an empty output set: expose a separate ALL bound.
        demands = {a: set() for a in self.byaddr}
        self.live = {}
        for _ in range(100):
            changed = False
            for entry, body in self.bodies.items():
                live = {a: set() for a in body['nodes']}; afters = {}
                work = deque(sorted(body['nodes'], reverse=True)); queued = set(work); pred = defaultdict(list)
                for a in body['nodes']:
                    for t in self.successors(entry, a): pred[t].append(a)
                while work:
                    a = work.popleft(); queued.discard(a)
                    succ = self.successors(entry, a)
                    after = set().union(*(live[t] for t in succ))
                    if self.ins[a].mnemonic in ('ret', 'retf', 'iret'): after |= demands[entry]
                    for t, k in self.edges[a]:
                        if k != 'call' and t not in body['nodes']:
                            after |= summaries[t]['inputs'] | demands[entry] if t in summaries else ATOMS
                    reads, _, must = self.effective_rw(a, summaries)
                    new = reads | (after-must); afters[a] = after
                    if new != live[a]:
                        live[a] = new
                        for p in pred[a]:
                            if p not in queued: work.append(p); queued.add(p)
                self.live[entry] = afters
                for a in body['nodes']:
                    for t, kind in self.edges[a]:
                        if t not in demands: continue
                        need = afters[a] if kind == 'call' else demands[entry]
                        if not need <= demands[t]: demands[t] |= need; changed = True
            if not changed: break
        else: raise ValueError('caller demand fixed point did not converge')
        self.demands = demands

    def value(self, a, op, state):
        ins = self.ins[a]
        if op.type == IMM:
            linear = int(a[:4],16)*16+ins.address
            relocated = any(linear+ins.imm_offset <= p < linear+ins.size for p in self.relocs)
            return frozenset((f'frame:{op.imm & 65535:04X}' if relocated else op.imm & 65535,))
        if op.type == REG:
            name = ins.reg_name(op.reg)
            if name in state['regs']: return state['regs'][name]
            if name.endswith(('l', 'h')) and name[0]+'x' in state['regs']:
                vals = state['regs'][name[0]+'x']
                if all(isinstance(v, int) for v in vals): return frozenset((v >> (8 if name[-1] == 'h' else 0)) & 255 for v in vals)
            return UNKNOWN
        if op.type == MEM:
            # Retain a load's provenance without treating mutable bytes as constants.
            return frozenset(('load@'+a,))
        return UNKNOWN

    def abstract(self, entry, summaries):
        initial = dict(regs={r: frozenset(('in:'+r,)) for r in TRACK}, stack={}, sp=0)
        initial['regs']['cs'] = frozenset(('frame:'+entry[:4],))
        incoming = {entry: initial}; todo = deque([entry]); queued = {entry}; exits = []; unknown_exit = False
        def merge(t, state):
            if t not in incoming:
                incoming[t] = dict(regs=dict(state['regs']), stack=dict(state['stack']), sp=state['sp']); return True
            old = incoming[t]
            regs = {r: union((old['regs'][r], state['regs'][r])) for r in TRACK}
            sp = old['sp'] if old['sp'] == state['sp'] else None
            stack = {k: union((v, state['stack'][k])) for k, v in old['stack'].items() if k in state['stack']} if sp is not None else {}
            new = dict(regs=regs, stack=stack, sp=sp)
            if old != new: incoming[t] = new; return True
            return False
        steps = 0
        while todo:
            steps += 1
            if steps > 100000: raise ValueError('abstract interpreter failed to converge '+entry)
            a = todo.popleft(); queued.discard(a); src = incoming[a]
            state = dict(regs=dict(src['regs']), stack=dict(src['stack']), sp=src['sp'])
            i = self.ins[a]; m = mnemonic(i).split()[-1]; ops = i.operands
            def push(v):
                if state['sp'] is not None:
                    state['sp'] -= 2; state['stack'][state['sp']] = v
            def pop():
                if state['sp'] is None: return UNKNOWN
                v = state['stack'].get(state['sp'], frozenset(('stack:'+str(state['sp']),)))
                state['stack'].pop(state['sp'], None); state['sp'] += 2; return v
            val = self.value(a, ops[1], src) if len(ops) > 1 else UNKNOWN
            old = self.value(a, ops[0], src) if ops else UNKNOWN
            for r in self.site[a]['writes']:
                rr = r[0]+'x' if r in ('al', 'ah', 'bl', 'bh', 'cl', 'ch', 'dl', 'dh') else r
                if rr in state['regs'] and rr != 'sp': state['regs'][rr] = UNKNOWN
            if m == 'mov' and len(ops) == 2 and ops[0].type == REG:
                name = i.reg_name(ops[0].reg)
                if name in state['regs']: state['regs'][name] = val
                elif name in ('al', 'ah', 'bl', 'bh', 'cl', 'ch', 'dl', 'dh'):
                    rr = name[0]+'x'; before = src['regs'][rr]
                    if all(isinstance(v, int) for v in before | val):
                        state['regs'][rr] = union([frozenset(((v & (255 if name[-1] == 'h' else 65280)) |
                            ((w & 255) << (8 if name[-1] == 'h' else 0)),)) for v in before for w in val])
            elif m in ('xor', 'sub') and len(ops) == 2 and ops[0].type == ops[1].type == REG and ops[0].reg == ops[1].reg:
                name = i.reg_name(ops[0].reg)
                if name in state['regs']: state['regs'][name] = frozenset((0,))
            elif m == 'push': push(old)
            elif m == 'pushf': push(frozenset((('flags',tuple((r,src['regs'][r]) for r in FLAGS)),)))
            elif m == 'pushaw':
                for r in ('ax','cx','dx','bx','sp','bp','si','di'): push(src['regs'][r])
            elif m == 'popaw':
                for r in ('di','si','bp','sp','bx','dx','cx','ax'):
                    v = pop()
                    if r != 'sp': state['regs'][r] = v
            elif m == 'pop':
                v = pop()
                if ops[0].type == REG:
                    name = i.reg_name(ops[0].reg)
                    if name in state['regs']: state['regs'][name] = v
            elif m == 'popf':
                saved = pop()
                if len(saved)==1 and isinstance(next(iter(saved)),tuple) and next(iter(saved))[0]=='flags':
                    for r,v in next(iter(saved))[1]: state['regs'][r] = v
            elif m == 'enter':
                push(src['regs']['bp']); state['regs']['bp'] = frozenset(('stack:'+str(state['sp']),)) if state['sp'] is not None else UNKNOWN
                if state['sp'] is not None: state['sp'] -= ops[0].imm
                if len(ops) > 1 and ops[1].imm: state['sp'] = None; state['stack'] = {}
            elif m == 'leave':
                bp = src['regs']['bp']; state['sp'] = int(next(iter(bp)).split(':')[1]) if len(bp) == 1 and str(next(iter(bp))).startswith('stack:') else None
                state['regs']['bp'] = pop()
            elif m == 'mov' and len(ops) == 2 and ops[0].type == REG and i.reg_name(ops[0].reg) == 'sp':
                state['sp'] = None
            if m == 'mov' and len(ops) == 2 and ops[0].type == REG and i.reg_name(ops[0].reg) == 'bp' and ops[1].type == REG and i.reg_name(ops[1].reg) == 'sp':
                state['regs']['bp'] = frozenset(('stack:'+str(state['sp']),)) if state['sp'] is not None else UNKNOWN
            if m == 'mov' and len(ops) == 2 and ops[0].type == REG and i.reg_name(ops[0].reg) == 'sp':
                vals = self.value(a,ops[1],src)
                state['sp'] = int(next(iter(vals)).split(':')[1]) if len(vals)==1 and str(next(iter(vals))).startswith('stack:') else None
            if m in ('add', 'sub') and ops and ops[0].type == REG and i.reg_name(ops[0].reg) == 'sp':
                if state['sp'] is not None and ops[1].type == IMM: state['sp'] += ops[1].imm * (1 if m == 'add' else -1)
                else: state['sp'] = None
            if ops and ops[0].type == REG:
                name = i.reg_name(ops[0].reg)
                if m == 'xchg' and len(ops)==2 and ops[1].type == REG:
                    other = i.reg_name(ops[1].reg)
                    if name in state['regs'] and other in state['regs']:
                        state['regs'][name],state['regs'][other] = src['regs'][other],src['regs'][name]
                elif name in state['regs'] and m in ('inc','dec','add','sub','and','or','shl','shr'):
                    right = frozenset((1,)) if m in ('inc','dec') else val
                    if all(isinstance(v,int) for v in old | right):
                        fn = {'inc':lambda v,w:v+1,'dec':lambda v,w:v-1,'add':lambda v,w:v+w,'sub':lambda v,w:v-w,
                              'and':lambda v,w:v&w,'or':lambda v,w:v|w,'shl':lambda v,w:v<<(w&31),'shr':lambda v,w:v>>(w&31)}[m]
                        state['regs'][name] = union(frozenset((fn(v,w)&65535,)) for v in old for w in right)
            if m in ('lds', 'les'):
                seg = 'ds' if m == 'lds' else 'es'; mem = ops[1].mem
                # A far load is a parameter/provenance token; data word values are initial
                # evidence only and never immutable in this analysis.
                state['regs'][seg] = frozenset(('far@'+a,))
                if ops[0].type == REG: state['regs'][i.reg_name(ops[0].reg)] = frozenset(('offset@'+a,))
            if m in ('call', 'lcall'):
                ts = [t for t, k in self.edges[a] if k == 'call']
                for r in TRACK:
                    if r in ('cs', 'ss', 'sp'): continue
                    vals = []
                    for t in ts:
                        output = summaries.get(t, {}).get('exit', {}).get(r, UNKNOWN)
                        vals.append(union(src['regs'].get(v[3:], UNKNOWN) if isinstance(v, str) and v.startswith('in:') else frozenset((v,)) for v in output))
                    state['regs'][r] = union(vals) if vals else UNKNOWN
                # TASM's same-segment FAR CALL is PUSH CS / CALL NEAR.
                kinds = set().union(*(self.return_kinds.get(t, set()) for t in ts))
                if m == 'call' and kinds == {'retf'}: pop()
                for t in ts:
                    if t in self.library:
                        cleanup = self.library[t]['cleanup']
                        if cleanup is None: state['sp'] = None
                        elif state['sp'] is not None: state['sp'] += cleanup
                if a == '0A32:009B':
                    # Saved handler IRETs, consuming PUSHF in addition to CALL FAR's frame.
                    pop(); unknown_exit = True
                if m == 'lcall' and kinds == {'ret'}:
                    # The caller continuation is not a returning path.
                    unknown_exit = True
                    continue
            if m == 'int':
                for r in TRACK:
                    if r not in ('cs', 'ss', 'sp'): state['regs'][r] = UNKNOWN
            if m in ('cld','std','clc','stc','cli','sti'):
                flag,value = {'cld':('df',0),'std':('df',1),'clc':('cf',0),'stc':('cf',1),'cli':('if',0),'sti':('if',1)}[m]
                state['regs'][flag] = frozenset((value,))
            if m in ('ret', 'retf', 'iret'):
                exits.append(state); continue
            if m == 'hlt': unknown_exit = True; continue
            for t, kind in self.edges[a]:
                if kind == 'call': continue
                if t in self.bodies[entry]['nodes']:
                    if merge(t, state) and t not in queued: todo.append(t); queued.add(t)
                elif t in self.byaddr:
                    tail = summaries.get(t)
                    if tail:
                        regs = {}
                        for r in TRACK:
                            output = tail.get('exit', {}).get(r, UNKNOWN)
                            regs[r] = union(state['regs'].get(v[3:], UNKNOWN) if isinstance(v, str) and v.startswith('in:') else frozenset((v,)) for v in output)
                        delta = tail.get('deltas', [None]); sp = state['sp']
                        exits.append(dict(regs=regs, stack={}, sp=sp+delta[0] if sp is not None and len(delta) == 1 and delta[0] is not None else None))
                    else: unknown_exit = True
                else: unknown_exit = True
        outputs = {r: union(s['regs'][r] for s in exits) if exits else UNKNOWN for r in TRACK}
        # An unresolved transfer can return to its caller with arbitrary state.
        if unknown_exit: outputs = {r: UNKNOWN for r in TRACK}
        return dict(exit=outputs, deltas=sorted({s['sp'] for s in exits}, key=str), unknown_exit=unknown_exit), incoming

    def segments_stack(self):
        summaries = {}
        for _ in range(32):
            new = {}; states = {}
            for a in self.byaddr:
                new[a], states[a] = self.abstract(a, summaries)
            if new == summaries: break
            summaries = new
        else: raise ValueError('segment/stack summaries did not converge')
        self.abstract_summaries = summaries; self.states = states
        # Call-entry segment values from all known calls and tails. Root/seed values
        # remain explicit unknown parameters; interrupt DS is arbitrary on entry.
        contexts = {a: {r: UNKNOWN for r in ('ds', 'es', 'ss')} for a in self.byaddr}
        for _ in range(32):
            gathered = {a: defaultdict(list) for a in self.byaddr}
            for entry, states in self.states.items():
                for a, state in states.items():
                    for t, _ in self.edges[a]:
                        if t not in self.byaddr: continue
                        for r in ('ds', 'es', 'ss'):
                            gathered[t][r].append(self.instantiate(state['regs'][r], contexts[entry]))
            new = {a: {r: union(gathered[a][r]) if gathered[a][r] else UNKNOWN for r in ('ds', 'es', 'ss')} for a in self.byaddr}
            if new == contexts: break
            contexts = new
        self.contexts = contexts

    @staticmethod
    def instantiate(vals, context):
        return union(context.get(v[3:], UNKNOWN) if isinstance(v, str) and v.startswith('in:') else frozenset((v,)) for v in vals)

    def symbol(self, frame, off, indexed=False):
        a = address(frame, off)
        if a in self.symbol_at: return sorted(set(self.symbol_at[a]))
        offsets = self.data_offsets.get(frame, [])
        k = bisect_right(offsets, off)-1
        if k >= 0:
            base = offsets[k]; delta = off-base
            # A nearby label is a location expression, not proof of an object's extent.
            if delta < 256 and not indexed:
                return [n+f'+{delta:X} (nearest label)' for n in sorted(set(self.symbol_at[address(frame, base)]))]
        return []

    def far_load_facts(self):
        """Keep initial pointer evidence separate from proved flowing values.

        In particular a stored VGA pointer is useful evidence, but mutable RAM
        cannot be treated as a constant without a whole-memory alias invariant.
        """
        self.far_loads = {}
        for a,i in self.ins.items():
            if i.mnemonic not in ('lds','les'): continue
            op = i.operands[1]; mem = op.mem
            seg = i.reg_name(mem.segment) if mem.segment else ('ss' if i.reg_name(mem.base)=='bp' else 'ds')
            rec = dict(destination='ds' if i.mnemonic=='lds' else 'es', pointer=i.op_str.split(',',1)[1].strip(),
                       origin='runtime far pointer', complete=False)
            candidates = []
            if not mem.base and not mem.index:
                if seg=='cs': candidates = [(int(a[:4],16),mem.disp&65535)]
                else:
                    source = self.lines.get(a,('',''))[1]
                    tokens = {t.lower() for t in S.IDENT.findall(source)}
                    for q,s in self.symbols.items():
                        if q.split(':')[0]==self.module_at(a) and q.split(':')[1].lower() in tokens and s['offset']==(mem.disp&65535):
                            candidates.append((s['frame'],s['offset']))
            candidates = sorted(set(candidates))
            if len(candidates)==1:
                f,o = candidates[0]; linear = f*16+o
                raw = self.word(f,o+2)
                val = f'frame:{raw:04X}' if linear+2 in self.relocs else f'absolute:{raw:04X}'
                rec.update(origin='initial built data, conditional on unchanged pointer segment word',
                    cell=address(f,o), symbols=self.symbol(f,o), initial_segment=val,
                    initial_offset=f'{self.word(f,o):04X}',
                    invariants=[f'addressing segment identifies {f:04X} cell', 'pointer segment word has not been overwritten or aliased by a wider write'])
            elif seg=='ss': rec['origin']='far pointer from stack parameter/local (caller-supplied or spilled pointer)'
            self.far_loads[a] = rec
            self.site[a]['far_load'] = rec

    def effects(self):
        direct = {a: defaultdict(set) for a in self.byaddr}
        for a, i in self.ins.items():
            m = mnemonic(i).split()[-1]; f = int(a[:4], 16); memories = []
            for n, op in enumerate(i.operands):
                if op.type != MEM or m == 'lea': continue
                mem = op.mem; seg = i.reg_name(mem.segment) if mem.segment else ('ss' if i.reg_name(mem.base) in ('bp', 'sp') else 'ds')
                vals = []; symbolic = []
                for entry in self.owners[a]:
                    state = self.states[entry].get(a)
                    if state:
                        v = state['regs'].get(seg, UNKNOWN)
                        symbolic.append(v); vals.append(self.instantiate(v, self.contexts[entry]))
                if seg == 'cs': vals = symbolic = [frozenset((f'frame:{f:04X}',))]
                values = union(vals) if vals else UNKNOWN
                expr = union(symbolic) if symbolic else UNKNOWN
                frames = {int(v[6:],16) for v in values if isinstance(v,str) and v.startswith('frame:')}
                indexed = bool(mem.base or mem.index); off = mem.disp & 65535
                ac = op.access
                if not ac:
                    # Missing Capstone access annotations must not hide a possible store.
                    ac = CS_AC_READ | CS_AC_WRITE
                # Capstone marks MOVS destination ES correctly; all explicit string
                # operands are included, in addition to the implicit stack records below.
                symbols = sorted({s for v in frames for s in self.symbol(v, off, indexed)})
                source = self.lines.get(a, ('', ''))[1]
                names = self.source_names[self.module_at(a)]
                hints = sorted({names[token.lower()] for token in S.IDENT.findall(source) if token.lower() in names})
                access = ('R' if ac & CS_AC_READ else '')+('W' if ac & CS_AC_WRITE else '')
                frame_names = []
                for v in values:
                    if isinstance(v,str) and v.startswith('frame:'):
                        frame = int(v[6:],16)
                        frame_names.append('DGROUP' if frame == 0x5C09 else next((k for k,z in cgen.FRAMES.items() if z==frame),v))
                    elif isinstance(v,int): frame_names.append('VGA' if v==0xA000 else f'absolute:{v:04X}')
                    else: frame_names.append('unknown' if v=='?' else v)
                desc = dict(operand=n, access=access, segment=seg, segment_values=sorted(frame_names),
                    segment_expressions=display(expr), displacement=f'{off:04X}',
                    base=i.reg_name(mem.base), index=i.reg_name(mem.index), width=op.size,
                    indexed=indexed, symbols=symbols, source_offset_hints=hints,
                    objects=sorted({o['id'] for v in frames for o in self.data_objects
                                    if o['start'] <= v*16+off < o['end']}) if not indexed else [],
                    extent='index/REP extent not bounded' if indexed else 'operand width only')
                conditional = {v[4:]:self.far_loads[v[4:]] for v in values
                    if isinstance(v,str) and v.startswith('far@') and v[4:] in self.far_loads and 'initial_segment' in self.far_loads[v[4:]]}
                if conditional: desc['stored_pointer_evidence_under_invariants'] = sorted(conditional)
                memories.append(desc)
                for entry in self.owners[a]:
                    for action, bit in (('reads', CS_AC_READ), ('writes', CS_AC_WRITE)):
                        if not ac & bit: continue
                        names = symbols or [seg.upper()+':'+f'{off:04X}'+(' indexed' if indexed else '')]
                        direct[entry][action].update(names)
                    if seg != 'ss' and (not all(isinstance(v, int) or isinstance(v,str) and v.startswith('frame:') for v in values) or indexed):
                        direct[entry]['unresolved'].add('alias/range@'+a)
                    for v in values:
                        if v == 0xA000: direct[entry]['devices'].add('VGA aperture/latches')
                        elif not (isinstance(v,int) or isinstance(v,str) and v.startswith('frame:')) and seg != 'ss': direct[entry]['devices'].add('possible VGA via unresolved far/segment alias')
                for name in symbols+hints: self.varsites[name].add(a)
            if m in ('push', 'pop', 'pushf', 'popf', 'pushaw', 'popaw', 'call', 'lcall', 'ret', 'retf', 'iret', 'enter', 'leave', 'int'):
                memories.append(dict(access='RW' if m in ('enter', 'leave', 'iret','int') else 'W' if m.startswith(('push', 'call', 'lcall')) else 'R',
                    segment='ss', segment_values=['caller stack'], segment_expressions=['in:ss'],
                    displacement='SP-relative', width=16 if m in ('pushaw','popaw') else 6 if m in ('iret','int') else 4 if m in ('retf', 'lcall') else 2,
                    indexed=True, symbols=[], source_offset_hints=[], extent='implicit stack operation'))
                for entry in self.owners[a]: direct[entry]['stack'].add('SS:stack')
            self.site[a]['memory'] = memories
            for entry in self.owners[a]:
                if m in ('in', 'out'):
                    op = i.operands[1] if m == 'in' else i.operands[0]
                    state = self.states[entry].get(a)
                    vals = self.value(a, op, state) if state else UNKNOWN
                    direct[entry]['ports'].update(f'{v:04X}' if isinstance(v, int) else 'DX unknown' for v in vals)
                    self.site[a]['ports'] = display(vals)
                if m == 'int':
                    vector = i.operands[0].imm; direct[entry]['interrupts'].add(f'{vector:02X}')
                    state = self.states[entry].get(a); ax = state['regs']['ax'] if state else UNKNOWN
                    direct[entry]['services'].update(f'{vector:02X}/AH={v>>8:02X}' if isinstance(v, int) else f'{vector:02X}/AH unknown' for v in ax)
                    direct[entry]['unresolved'].add('external interrupt effects@'+a)
                for t, kind in self.edges[a]:
                    if kind in ('call', 'jump') and t not in self.ins:
                        direct[entry]['unresolved'].add(('runtime/external@' if t.startswith('0000:') else 'unknown transfer@')+a+'->'+t)
                    if kind == 'call' and self.ins[a].mnemonic == 'lcall' and self.return_kinds.get(t) == {'ret'}:
                        direct[entry]['unresolved'].add('far-call/near-return transfer@'+a)
                if a in self.transfers and self.transfers[a]['classification'] != 'fully_resolved':
                    direct[entry]['unresolved'].add('indirect assumptions@'+a)
                if a == '013B:2BE3': direct[entry]['unresolved'].add('saved-BX return transfer@'+a)
        self.direct_effects = direct
        trans = {a: {k: set(v) for k, v in e.items()} for a, e in direct.items()}
        for _ in range(300):
            changed = False
            for a, ts in self.graph.items():
                for t in ts:
                    for k, v in trans[t].items():
                        before = len(trans[a].get(k, set())); trans[a].setdefault(k, set()).update(v)
                        changed |= len(trans[a][k]) != before
            if not changed: break
        else: raise ValueError('effect closure failed')
        self.transitive = trans

    def module_at(self, a):
        f = int(a[:4], 16)
        return next(k for k, (v, _, _) in S.MODULES.items() if v == f)

    def provenance(self):
        stores = []; addresses = []
        for a, i in self.ins.items():
            source = self.lines.get(a, ('', ''))[1]
            if 'offset ' in source.lower():
                match = re.search(r'\boffset\s+(\w+)', source, re.I)
                if match:
                    q = self.module_at(a)+':'+match[1]
                    if q in self.symbols:
                        rec = self.symbols[q]; target = address(rec['frame'], rec['offset'])
                        addresses.append(dict(site=a, symbol=q, target=target, code=target in self.ins))
            if len(i.operands) >= 2 and i.operands[0].type == MEM and i.operands[0].access & CS_AC_WRITE:
                tokens = []
                for owner in self.owners[a]:
                    if a in self.states[owner]: tokens += display(self.value(a, i.operands[1], self.states[owner][a]))
                hints = sorted({v for mem in self.site[a]['memory'] for v in mem.get('source_offset_hints', [])})
                if any(re.search(r'Callback|UpdateOrScriptCursor|Descriptor|Vector', h) for h in hints) or any(str(v).startswith('load@') for v in tokens):
                    stores.append(dict(site=a, destination=i.op_str.split(',')[0], source_values=sorted(set(tokens), key=str), hints=hints))
        self.pointer_provenance = dict(address_materializations=addresses, pointer_candidate_stores=stores,
                                      descriptor_fields=self.descriptors)
        for a,rec in self.transfers.items():
            inputs = []
            i = self.ins[a]; op = i.operands[0]
            for owner in sorted(self.owners[a]):
                state = self.states[owner].get(a)
                if not state: continue
                regs = [i.reg_name(op.reg)] if op.type == REG else [i.reg_name(op.mem.base),i.reg_name(op.mem.index)] if op.type == MEM else []
                inputs.append(dict(routine=self.rid[owner], registers={r:display(state['regs'].get(r,UNKNOWN)) for r in regs if r}))
            rec['pointer_input_provenance'] = inputs
            fam = next((family for family in self.descriptors if rec['origin'].startswith(family+' descriptor')),None)
            if fam:
                off = self.ins[a].address
                field = i.operands[0].mem.disp if op.type == MEM else 0x2C
                if off in (0x1492,0x236F): fields = None
                elif off == 0x2B8C: fields = {6,10}
                else: fields = {field}
                rec['origin_words'] = [dict(cell=address(0x5C09,int(base,16)+int(k,16)),target=t)
                    for base,row in self.descriptors[fam].items() for k,t in row.items() if fields is None or int(k,16) in fields]
            if a in ('013B:0A15','013B:1492','013B:236F','013B:2B8C','0A32:0145'):
                needle = {'013B:0A15':'ActorOverlayOrScriptCallbacks','013B:1492':'ActorUpdateOrScriptCursor',
                          '013B:236F':'EnemyStateCallbacks','013B:2B8C':'FallingItemCallbacks','0A32:0145':'TimerCallbackOffsetBySlot'}[a]
                rec['candidate_store_sites'] = [s['site'] for s in stores if needle in s['hints']]

    def emit(self):
        routines = {}; callers_unknown = set()
        # All address-taken entries and seeds are open boundaries. A closed-world
        # direct-only entry is also affected by unresolved returns/transfers.
        taken = {x['target'] for x in self.pointer_provenance['address_materializations'] if x['code']}
        for rec in self.transfers.values(): taken.update(rec['targets'])
        for a in self.byaddr:
            if a in taken or not self.callers[a] or self.module_at(a) in ('C', 'TIMER'):
                callers_unknown.add(a)
        def serialize_effect(e):
            return {k: sorted(e.get(k, set())) for k in ('reads', 'writes', 'stack', 'ports', 'interrupts', 'services', 'devices', 'unresolved')}
        for entry, r in self.byaddr.items():
            body = self.bodies[entry]; ab = self.abstract_summaries[entry]; interface = self.summaries[entry]
            preserved = sorted(x for reg in TRACK if ab['exit'][reg] == frozenset(('in:'+reg,)) for x in atoms(reg))
            if ab['deltas'] != [0] and 'sp' in preserved: preserved.remove('sp')
            if ab['exit']['cs'] == frozenset((f'frame:{r["frame"]:04X}',)): preserved.append('cs'); preserved.sort()
            net = interface['may_write']-set(preserved)
            # Global unknown targets can enter any routine, so all-callers completeness
            # is never asserted merely because no pointer constant was found.
            complete = False
            deltas = ab['deltas']; balanced = deltas == [0] and not ab['unknown_exit']
            intervals = []; last = None
            for a in sorted(body['nodes']):
                off = int(a[5:], 16); end = off+self.ins[a].size
                if last and off == last[1]: last[1] = end
                else:
                    last = [off, end]; intervals.append(last)
            blocks = []
            for lo, hi in intervals: blocks.append([address(r['frame'], lo), address(r['frame'], hi)])
            known = sorted(self.demands[entry] & net)
            routines[self.rid[entry]] = dict(address=entry, source=f'{r["path"].relative_to(ROOT).as_posix()}:{r["line"]}',
                physical_interval=[entry, address(r['frame'], r['end'])], reachable_spans=blocks,
                cfg_sites=sorted(body['nodes']), shared_sites=sorted(a for a in body['nodes'] if len(self.owners[a]) > 1),
                calls=sorted(body['calls']), tails=sorted(body['tails']), unresolved_exits=sorted(body['bad']),
                callers=sorted(self.rid[a] for a in self.callers[entry]),
                register_interface=dict(inputs=sorted(interface['inputs']), may_write=sorted(interface['may_write']),
                    preserved_proved=preserved, known_caller_observed_outputs=known, possible_outputs=sorted(net),
                    complete=complete, input_complete=not any('external' in s or 'transfer' in s or 'indirect' in s for s in self.transitive[entry].get('unresolved', [])),
                    known_call_sites_processed=True,
                    incompleteness=['unresolved callback values, malformed return frames or external entry can add callers',
                                    'outputs are conservative may sets, not path-feasibility/minimal semantic results'],
                    output_bound='known continuations only; unknown/dynamic/external callers may observe any possible output',
                    all_callers_known=False, address_taken_or_public_or_seed=entry in callers_unknown,
                    granularity='byte atoms for AX/BX/CX/DX; other 16-bit registers; individual flags'),
                entry_segments={k: display(v) for k, v in self.contexts[entry].items()},
                segment_exit={k: display(ab['exit'][k]) for k in ('ds', 'es', 'ss')},
                effects_direct=serialize_effect(self.direct_effects[entry]), effects=serialize_effect(self.transitive[entry]),
                effects_complete=not bool(self.transitive[entry].get('unresolved')),
                stack=dict(classification='balanced' if balanced else 'unbalanced' if deltas and all(v is not None for v in deltas) and not ab['unknown_exit'] else 'unresolved',
                    delta_before_return=deltas, unknown_exit=ab['unknown_exit'], return_kinds=sorted(self.return_kinds[entry]),
                    note='delta excludes return-address pop; assumes returning callees and no alias into save area; tail entries may consume caller save words'))
        mismatch = []; return_targets = defaultdict(set)
        previous = {}
        for a,i in self.ins.items(): previous[address(int(a[:4],16),i.address+i.size)] = a
        for a,i in self.ins.items():
            if i.mnemonic not in ('call','lcall'): continue
            for t,kind in self.edges[a]:
                if kind!='call' or t not in self.byaddr: continue
                todo=[t]; seen=set()
                while todo:
                    routine = todo.pop()
                    if routine in seen: continue
                    seen.add(routine)
                    for ret in self.bodies[routine]['nodes']:
                        if self.ins[ret].mnemonic not in ('ret','retf','iret'): continue
                        frame = int(t[:4],16) if i.mnemonic=='lcall' and self.ins[ret].mnemonic=='ret' else int(a[:4],16)
                        return_targets[ret].add(address(frame,i.address+i.size))
                    todo.extend(q for q in self.bodies[routine]['tails'] if q in self.byaddr)
        for a, i in self.ins.items():
            self.site[a]['owners'] = sorted(self.rid[o] for o in self.owners[a])
            self.site[a]['edges'] = [[t, k] for t, k in sorted(self.edges[a])]
            if i.mnemonic in ('call', 'lcall'):
                ts = [t for t, k in self.edges[a] if k == 'call']
                live = set().union(*(self.live[o].get(a, set()) for o in self.owners[a]))
                writes = set().union(*(self.summaries.get(t, {'may_write': ATOMS})['may_write'] for t in ts))
                net = set().union(*(set(routines[self.rid[t]]['register_interface']['possible_outputs']) if t in self.rid else ATOMS for t in ts))
                self.site[a]['call_interface'] = dict(live_after=sorted(live),
                    callee_written_live_after=sorted(live & writes), complete=False,
                    callee_changed_live_after=sorted(live & net),
                    note='may-write upper bound, including callee saves/restores; see routine preserved_proved')
                kinds = set().union(*(self.return_kinds.get(t,{v[0] for v in self.library.get(t,{}).get('returns',[])}) for t in ts))
                pred = self.ins.get(previous.get(a))
                paired = pred is not None and pred.mnemonic=='push' and pred.op_str=='cs'
                form = 'far' if i.mnemonic=='lcall' else 'same-segment far via PUSH CS / CALL near' if paired and kinds=={'retf'} else 'near'
                if a=='0A32:009B': form='PUSHF / CALL far / external IRET'
                compatible = kinds==({'retf'} if i.mnemonic=='lcall' or paired else {'ret'})
                self.site[a]['call_frame'] = dict(form=form, target_return_kinds=sorted(kinds),
                    compatible_on_known_return_paths=compatible,
                    convention_complete=compatible and all(t in self.byaddr or t in self.library for t in ts)
                        and all(not self.abstract_summaries.get(t,{}).get('unknown_exit',False) for t in ts),
                    invariant='callee consumes the compatible return frame; stack parameters/save words do not alias it')
                for t in ts:
                    kinds = self.return_kinds.get(t, set())
                    if i.mnemonic == 'lcall' and kinds == {'ret'}:
                        rec = dict(site=a, target=t, kind='far_call_near_return',
                            continuation=address(int(t[:4], 16), i.address+i.size),
                            residual_stack='saved caller CS remains at SS:SP', classification='dynamic',
                            unknown=True, reason='near RET keeps callee CS and pops only return IP')
                        mismatch.append(rec)
                    elif i.mnemonic=='call' and kinds=={'retf'} and not paired:
                        mismatch.append(dict(site=a,target=t,kind='near_call_far_return',classification='dynamic',unknown=True,
                            continuation='UNKNOWN',residual_stack='RETF consumes an extra caller word as CS',reason='no immediately preceding PUSH CS'))
            if a in self.transfers: self.site[a]['indirect'] = self.transfers[a]
            if i.mnemonic in ('ret', 'retf', 'iret'):
                special = a == '013B:2BE3' or a in ('013B:001C','013B:001D','013B:001E','013B:001F')
                self.site[a]['return_transfer'] = dict(classification='dynamic' if special else 'under_invariants',
                    unknown=True, origin='saved BX on full-pool path or caller return IP' if a == '013B:2BE3' else 'SS return frame',
                    invariant='matching call/interrupt frame and balanced save area',
                    known_continuations=sorted(return_targets[a]),
                    targets='call-site continuations; arbitrary for malformed stack; IRET also restores FLAGS')
            if a == '013B:2BE3':
                self.site[a]['return_transfer']['flow'] = ['2B96 PUSH BX', 'full pool -> 2BAA JMP 2BE3 without POP BX', 'RET loads input BX into IP; true near return word remains']
        self.mismatches = mismatch
        scc = [[self.rid[a] for a in g] for g in tarjan(self.graph)]
        variables = {}
        for name, sites in sorted(self.varsites.items()):
            readers = set(); writers = set(); hints = set()
            for a in sites:
                for mem in self.site[a]['memory']:
                    if name not in mem.get('symbols', [])+mem.get('source_offset_hints', []): continue
                    if name in mem.get('source_offset_hints', []) and name not in mem.get('symbols', []): hints.add(a)
                    if 'R' in mem['access']: readers.update(self.site[a]['owners'])
                    if 'W' in mem['access']: writers.update(self.site[a]['owners'])
            variables[name] = dict(readers=sorted(readers), writers=sorted(writers), sites=sorted(sites),
                                   conditional_segment_sites=sorted(hints), complete=False)
        # Hyperedges retain the state responsible for coupling. Connected components
        # alone would merge most of the game via a few shared globals.
        clusters = defaultdict(list)
        for name, v in variables.items():
            if v['writers']: clusters[tuple(v['writers'])].append(name)
        shared = sorted([dict(routines=list(k), state=sorted(v)) for k, v in clusters.items()],
                        key=lambda v: (-len(v['routines']), v['routines'], v['state']))
        counts = dict(routines=len(routines), instructions=len(self.site),
            indirect_sites=len(self.transfers), indirect_classes=dict(sorted(Counter(v['classification'] for v in self.transfers.values()).items())),
            returns=sum(i.mnemonic in ('ret', 'retf', 'iret') for i in self.ins.values()),
            far_near_mismatch_calls=len(mismatch), full_interfaces=sum(v['register_interface']['complete'] for v in routines.values()),
            input_interfaces_without_unresolved_effects=sum(v['register_interface']['input_complete'] for v in routines.values()),
            effects_without_unresolved_ranges=sum(v['effects_complete'] for v in routines.values()),
            stack_classes=dict(sorted(Counter(v['stack']['classification'] for v in routines.values()).items())),
            scc_sizes=sorted((len(g) for g in scc), reverse=True),
            nontrivial_sccs=[len(g) for g in scc if len(g)>1],
            memory_accesses=sum(len(v['memory']) for v in self.site.values()),
            memory_with_unknown_segment=sum(any(x in ('unknown',) or x.startswith(('in:', 'far@', 'load@','offset@','stack:')) for x in m['segment_values']) for v in self.site.values() for m in v['memory']),
            orphan_instructions=sum(not v['owners'] for v in self.site.values()))
        paths = sorted(set([ROOT/'tools/progmodel.py', ROOT/'tools/symtab.py', ROOT/'tools/cgen.py', ROOT/'tools/where.py',
            ROOT/'metadata/asm-map.json', ROOT/'metadata/names.json', ROOT/'metadata/data-layout.json', ROOT/'src/c/inventory.json']+S.sources()))
        receipts = {p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()) for p in paths}
        build = cgen.PLAIN
        receipts.update({p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()) for p in sorted(build.glob('*.LST'))})
        receipts['build/link/plain/UGH.MAP'] = sha256((build/'UGH.MAP').read_bytes())
        components = decomposition(routines,variables,self.rid)
        return dict(schema=1, coordinate_system='unrelocated module frame:offset; end exclusive',
            analysis='static may-analysis with explicit UNKNOWN; no game or emulator execution',
            assumptions=['instruction decode restricted to curated code spans and compiled C instruction lengths',
                         'no arbitrary executable-code mutation or arbitrary RAM corruption; otherwise all targets/effects are unknown',
                         'unresolved transfers remain open and can enter any routine; known graph is a lower bound',
                         'per-variable source offset hints are conditional on the segment invariant, not exact alias proofs'],
            image_sha256=sha256(self.mz.image), inputs=receipts, counts=counts, routines=routines, sites=self.site,
            indirect_sites=self.transfers, abnormal_calls=mismatch, pointer_provenance=self.pointer_provenance,
            runtime_diagnostics=self.library,
            far_loads=self.far_loads,
            variables=variables, shared_write_clusters=shared, scc=scc, scc_complete=False,
            components=components,
            candidates=candidates(routines))


def decomposition(routines, variables, ids):
    """Proposal: an exhaustive partition, with measured cross-component interfaces.

    Membership is reviewed semantic grouping; edges/writer hyperedges are computed.
    Shared state is explicitly retained instead of assigned by majority voting.
    """
    def group(n, r):
        f,o = (int(x,16) for x in r['address'].split(':'))
        if f == 0xA32: return 'timer'
        if f in (0x664,0x878): return 'audio'
        if o in (8,0xC07,0x3D66,0x4F43,0x4F4E,0x4F5E): return 'sequencing'
        if 0x1C <= o <= 0x1F: return 'external_hooks'
        if o == 0x20: return 'far_copy'
        if o < 0x88D: return 'front_end'
        if o < 0xB4F: return 'demo'
        if o == 0xB4F: return 'render_hud'
        if o < 0xC07 or o == 0x4C81: return 'pictures'
        if o == 0xFE8 or 0x44DB <= o < 0x4634 or o >= 0x50C6: return 'input'
        if o < 0x1486: return 'player_physics'
        if o < 0x2196: return 'passenger_stone'
        if o < 0x2363: return 'contacts'
        if o < 0x2B7F: return 'hazards'
        if o < 0x2D1C: return 'falling_items'
        if o < 0x3961 or 0x3C35 <= o < 0x3D4D: return 'water_weather'
        if o < 0x3C35: return 'level_loader'
        if o < 0x3D66 or 0x3F0F <= o < 0x3F55 or 0x4EFF <= o < 0x4F43: return 'numeric'
        if o < 0x4497: return 'render_hud'
        if 0x4CA5 <= o < 0x4E19: return 'ice'
        return 'video_dos'
    owner = {n: group(n,r) for n,r in routines.items()}
    groups = defaultdict(list)
    for n,c in owner.items(): groups[c].append(n)
    result = {}
    for c,members in sorted(groups.items()):
        calls_out = []; calls_in = []; local = []; shared = []
        for n in members:
            r = routines[n]
            for t in sorted(set(r['calls']+r['tails'])):
                if t in ids and owner[ids[t]] != c: calls_out.append([n,ids[t]])
                elif t not in ids: calls_out.append([n,t])
            for caller in r['callers']:
                if owner[caller] != c: calls_in.append([caller,n])
        for name,v in variables.items():
            writers = {owner[n] for n in v['writers']}
            if c not in writers: continue
            if len(writers)==1: local.append(name)
            else: shared.append(name)
        result[c] = dict(routines=sorted(members), count=len(members), calls_in=sorted(calls_in), calls_out=sorted(calls_out),
            written_only_here=sorted(local), shared_written_state=sorted(shared),
            ownership_complete=False, note='source-offset writer candidates; far/indexed aliases can add owners')
    return result


def candidates(routines):
    # Scores are reviewed judgments, not false numeric precision from instruction counts.
    # All dimensions use 1..5, higher is better; evidence follows every score.
    specs = [
        ('far_copy', ['CopyFarBytes'], [5,5,4,4,4,5],
         ['one leaf; four original-C callers; no persistent owned state', '25 exact bytes; straight REP MOVSB and cdecl adaptation',
          'finite count but DF, overlap, offset wrap and parameter/save-area aliases need explicit contract',
          'far cdecl frame, segment registers, register saves and CX loop counter', 'used by event scan, voice allocation and state restoration',
          'ordered buffer-copy/alias/bridge proof reused throughout rendering and audio']),
        ('ice', ['UnpackIceStream', 'UnpackIceToScratch', 'DecodeIceLiteralAndMatchStream', 'ReadIceBitToCarry', 'ReadIceBitsToDx'],
         [5,5,4,5,3,5], ['no shared mutable global outside output/stack', 'exact ASM plus independent codec and five asset round trips',
          'bounded bit grammar and generated streams; arbitrary malformed streams not bounded', 'register bit buffer/DF/CS tables/backward segment machinery',
          'unblocks all maps and pictures, no gameplay architecture ownership', 'first bit-precise buffer/alias/bridge technique']),
        ('coordinate_scale', ['ScaleLevelSpeedToThreeHalves', 'ScaleLevelYToThreeQuarters'], [4,5,5,2,2,4],
         ['two arithmetic leaves share CoordinateScaleScratch with level clearing', 'few exact instructions', 'exhaustive 16-bit domain feasible; scratch write observable unless proved dead', 'few registers/flags removed', 'narrow geometry utility', 'wrap/signed-rounding proof reusable']),
        ('decimal', ['EncodeSixDecimalDigits', 'EncodeFourDecimalDigits', 'EncodeTwoDecimalDigits'], [4,4,4,4,3,4],
         ['digit buffer and divisor state; shared tails must stay grouped', 'exact arithmetic visible; formatting quirks retained', 'finite ranges and buffer differential cases',
          'DIV/register digits/segment offsets', 'HUD and high scores share formatting', 'shared-tail multi-entry contract technique']),
        ('timer_slots', ['RegisterTimerCallback', 'RemoveTimerCallback', 'SetTimerCallbackInterval'], [2,4,2,5,5,5],
         ['ISR and sound callbacks share arrays; public callback API', 'exact stride defect is visible; behaviour must retain it',
          'invalid handles/capacity and mixed far words complicate contract', 'seven arrays/far pointers/CLI/POPF/stack adapters',
          'central scheduling and interrupt ownership', 'state projection and callback equivalence reusable']),
        ('demo', ['InitializeDemoScripts', 'AdvanceDemoScripts'], [2,4,3,5,4,4],
         ['aliases actor arrays and rendering caches', '28 script headers and finite callback set under initialization invariants',
          'finite shipped scripts; malformed loops/slots need assumptions', 'bytecode pointers and register callbacks', 'typed cutscene interpreter', 'interpreter/state projection technique']),
        ('music_clock', ['SwapDwordByteOrder', 'GetElapsedMusicTime', 'DisableMusicSectionLoop'], [3,4,3,3,3,3],
         ['SOUND globals and C record-12 aliases; arithmetic runtime dependency', 'matched original C plus ASM callers',
          'zero rate faults, 32-bit wrap, runtime division and ES output', 'far record loads and helper calls', 'sound state ownership valuable after table/API repair analysis', 'runtime and originally-C ABI techniques']),
    ]
    dimensions = ['low_coupling','behaviour_confidence','verification_tractability','removable_machinery','architectural_value','technique_reuse']
    result = []
    for name, needles, scores, why in specs:
        selected = sorted(n for n in routines if n.split(':')[1] in needles)
        result.append(dict(component=name, routines=selected, total=sum(scores),
            scores={k: dict(score=s, evidence=w) for k, s, w in zip(dimensions,scores,why)},
            callees=sorted({t for n in selected for t in routines[n]['calls']+routines[n]['tails']}),
            ranking_is_judgment=True))
    return sorted(result, key=lambda v: (-v['total'], v['component']))


def generate():
    model = Model(); model.decode(); model.indirect(); model.flow(); model.interfaces()
    model.segments_stack(); model.far_load_facts(); model.effects(); model.provenance()
    return model.emit()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check', action='store_true')
    p.add_argument('query', nargs='?', choices=['routine','site','var','scc','candidates'])
    p.add_argument('name', nargs='?')
    args = p.parse_args()
    try:
        if args.query:
            d = json.loads(OUT.read_text())
            if args.query in ('scc','candidates'): result = d[args.query]
            elif args.query == 'site':
                key = (args.name or '').upper()
                if key not in d['sites']:
                    linear = S.address(args.name or '')
                    hits = [a for a in d['sites'] if int(a[:4],16)*16+int(a[5:],16)==linear]
                    if len(hits)!=1: raise ValueError('site is not a decoded instruction boundary')
                    key = hits[0]
                result = d['sites'][key]
            else:
                table = d['routines' if args.query == 'routine' else 'variables']
                hits = [v for k, v in table.items() if k.lower() == (args.name or '').lower() or k.split(':')[-1].lower() == (args.name or '').lower()]
                if len(hits) != 1: raise ValueError('unknown/ambiguous query; use MODULE:NAME')
                result = hits[0]
            print(json.dumps(result, indent=2, sort_keys=True)); return
        d = generate(); content = json.dumps(d, sort_keys=True, separators=(',', ':'), ensure_ascii=True)+'\n'
        if args.check:
            if not OUT.exists() or OUT.read_text() != content: raise ValueError('metadata/program-model.json stale; run python tools/progmodel.py')
        else: OUT.write_text(content)
        print(json.dumps(d['counts'], sort_keys=True))
        print('program-model: '+('current' if args.check else 'written'))
    except (ValueError, KeyError, FileNotFoundError) as e:
        p.exit(2, 'progmodel: '+str(e)+'\n')


if __name__ == '__main__': main()
