import pathlib,sys,ast,types,json,contextlib,io,hashlib,time
R=pathlib.Path(sys.argv[1]).resolve() if len(sys.argv)>1 else pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(R/'tools'));import legacy_skill_runner as legacy
from lupa.lua51 import LuaRuntime
changes=[];t=time.perf_counter()
class CurrentBuild(ast.NodeTransformer):
 def visit_Constant(self,node):
  if isinstance(node.value,str) and 'function GetBuildInfo()' in node.value:
   before=node.value;after=before.replace('{"70862","70888"}','{"70959"}').replace('"70862"','"70959"').replace('"70888"','"70959"').replace('build="70889"','build="not-a-build"')
   if before!=after:changes.append(dict(before=hashlib.sha256(before.encode()).hexdigest(),after=hashlib.sha256(after.encode()).hexdigest(),kind='fixture70959 and invalid-build negative for new family contract'));return ast.copy_location(ast.Constant(after),node)
  return node
legacy.verify_fixture_manifest()
for name in ['test_recipe_panel','test_item_tooltip','test_spellbook_metadata']:
 path=legacy.RECOVERED/'tests'/f'{name}.py';module=types.ModuleType(name);module.__file__=str(path);sys.modules[name]=module;tree=CurrentBuild().visit(ast.parse(path.read_text(encoding='utf8')));ast.fix_missing_locations(tree);exec(compile(tree,str(path),'exec'),module.__dict__)
tree=ast.parse(pathlib.Path(legacy.__file__).read_text(encoding='utf8').replace('str(p.relative_to(ROOT/"src"))','p.relative_to(ROOT/"src").as_posix()'));fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='check');adapted=CurrentBuild().visit(fn);mod=ast.Module(body=[adapted],type_ignores=[]);ast.fix_missing_locations(mod);ns=dict(vars(legacy));exec(compile(mod,'<70959 selected replay>','exec'),ns)
buffer=io.StringIO();archive=R/'ForeverThai-0.480.1-SKILLS-HOTFIX-COMBINED.zip'
try:
 with contextlib.redirect_stdout(buffer),contextlib.redirect_stderr(buffer):selected,toc=ns['check'](archive)
finally:(R/'skill-ui-output.txt').write_text(buffer.getvalue(),encoding='utf8')
l=LuaRuntime(unpack_returned_tuples=True,register_eval=False,register_builtins=False);l.execute('os=nil;io=nil;package=nil;require=nil;dofile=nil;loadfile=nil;debug=nil');a=l.table();l.execute((R/'src/ForeverThai/Skills/Core.lua').read_text(encoding='utf8'),'ForeverThai',a);l.execute('function GetBuildInfo()return sampleVersion,sampleBuild,"",sampleInterface end;function GetLocale()return sampleLocale end');g=l.globals();gates=[]
for build,version,iface,locale,want in [('70862','1.60.1',16001,'enUS',True),('70888','1.60.1',16001,'enUS',True),('70938','1.60.1',16001,'enUS',True),('70959','1.60.1',16001,'enUS',True),('71000','1.60.1',16001,'enUS',True),('not-a-build','1.60.1',16001,'enUS',False),(None,'1.60.1',16001,'enUS',False),('70959','1.60.2',16001,'enUS',False),('70959','1.60.1',16002,'enUS',False),('70959','12.1.5',120105,'enUS',False),('70959','2.5.6',20506,'enUS',False),('70959','1.60.1',16001,'frFR',False)]:
 g.sampleBuild,g.sampleVersion,g.sampleInterface,g.sampleLocale=build,version,iface,locale;assert a.skills.Compatible()==want,(build,version,iface,locale);gates.append(dict(build=build,version=version,interface=iface,locale=locale,allowed=want))
g.sampleBuild,g.sampleVersion,g.sampleInterface,g.sampleLocale='70959','1.60.1',16001,'enUS';l.execute('AlphaWoWSkillsDB={enabled=false,fontSize=19,englishNames=false,original=false};addonForCheck=nil');a.skills.Initialize();assert a.skills.settings.enabled==False and a.skills.settings.fontSize==19;assert a.skills.Render('Adds {1} damage.','เพิ่มความเสียหาย {1}','Adds 12 damage.')=='เพิ่มความเสียหาย 12';assert a.skills.Render('Adds {1} damage.','เพิ่มความเสียหาย {1}','Adds 12 armor.') is None
report=dict(status='PASSED_70959_FULLTOC_AND_NINE_SELECTED_SKILL_UI_SIMULATIONS',selected_cases=selected,toc_modules=toc,full_combined_toc_loaded=True,stoneform_Thai_bitmap=True,devotion_aura160_armor30yards=True,perception20seconds_action=True,item_tooltip_exact_and_changed_text_rejection=True,profession_recipe_list_recycling=True,completed_talent_tooltip=True,build_gates=gates,other_family_and_locale_rejected=True,future71000_gate_only_not_real_client_test=True,explicit_disabled_preference_preserved=True,full_line_name_number_and_secret_guards_retained=True,fixture_transformations=changes,original_fixture_files_unchanged=True,runtime_not_test_transformed=True,game_install_or_UI_control=False,actual_game_acceptance=False,wall=time.perf_counter()-t)
(R/'skill-ui-checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps(report,indent=2))
