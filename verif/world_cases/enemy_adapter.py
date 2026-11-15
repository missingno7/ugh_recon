"""Keep the existing deep counter on the generic stage's frozen source root."""
def source(text):
 old="target=OUT/'baseline';assert (OUT/'levels.json').is_file()"
 assert text.count(old)==1
 return text.replace(old,"target=snapshot();assert (OUT/'levels.json').is_file()")
def install(adapter):adapter.SOURCE_ADAPTERS['enemy_world_cases']=source
