from pathlib import Path

p = Path('server.js')
s = p.read_text(encoding='utf-8')
old_ver = 'const SERVER_VERSION = "2026-08-23-potentia-v52-grounded-preference-starter";'
new_ver = 'const SERVER_VERSION = "2026-08-23-potentia-v53-single-question-preference-starter";'
assert old_ver in s, 'v52 base version missing'
s = s.replace(old_ver, new_ver, 1)

old = '{label:"조금 더 가볍게",text:`${when} 시간 괜찮으세요? ${preference} 좋아한다고 하신 얘기도 만나서 이어가볼까요?`,reason:"없는 장소나 공통 취향을 만들지 않고 확인된 취향을 만남 제안의 맥락으로 씁니다."}'
new = '{label:"조금 더 가볍게",text:`${when} 괜찮으시면 ${preference} 좋아한다고 하신 얘기도 만나서 이어가볼까요?`,reason:"없는 장소나 공통 취향을 만들지 않고 확인된 취향을 만남 제안의 맥락으로 씁니다."}'
assert old in s, 'v52 starter reply template missing'
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')
