from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')

assert '2026-08-23-potentia-v20-manual-aligned' in s, 'expected v20 server not found'
s=s.replace('const SERVER_VERSION = "2026-08-23-potentia-v20-manual-aligned";', 'const SERVER_VERSION = "2026-08-23-potentia-v21-source-aligned";', 1)

old='''- 상대가 “그냥 누워 있어요”라고 한 경우 입력에 없는 ‘편하게 쉬고 있다’, ‘피곤하다’, ‘편안한 저녁이다’ 같은 상태를 덧붙이지 않는다. 확인 가능한 사실은 상대가 누워 있다고 답했다는 것뿐이다.'''
new='''- 상대가 “그냥 누워 있어요”라고 한 번 짧게 답한 경우 관심 없음으로 확정하지 않는다. 포텐티아 매뉴얼의 안전한 예시처럼 “오늘 좀 피곤하셨나 봐요. 하루는 어땠어요?”처럼 가벼운 가능성 표현 + 개방형 질문 하나로 한 번 더 자연스럽게 확인할 수 있다. 다만 입력에 없는 시간대(저녁/아침), 구체적 활동(몸 푸는 중, 운동 중), 장소를 사실처럼 만들어내지 않는다.'''
assert old in s, 'lying-down rule anchor missing'
s=s.replace(old,new,1)

old='''- ‘그때 얘기했던 데’, ‘아까 말한 카페’, ‘전에 말한 전시’처럼 입력에 실제로 등장하지 않은 공유 장소·대화 주제·과거 사건을 만들어 답장 명분으로 쓰지 않는다. ‘초반 어색함이 없었다’처럼 입력에 없는 관계 평가도 사실처럼 보태지 않는다.'''
new='''- ‘그때 얘기했던 데’, ‘아까 말한 카페’, ‘전에 말한 전시’처럼 입력에 실제로 등장하지 않은 공유 장소·대화 주제·과거 사건을 만들어 답장 명분으로 쓰지 않는다. ‘초반 어색함이 없었다’처럼 입력에 없는 관계 평가도 사실처럼 보태지 않는다.
- 추천 답장은 사용자가 실제로 말해도 거짓이 되지 않아야 한다. 사용자가 직접 ‘기대된다’, ‘생각 중이다’, ‘가보고 싶다’ 같은 감정·계획을 말하지 않았다면 그런 1인칭 상태를 새로 만들어 답장에 넣지 않는다. 특히 PRO 고백 타이밍에서는 상대가 다음 만남을 먼저 제안했다면, 입력에 없는 장소·활동·감정을 만들기보다 약속을 자연스럽게 확정하거나 지금은 별도 메시지가 필요 없다는 선택을 우선한다.'''
assert old in s, 'pro grounding anchor missing'
s=s.replace(old,new,1)

old='''[[nextAction]]\n지금 연락할지 기다릴지와 바로 할 행동을 1~2문장으로 구체적으로 안내. 초기 비긴급 무응답이라면 약 3일 기준과 한 번의 후속 연락 원칙을 지키고, 2~3시간·하루만으로 관계 종료를 권하지 말 것'''
new='''[[nextAction]]\n지금 연락할지 기다릴지와 바로 할 행동을 1~2문장으로 구체적으로 안내. 답장을 하나 보낸 뒤 초기 비긴급 무응답이 생기면 약 3일 정도 기다린 뒤 한 번만 담백하게 확인하고, 그 확인에도 다시 무응답이면 종료한다. 2~3시간·하루만으로 관계 종료를 권하지 말 것'''
assert old in s, 'quick timing anchor missing'
s=s.replace(old,new,1)

# Detail mode: stop the model from inventing a conversational pretext when the input only establishes participation.
old='''[[reply1]]\n{"label":"가장 자연스러운 답장","text":"답장","reason":"이유"}'''
new='''[[reply1]]\n{"label":"가장 자연스러운 답장","text":"입력된 사실만으로 보낼 수 있는 답장 또는 메시지가 불필요하면 그에 맞는 짧은 문장","reason":"이유"}'''
assert old in s, 'detail reply1 template missing'
s=s.replace(old,new,1)

assert '2026-08-23-potentia-v21-source-aligned' in s
assert '포텐티아 매뉴얼의 안전한 예시처럼' in s
assert '추천 답장은 사용자가 실제로 말해도 거짓이 되지 않아야 한다' in s
p.write_text(s,encoding='utf-8')
print('Potentia v21 source-aligned patch applied')
