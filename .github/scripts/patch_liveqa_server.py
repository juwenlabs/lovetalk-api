from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')

assert '2026-08-23-potentia-v19-final-grounding' in s, 'expected v19 server not found'
s=s.replace('const SERVER_VERSION = "2026-08-23-potentia-v19-final-grounding";', 'const SERVER_VERSION = "2026-08-23-potentia-v20-manual-aligned";', 1)

old='''- 상대가 단 한 번 짧게 답한 경우 '대화할 여유가 있다', '열려 있다', '호감이 낮다/높다'처럼 참여나 감정을 판정하지 않는다. 확인 가능한 사실은 짧게 답했다는 것뿐이라고 두고 한 번 더 자연스럽게 흐름을 확인한다.'''
new='''- 상대가 단 한 번 짧게 답한 경우 '대화할 여유가 있다', '열려 있다', '호감이 낮다/높다'처럼 참여나 감정을 판정하지 않는다. 확인 가능한 사실은 짧게 답했다는 것뿐이라고 두고 한 번 더 자연스럽게 흐름을 확인한다.
- 상대가 “그냥 누워 있어요”라고 한 경우 입력에 없는 ‘편하게 쉬고 있다’, ‘피곤하다’, ‘편안한 저녁이다’ 같은 상태를 덧붙이지 않는다. 확인 가능한 사실은 상대가 누워 있다고 답했다는 것뿐이다.'''
assert old in s, 'single-short-answer anchor missing'
s=s.replace(old,new,1)

old="판단 확신도가 필요하면 반드시 '높음', '중간', '낮음' 중 하나만 선택하고 '중간~높음' 같은 범위를 만들지 않는다."
new="판단 확신도가 필요하면 반드시 '높음', '중간', '낮음' 중 하나만 선택한다. ‘중간 정도’, ‘중간~높음’, ‘낮음~중간’처럼 변형하거나 범위로 표현하지 않는다. 확신도를 문장에 쓸 때는 가능하면 ‘판단 확신도: 중간’처럼 정확히 한 단계로 표기한다."
assert old in s, 'confidence anchor missing'
s=s.replace(old,new,1)

old='''- 사용자가 말하지 않은 자신의 현재 행동·경험·감정도 지어내지 않는다. 예를 들어 입력에 근거가 없는데 ‘나도 쉬고 있었어’, ‘나도 그곳에 가봤어’, ‘나도 문득 생각났어’처럼 사용자 1인칭 사실을 새로 만들지 않는다. 작은 자기 이야기는 사용자가 제공한 실제 정보에서만 사용한다.'''
new='''- 사용자가 말하지 않은 자신의 현재 행동·경험·감정도 지어내지 않는다. 예를 들어 입력에 근거가 없는데 ‘나도 쉬고 있었어’, ‘나도 그곳에 가봤어’, ‘나도 문득 생각났어’처럼 사용자 1인칭 사실을 새로 만들지 않는다. 작은 자기 이야기는 사용자가 제공한 실제 정보에서만 사용한다.
- ‘그때 얘기했던 데’, ‘아까 말한 카페’, ‘전에 말한 전시’처럼 입력에 실제로 등장하지 않은 공유 장소·대화 주제·과거 사건을 만들어 답장 명분으로 쓰지 않는다. ‘초반 어색함이 없었다’처럼 입력에 없는 관계 평가도 사실처럼 보태지 않는다.'''
assert old in s, 'invented-context anchor missing'
s=s.replace(old,new,1)

old='''- 초기 비긴급 무응답은 충분히 기다린 뒤 한 번만 담백하게 확인하고, 다시 무응답이면 종료한다. 약속 당일·안전·긴급 일정은 즉시 확인한다.'''
new='''- 초기 비긴급 무응답은 기본적으로 최소 약 3일 정도 기다린 뒤 한 번만 담백하게 확인하고, 그 확인에도 다시 무응답이면 종료한다. 한두 시간, 2~3시간, 하루 정도의 무응답만으로 추가 연락 종료를 권하지 않는다. 다만 약속 당일·안전·긴급 일정은 즉시 확인한다.'''
assert old in s, 'no-reply timing anchor missing'
s=s.replace(old,new,1)

old='''[[nextAction]]\n지금 연락할지 기다릴지와 바로 할 행동을 1~2문장으로 구체적으로 안내'''
new='''[[nextAction]]\n지금 연락할지 기다릴지와 바로 할 행동을 1~2문장으로 구체적으로 안내. 초기 비긴급 무응답이라면 약 3일 기준과 한 번의 후속 연락 원칙을 지키고, 2~3시간·하루만으로 관계 종료를 권하지 말 것'''
assert old in s, 'quick nextAction anchor missing'
s=s.replace(old,new,1)

assert '2026-08-23-potentia-v20-manual-aligned' in s
assert '최소 약 3일 정도' in s
assert '그때 얘기했던 데' in s
p.write_text(s,encoding='utf-8')
print('Potentia v20 manual-aligned patch applied')
