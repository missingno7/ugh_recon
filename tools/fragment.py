"""Derive the relocation proof variant from plain assembly and reloc-layout.json.

Pure derivation: no oracle, compiler output, instruction-byte table, line-number
binding, or address-comment parsing. Generated files belong under build/link/.
"""
import argparse
import json
import re
from pathlib import Path

IDENT = r'[A-Za-z_?$@][\w?$@]*'
INVERSE = {'je':'jne','jne':'je','jz':'jnz','jnz':'jz','ja':'jbe','jbe':'ja',
           'jae':'jb','jb':'jae','jc':'jnc','jnc':'jc','jg':'jle','jle':'jg',
           'jge':'jl','jl':'jge','js':'jns','jns':'js','jo':'jno','jno':'jo',
           'jp':'jnp','jnp':'jp','jpe':'jpo','jpo':'jpe'}


def statement(line):
    """Strip a comment while preserving semicolons inside quoted data strings."""
    quote = None
    for i, c in enumerate(line):
        if c in "\"'":
            if quote == c: quote = None
            elif quote is None: quote = c
        elif c == ';' and quote is None:
            return line[:i].strip()
    return line.strip()


def definitions(lines, owner):
    result = {}
    for position, line in enumerate(lines):
        match = re.match(r'^('+IDENT+r')(?::\s*$|\s+(?:proc|label)\b)', statement(line), re.I)
        if match:
            symbol = match[1].upper()
            if symbol in result: raise ValueError(f'{owner}: duplicate label {match[1]}')
            result[symbol] = position
    return result


