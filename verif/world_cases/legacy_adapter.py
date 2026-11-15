"""Port historical compiler-flag mutation operators to registry declarations.

Only the old shared-hostbuild flag-selector edit is translated. Source mutations,
case data, expected failure checks, compiler flags and comparisons stay intact.
The generated copy's own registry entry receives the exact requested -D flag.
"""
import ast,importlib.util,json,re,sys
from pathlib import Path

SOURCE_ADAPTERS={}

FLAG=re.compile(r"['\"](-D[A-Za-z_]\w*(?:=[^'\"]+)?)['\"]")
def selector(text):return isinstance(text,str) and 'return ' in text and '-DUGH_NATIVE_' in text

def supported(text):
 assert selector(text),text
 return True

def flag_text(path,before,after):
 path=Path(path);root=path.parent.parent;old=FLAG.findall(before);new=FLAG.findall(after);added=[f for f in new if f not in old];assert added,(before,after)
 rows=[(p,json.loads(p.read_text())) for p in (root/'metadata/worlds').glob('*.json')]
 matches=[(p,r) for p,r in rows if '-D'+r['flag'] in old];assert len(matches)==1,(before,'unknown registry selector')
 p,row=matches[0];row['compile_flags']+=added;p.write_text(json.dumps(row,indent=2)+'\n')
 return path.read_text()

class Port(ast.NodeTransformer):
 def __init__(self):self.values={};self.changed=0
 def constant(self,node):
  if isinstance(node,ast.Constant):return node.value
  if isinstance(node,ast.Name):return self.values.get(node.id)
 def visit_Assign(self,node):
  node.value=self.visit(node.value)
  for target in node.targets:
   if isinstance(target,ast.Name):self.values[target.id]=self.constant(node.value)
  return node
 def visit_Assert(self,node):
  test=node.test
  if isinstance(test,ast.Compare) and isinstance(test.left,ast.Call) and isinstance(test.left.func,ast.Attribute) and test.left.func.attr=='count' and test.left.args and selector(self.constant(test.left.args[0])):
   self.changed+=1;return ast.copy_location(ast.Expr(ast.Call(ast.Name('_world_flag_supported',ast.Load()),[test.left.args[0]],[])),node)
  return self.generic_visit(node)
 def visit_Call(self,node):
  if isinstance(node.func,ast.Attribute) and node.func.attr=='replace' and len(node.args)>=2 and selector(self.constant(node.args[0])):
   # p is the existing historical writer variable in these bounded adapters.
   self.changed+=1;return ast.copy_location(ast.Call(ast.Name('_world_flag_text',ast.Load()),[ast.Name('p',ast.Load()),node.args[0],node.args[1]],[]),node)
  return self.generic_visit(node)

def module(name,path):
 path=Path(path);text=path.read_text(encoding='utf-8-sig')
 if name in SOURCE_ADAPTERS:text=SOURCE_ADAPTERS[name](text)
 tree=ast.parse(text);rewrite=Port();tree=rewrite.visit(tree);ast.fix_missing_locations(tree)
 spec=importlib.util.spec_from_file_location(name,path);mod=sys.modules.get(name) or importlib.util.module_from_spec(spec);mod._world_flag_text=flag_text;mod._world_flag_supported=supported;sys.modules[name]=mod;exec(compile(tree,str(path),'exec'),mod.__dict__)
 mod._registry_mutation_ports=rewrite.changed;return mod
