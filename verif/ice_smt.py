"""Small SMT-LIB obligations using the supervisor-installed Python Z3.

These are explicit arithmetic/array models, not automatic C verification.
The compiled-C exhaustive harness checks the linkage to the actual helpers.
"""
import hashlib,json,re,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/workers/pilot-ice-2'

def solver():
    OUT.mkdir(parents=True,exist_ok=True)
    info=json.loads((ROOT/'metadata/verif-tools.json').read_text())['z3']
    sys.path.insert(0,re.search(r'[A-Za-z]:[/\\]\S+',info['install'])[0])
    import z3
    if z3.get_version_string()!=info['version']:raise RuntimeError('Z3 version differs from manifest')
    return z3,dict(info,actual_version=z3.get_version_string(),
                   manifest_sha256=hashlib.sha256((ROOT/'metadata/verif-tools.json').read_bytes()).hexdigest())

OBLIGATIONS={
'cursor_wrap':r'''
(declare-const index (_ BitVec 64))
(assert (bvule index (_ bv65535 64)))
(define-fun l1 () (_ BitVec 16) (bvsub ((_ extract 15 0) index) (_ bv1 16)))
(define-fun l2 () (_ BitVec 64) (bvand (bvadd index (_ bv65535 64)) (_ bv65535 64)))
(assert (not (= ((_ zero_extend 48) l1) l2)))
''',
'refill':r'''
(declare-const pending (_ BitVec 8))
(declare-const byte (_ BitVec 8))
(define-fun carry () (_ BitVec 8) (bvlshr pending #x07))
(define-fun shifted () (_ BitVec 8) (bvmul pending #x02))
(define-fun old_pending () (_ BitVec 8) (ite (= shifted #x00) (bvadd (bvmul byte #x02) carry) shifted))
(define-fun new_pending () (_ BitVec 8) (ite (= (bvshl pending #x01) #x00) (bvor (bvshl byte #x01) carry) (bvshl pending #x01)))
(define-fun old_bit () (_ BitVec 8) (ite (= shifted #x00) (bvlshr byte #x07) carry))
(define-fun new_bit () (_ BitVec 8) (ite (= (bvshl pending #x01) #x00) (bvlshr byte #x07) carry))
(assert (or (not (= old_pending new_pending)) (not (= old_bit new_bit))))
''',
'copy_step':r'''
(declare-const memory (Array (_ BitVec 16) (_ BitVec 8)))
(declare-const cursor (_ BitVec 16))
(declare-const from (_ BitVec 16))
; Both loops read before writing, including aliases. This is the inductive
; step for any number of backward copies; matching initial indices and counts
; is a separate obligation below.
(define-fun old_memory () (Array (_ BitVec 16) (_ BitVec 8)) (store memory cursor (select memory from)))
(define-fun new_memory () (Array (_ BitVec 16) (_ BitVec 8)) (store memory cursor (select memory from)))
(define-fun old_cursor () (_ BitVec 16) (bvsub cursor #x0001))
(define-fun new_cursor () (_ BitVec 16) (bvand (bvadd cursor #xffff) #xffff))
(assert (or (not (= old_memory new_memory)) (not (= old_cursor new_cursor))))
''',
'match_start':r'''
(declare-const cursor (_ BitVec 16))
(declare-const bx (_ BitVec 16))
(declare-const code (_ BitVec 16))
(declare-const kind (_ BitVec 2))
(assert (bvule bx (_ bv1031 16)))
; kind: zero=length2, one=wide8, two=short5, three=wide12.
(assert (or (and (= kind #b00) (= bx #x0000) (bvule code #x01ff))
            (and (= kind #b01) (bvugt bx #x0000) (bvule code #x00ff))
            (and (= kind #b10) (bvugt bx #x0000) (bvule code #x001f))
            (and (= kind #b11) (bvugt bx #x0000) (bvule code #x0fff))))
(define-fun bias () (_ BitVec 16) (ite (= kind #b00) #xffff (ite (= kind #b01) #x001f (ite (= kind #b10) #xffff #x011f))))
(define-fun raw () (_ BitVec 16) (bvadd code bias))
(define-fun dx () (_ BitVec 16) (ite (and (not (= bx #x0000)) (bvslt raw #x0000)) (bvsub raw bx) raw))
(define-fun length () (_ BitVec 16) (bvadd bx #x0002))
(define-fun distance () (_ BitVec 16) (ite (= kind #b00) (bvadd code #x0001) (ite (= kind #b01) (bvadd length (bvadd #x001f code)) (ite (= kind #b10) (ite (= code #x0000) #x0001 (bvsub (bvadd length code) #x0001)) (bvadd length (bvadd #x011f code))))))
(assert (not (= (bvadd cursor (bvadd length dx)) (bvadd cursor distance))))
'''
}

def main():
    z,info=solver();rows=[]
    for name,body in OBLIGATIONS.items():
        script='(set-option :timeout 30000)\n'+body+'\n(check-sat)\n'
        (OUT/f'{name}.smt2').write_text(script)
        query=z.Solver();query.set(timeout=30000);query.from_string(body)
        start=time.perf_counter();result=str(query.check())
        elapsed=time.perf_counter()-start
        rows.append(dict(property=name,result=result,seconds=elapsed))
        if result!='unsat':raise AssertionError(rows[-1])
    result=dict(tool=info,properties=rows,scope='all inputs of the explicit SMT models; C correspondence requires review plus ice_primitives.c')
    (OUT/'smt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
