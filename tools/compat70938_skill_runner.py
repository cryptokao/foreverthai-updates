"""Adapt only pinned recovered fixture build literals to70938; retain9 selected assertions.
Never rewrites runtime source or recovered files. Original legacy runner stays unchanged.
"""
import ast,contextlib,hashlib,io,json,pathlib,sys,types,unittest
import legacy_skill_runner as legacy
ROOT=pathlib.Path(__file__).resolve().parents[1];TRANSFORMS=[]
class BuildFixture(ast.NodeTransformer):
 def visit_Constant(self,node):
  if isinstance(node.value,str) and 'function GetBuildInfo()' in node.value:
   before=node.value;after=before.replace('{"70862","70888"}','{"70938"}').replace('"70862"','"70938"').replace('"70888"','"70938"')
   if before!=after:TRANSFORMS.append(dict(before_sha256=hashlib.sha256(before.encode()).hexdigest(),after_sha256=hashlib.sha256(after.encode()).hexdigest(),kind='Lua fixture build literals only'));return ast.copy_location(ast.Constant(after),node)
  return node
archive=pathlib.Path(sys.argv[1]);legacy.verify_fixture_manifest()
for name in ['test_recipe_panel','test_item_tooltip','test_spellbook_metadata']:
 path=legacy.RECOVERED/'tests'/f'{name}.py';module=types.ModuleType(name);module.__file__=str(path);sys.modules[name]=module;tree=BuildFixture().visit(ast.parse(path.read_text()));ast.fix_missing_locations(tree);exec(compile(tree,str(path),'exec'),module.__dict__)
tree=ast.parse(pathlib.Path(legacy.__file__).read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='check');adapted=BuildFixture().visit(fn);m=ast.Module(body=[adapted],type_ignores=[]);ast.fix_missing_locations(m);namespace=dict(vars(legacy));exec(compile(m,'<70938 selected replay>','exec'),namespace)
output=io.StringIO()
with contextlib.redirect_stdout(output),contextlib.redirect_stderr(output):selected,toc=namespace['check'](archive)
# Explicit gate checks; do not rerun old UI suites to prove unchanged old builds.
from lupa.lua51 import LuaRuntime
l=LuaRuntime();a=l.table();l.execute((ROOT/'src/ForeverThai/Skills/Core.lua').read_text(),'ForeverThai',a);g=l.globals();l.execute('version="1.60.1";interface=16001;locale="enUS";function GetBuildInfo()return version,build,"",interface end;function GetLocale()return locale end')
gates=[]
for b,loc,v,iface,want in [('70862','enUS','1.60.1',16001,True),('70888','enUS','1.60.1',16001,True),('70938','enUS','1.60.1',16001,True),('70939','enUS','1.60.1',16001,False),('70938','enGB','1.60.1',16001,False),('70938','frFR','1.60.1',16001,False),('70938','enUS','1.60.2',16001,False),('70938','enUS','1.60.1',16002,False)]:
 g.build,g.locale,g.version,g.interface=b,loc,v,iface;assert a.skills.Compatible()==want;gates.append(dict(build=b,locale=loc,version=v,interface=iface,supported=want))
report=dict(status='passed',candidate_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),build='70938',selected_cases=selected,toc_modules=toc,full_combined_toc_settings=True,stoneform_real_bitmap=True,devotion_aura_160_armor_30yards=True,perception_action=True,selected_paths=['recipe panel/list recycling','item tooltip actual effects/mismatch/native values','spellbook metadata','action card','completed talent'],old_build_gate_checks_only=gates,fixture_transformations=TRANSFORMS,original_fixtures_unchanged=True,runtime_source_not_transformed=True,new_translations=0,scope='Fresh70938 simulation with exact source ZIP. Nine selected fixture assertions retained, only fixture build literals adapted. Not oldbuild UI reruns, NPC686, font rebuild or live game proof.')
(ROOT/'evidence/compat70938-skills.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'work/compat70938-skills-output.txt').write_text(output.getvalue());print(json.dumps(report,indent=2))