def derive(sources, layout):
    """Return generated filename -> source text; inputs are strings/dictionaries."""
    if layout.get('schema') != 1: raise ValueError('unsupported relocation layout schema')
    registry = layout['labels']
    output = {}; physical = []
    for module in layout['modules']:
        owner = module['name']; segment = module['segment']; group = module['group']
        lines = sources[owner].splitlines()
        begins = [i for i,l in enumerate(lines) if re.match(re.escape(segment)+r'\s+segment\b', statement(l), re.I)]
        ends = [i for i,l in enumerate(lines) if re.fullmatch(re.escape(segment)+r'\s+ends', statement(l), re.I)]
        if len(begins) != 1 or len(ends) != 1 or begins[0] >= ends[0]:
            raise ValueError(f'{owner}: expected one plain {segment} segment')
        pre = lines[:begins[0]]; body = lines[begins[0]+1:ends[0]]; tail = lines[ends[0]+1:]
        defs = definitions(body, owner)

        def locate(key, role):
            if key not in registry: raise ValueError(f'{owner}: unknown layout label ID {key}')
            symbol = registry[key]
            if symbol.upper() not in defs:
                raise ValueError(f'{owner}: {role} label {symbol} ({key}) not found in clean source')
            return defs[symbol.upper()]

        cuts = [locate(key, 'cut') for key in module['cut_labels']]
        if cuts != sorted(set(cuts)): raise ValueError(f'{owner}: cut labels are not in source order')
        names = module['piece_names']; order = module['declaration_order']
        if len(cuts) != len(names)+1 or len(order) != len(names) or set(order) != set(names):
            raise ValueError(f'{owner}: invalid piece/declaration ordering')
        if any(statement(l) for l in body[cuts[-1]+1:]):
            raise ValueError(f'{owner}: statements after end cut {registry[module["cut_labels"][-1]]}')
        resident = module['resident_prefix']
        boundaries = cuts if resident else [0]+cuts[1:]

        def piece(position):
            if resident and position < cuts[0]: return segment
            for i, (a,b) in enumerate(zip(boundaries,boundaries[1:])):
                if a <= position < b: return names[i]
            return names[-1]

        rules = {}
        for rule in module['adjustments']:
            at = locate(rule['site'], 'adjustment'); symbol = registry[rule['site']]
            # Locate the next statement, ignoring comments and aliasing labels.
            at += 1
            while at < len(body) and (not statement(body[at]) or re.fullmatch(IDENT+r':', statement(body[at]))): at += 1
            if at >= len(body): raise ValueError(f'{owner}: no instruction after {symbol}')
            if at in rules: raise ValueError(f'{owner}: duplicate adjustment at {symbol}')
            rules[at] = (rule, symbol)
        used = set()

        def render(a,b):
            rendered = []
            for position in range(a,b):
                line = body[position]; code = statement(line); out = line
                if re.match(r'assume\b', code, re.I):
                    out = re.sub(r'\bcs:\s*'+re.escape(segment)+r'\b', 'cs:'+group, line, flags=re.I)
                rule, symbol = rules.get(position, (None,None))
                control = re.fullmatch(r'(j\w+|loop\w*|call)\s+(?:(short|near\s+ptr|far\s+ptr)\s+)?('+IDENT+r')', code, re.I)
                if rule and rule['form'] == 'alignment_nop':
                    if code.lower() != 'even': raise ValueError(f'{owner}: expected EVEN after {symbol}')
                    out = '    nop ; derived group-relative alignment'; used.add(position)
                elif control and control[3].upper() in defs and piece(position) != piece(defs[control[3].upper()]):
                    op, qual, target = control.groups(); op = op.lower(); qual = (qual or '').lower()
                    form = rule['form'] if rule else None
                    if op == 'call':
                        if qual == 'far ptr':
                            out = '    push cs\n    call near ptr '+target
                            if defs[target.upper()] > position: out += '\n    nop'
                        else: out = '    call near ptr '+target
                    elif op == 'jmp':
                        if qual == 'short' or form == 'short_jump': out = '    jmp short '+target+'+1'
                        elif qual == 'near ptr' or form == 'near_jump': out = '    jmp near ptr '+target
                        else: raise ValueError(f'{owner}: missing JMP form at {code}')
                    elif op.startswith('loop') or op == 'jcxz': out = '    '+op+' '+target+'+1'
                    elif op in INVERSE:
                        if qual == 'short' or form in ('conditional_short','conditional_reserved'):
                            out = '    '+op+' short '+target+'+1'
                            if form == 'conditional_reserved': out += '\n    nop\n    nop\n    nop'
                        elif form == 'conditional_long':
                            skip = '__proof_'+rule['site']
                            out = '    '+INVERSE[op]+' short '+skip+'\n    jmp near ptr '+target+'\n'+skip+':'
                        else: raise ValueError(f'{owner}: missing conditional form at {code}')
                    else: raise ValueError(f'{owner}: unsupported cross-piece transfer {code}')
                    if rule: used.add(position)
                elif rule:
                    raise ValueError(f'{owner}: adjustment after {symbol} no longer matches {code}')
                # Native local offsets require the common frame. EQU aliases stay intact.
                def group_offset(match):
                    target = match[1]
                    return 'offset '+group+':'+target if target.upper() in defs else match[0]
                if 'offset' in statement(out).lower():
                    code_part, sep, comment = out.partition(';')
                    out = re.sub(r'\boffset\s+('+IDENT+r')', group_offset, code_part, flags=re.I)+(sep+comment if sep else '')
                rendered.append(out)
            return rendered

        chunks = {name:render(a,b) for name,a,b in zip(names,boundaries,boundaries[1:])}
        prefix = render(0,cuts[0]) if resident else []
        if used != set(rules): raise ValueError(f'{owner}: unused adjustments: {[rules[p][1] for p in set(rules)-used]}')
        # Known external selectors make the generated stream independent of forward-EXTRN batching.
        trailing = []
        for line in tail:
            code = statement(line)
            if re.match(r'extrn\b', code, re.I): pre.append(line)
            elif code.lower() == 'end' or not code: trailing.append(line if not code else '')
            else: raise ValueError(f'{owner}: unsupported statement after segment: {code}')
        declarations = []; members = ([segment] if resident else [])+names
        align = lambda n: 'word' if n == segment else 'byte'
        if resident: declarations += [f"{segment} segment word public 'CODE'", segment+' ends']
        for name in order: declarations += [f"{name} segment {align(name)} public 'CODE'",name+' ends']
        declarations.append(group+' group '+','.join(members))
        generated = ['; GENERATED by tools/fragment.py. Edit the clean source and layout, never this file.']+pre+declarations
        if resident: generated += [f"{segment} segment word public 'CODE'",'assume cs:'+group]+prefix+[segment+' ends']
        for name in order:
            generated += [f"{name} segment {align(name)} public 'CODE'",'assume cs:'+group]+chunks[name]+[name+' ends']
        generated += trailing+['end']
        output[owner+'.ASM'] = '\n'.join(generated)+'\n'
        physical += [(name,align(name)) for name in members]
    output['TIMER.ASM'] = sources['TIMER']
    # DGROUP's forward selector declarations are also a proof-only emission
    # arrangement. Keep normal declarations at the top of the maintained data.
    for owner, keys in layout['deferred_data_externals'].items():
        lines=sources[owner].splitlines(); deferred=[]
        for key in keys:
            symbol=registry[key]
            matches=[i for i,line in enumerate(lines) if re.fullmatch(
                r'extrn\s+'+re.escape(symbol)+r'\s*:\s*far',statement(line),re.I)]
            if len(matches)!=1:raise ValueError(f'{owner}: external label {symbol} ({key}) not found exactly once')
            deferred.append(lines.pop(matches[0]))
        ends=[i for i,line in enumerate(lines) if statement(line).lower()=='end']
        if len(ends)!=1:raise ValueError(f'{owner}: expected one END')
        at=ends[0];lines[at:at]=deferred
        output[owner+'.ASM']='\n'.join(lines)+'\n'
    physical += [(p['segment'],p['alignment']) for p in layout['layout_tail']]
    layout_source = ['; GENERATED empty physical-order declarations. Do not edit.','.286']
    for name,alignment in physical:
        layout_source += [f"{name} segment {alignment} public 'CODE'",name+' ends']
    output['LAYOUT.ASM'] = '\n'.join(layout_source+['end'])+'\n'
    return output


def write_variant(asm_directory, layout_path, destination):
    destination=Path(destination)
    destination.resolve().relative_to((Path(__file__).resolve().parents[1]/'build/link').resolve())
    sources = {name:(Path(asm_directory)/(name+'.ASM')).read_text() for name in ('GAME','SOUND','TIMER')}
    layout = json.loads(Path(layout_path).read_text())
    for name in layout['deferred_data_externals']:
        sources[name]=(Path(asm_directory).parent/'data'/(name+'.ASM')).read_text()
    output = derive(sources,layout)
    destination.mkdir(parents=True,exist_ok=True)
    for name,text in output.items():
        (destination/name).write_bytes(text.replace('\r\n','\n').replace('\n','\r\n').encode('ascii'))
    return layout


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources',type=Path,default=root/'src/asm')
    parser.add_argument('--layout',type=Path,default=root/'metadata/reloc-layout.json')
    parser.add_argument('--output',type=Path,default=root/'build/link/proof')
    args = parser.parse_args()
    try:
        args.output.resolve().relative_to((root/'build/link').resolve())
        write_variant(args.sources,args.layout,args.output)
    except ValueError as error: parser.exit(2,str(error)+'\n')
