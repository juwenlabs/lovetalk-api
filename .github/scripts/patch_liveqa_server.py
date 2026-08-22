from pathlib import Path
import re

p=Path('server.js')
s=p.read_text(encoding='utf-8')
s=re.sub(r'const SERVER_VERSION = "[^"]+";', 'const SERVER_VERSION = "2026-08-23-potentia-v17-style";', s, count=1)

old='''- 번호 교환 직후·소개팅·앱 매칭·초기 낯선 관계에서 사용자가 이미 반말 관계라고 명시하지 않았다면 존댓말을 기본으로 한다. 상대 이름을 불필요하게 반복하지 않는다.'''
new='''- 번호 교환 직후·소개팅·앱 매칭·초기 낯선 관계에서 사용자가 이미 반말 관계라고 명시하지 않았다면 존댓말을 기본으로 한다. 상대 이름은 첫 메시지에 꼭 필요하지 않으면 생략하고 불필요하게 반복하지 않는다.
- 초기 관계에서 두 사람이 실제로 웃긴 맥락이나 ㅋㅋ·ㅎㅎ를 이미 공유했다는 근거가 없으면 AI가 먼저 ㅋㅋ, ㅎㅎ, ^^, 장난스러운 이모지를 자동으로 붙이지 않는다.'''
assert old in s, 'initial tone anchor missing'
s=s.replace(old,new,1)

old2='''- 참여도는 행동 강도를 정하는 내부 운영값일 뿐 호감 확률이 아니다. 사용자에게 '호감 중간~높음'처럼 준점수 형태로 포장하지 말고, 확인된 참여 행동과 판단 확신도(높음/중간/낮음)를 분리해 설명한다.'''
new2='''- 참여도는 행동 강도를 정하는 내부 운영값일 뿐 호감 확률이 아니다. 사용자에게 '호감 중간~높음'처럼 준점수 형태로 포장하지 말고, 확인된 참여 행동과 판단 확신도를 분리해 설명한다. 판단 확신도가 필요하면 반드시 '높음', '중간', '낮음' 중 하나만 선택하고 '중간~높음' 같은 범위를 만들지 않는다.'''
assert old2 in s, 'confidence anchor missing'
s=s.replace(old2,new2,1)

assert '2026-08-23-potentia-v17-style' in s
assert '실제로 웃긴 맥락' in s
assert "'높음', '중간', '낮음' 중 하나만" in s
p.write_text(s,encoding='utf-8')
print('Potentia v17 style patch applied')
