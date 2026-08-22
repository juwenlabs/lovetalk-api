from pathlib import Path
import re

p=Path('server.js')
s=p.read_text(encoding='utf-8')

# Final QA cleanup: remove internal length marker from user-visible parsing,
# tighten fact-grounding for invented first-person stories, and initial-chat symbols.
assert '2026-08-23-potentia-v18-grounded-complete' in s, 'expected v18 server not found'
s=s.replace('const SERVER_VERSION = "2026-08-23-potentia-v18-grounded-complete";', 'const SERVER_VERSION = "2026-08-23-potentia-v19-final-grounding";', 1)

old='''- 사용자가 제공하지 않은 현재 날씨, 장소, 일정, 직업 사정, 상대의 피곤함·기분·의도·활동을 사실처럼 만들어 답장에 넣지 않는다. 필요한 정보가 없으면 추측을 문장 재료로 채우지 말고 입력된 사실만 사용하거나 낮은 위험의 질문으로 확인한다.'''
new='''- 사용자가 제공하지 않은 현재 날씨, 장소, 일정, 직업 사정, 상대의 피곤함·기분·의도·활동을 사실처럼 만들어 답장에 넣지 않는다. 필요한 정보가 없으면 추측을 문장 재료로 채우지 말고 입력된 사실만 사용하거나 낮은 위험의 질문으로 확인한다.
- 사용자가 말하지 않은 자신의 현재 행동·경험·감정도 지어내지 않는다. 예를 들어 입력에 근거가 없는데 ‘나도 쉬고 있었어’, ‘나도 그곳에 가봤어’, ‘나도 문득 생각났어’처럼 사용자 1인칭 사실을 새로 만들지 않는다. 작은 자기 이야기는 사용자가 제공한 실제 정보에서만 사용한다.'''
assert old in s, 'fact-grounding rule anchor missing'
s=s.replace(old,new,1)

old='''- 초기 관계에서 두 사람이 실제로 웃긴 맥락이나 ㅋㅋ·ㅎㅎ를 이미 공유했다는 근거가 없으면 AI가 먼저 ㅋㅋ, ㅎㅎ, ^^, 장난스러운 이모지를 자동으로 붙이지 않는다.'''
new='''- 초기 관계에서 두 사람이 실제로 웃긴 맥락이나 ㅋㅋ·ㅎㅎ·ㅎ 같은 웃음표현을 이미 공유했다는 근거가 없으면 AI가 먼저 ㅋㅋ, ㅎㅎ, ㅎ, ^^, 장난스러운 이모지를 자동으로 붙이지 않는다.'''
assert old in s, 'initial laughter rule anchor missing'
s=s.replace(old,new,1)

# Keep the token-budget instruction, but do not encode it as a parseable output section.
old='''아래 표식을 정확히 같은 순서로 출력하세요. 코드블록/설명/머리말 금지. reply는 한 줄 유효 JSON 객체.\n[[meaning]]'''
new='''아래 표식을 정확히 같은 순서로 출력하세요. 코드블록/설명/머리말 금지. reply는 한 줄 유효 JSON 객체. 전체 출력은 모든 표식과 reply JSON을 포함해 약 2600자 안에서 반드시 끝내세요.\n[[meaning]]'''
assert old in s, 'detail protocol intro missing'
s=s.replace(old,new,1)

old='''[[nextAction]]\n현재 타이밍 판단 + 다음 연락 시점 + 그때까지 행동 방법 3문장 이내, 약 240자 이내\n[[lengthRule]]\n전체 출력은 모든 표식과 reply JSON을 포함해 약 2600자 안에서 반드시 끝낼 것\n[[done]]'''
new='''[[nextAction]]\n현재 타이밍 판단 + 다음 연락 시점 + 그때까지 행동 방법 3문장 이내, 약 240자 이내\n[[done]]'''
assert old in s, 'lengthRule block missing'
s=s.replace(old,new,1)

# Defensive cleanup: even if an old model response emits the internal marker, never leak it.
old='''    const raw=src.slice(start+marker.length,end).trim(); if(!raw) continue;'''
new='''    const raw=src.slice(start+marker.length,end).replace(/\\[\\[lengthRule\\]\\][\\s\\S]*$/i,"").trim(); if(!raw) continue;'''
assert old in s, 'parser raw anchor missing'
s=s.replace(old,new,1)

assert '[[lengthRule]]' not in s
assert '사용자가 말하지 않은 자신의 현재 행동·경험·감정도 지어내지 않는다' in s
assert '2026-08-23-potentia-v19-final-grounding' in s
p.write_text(s,encoding='utf-8')
print('Potentia v19 final grounding patch applied')
