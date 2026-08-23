from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')
assert '2026-08-23-potentia-v35-realuser-consistency' in s, 'expected v35 server not found'
s=s.replace('const SERVER_VERSION = "2026-08-23-potentia-v35-realuser-consistency";', 'const SERVER_VERSION = "2026-08-23-potentia-v36-apology-detection";', 1)

old=r'''  const receivedApology=relation.includes("연애") && /(?:상대|애인)[^.\n]{0,80}(?:미안|사과)/.test(compact) && /(?:감정[^.\n]{0,30}(?:가라앉|정리)|이제[^.\n]{0,30}가라앉)/.test(compact);'''
new=r'''  const receivedApology=relation.includes("연애") && /(?:상대|애인)[^\n]{0,160}(?:미안|사과)/.test(compact) && /(?:감정[^\n]{0,50}(?:가라앉|정리)|이제[^\n]{0,50}가라앉)/.test(compact);'''
assert old in s, 'received apology detector anchor missing'
s=s.replace(old,new,1)

assert '2026-08-23-potentia-v36-apology-detection' in s
assert '[^\\n]{0,160}(?:미안|사과)' in s
p.write_text(s,encoding='utf-8')
print('Potentia v36 apology detection patch applied')
