from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')

assert '2026-08-23-potentia-v21-source-aligned' in s, 'expected v21 server not found'
s=s.replace('const SERVER_VERSION = "2026-08-23-potentia-v21-source-aligned";', 'const SERVER_VERSION = "2026-08-23-potentia-v22-timing-enforced";', 1)

# Make the source example operational in quick mode instead of leaving it as a loose general rule.
old='''[[meaning]]\n확인된 사실과 정보 한계를 함께 반영한 핵심 의미 1문장'''
new='''특히 입력에 상대의 “그냥 누워 있어요” 같은 한 번의 짧은 답장이 있다면, reply 후보 중 하나는 포텐티아 매뉴얼 예시처럼 가벼운 가능성 표현 + 개방형 질문 하나를 한 답장 안에 담으세요. 입력에 없는 시간대·구체적 활동·장소는 만들지 마세요.\n[[meaning]]\n확인된 사실과 정보 한계를 함께 반영한 핵심 의미 1문장'''
assert old in s, 'quick meaning anchor missing'
s=s.replace(old,new,1)

old='''[[nextAction]]\n지금 연락할지 기다릴지와 바로 할 행동을 1~2문장으로 구체적으로 안내. 답장을 하나 보낸 뒤 초기 비긴급 무응답이 생기면 약 3일 정도 기다린 뒤 한 번만 담백하게 확인하고, 그 확인에도 다시 무응답이면 종료한다. 2~3시간·하루만으로 관계 종료를 권하지 말 것'''
new='''[[nextAction]]\n지금 연락할지 기다릴지와 바로 할 행동을 1~2문장으로 구체적으로 안내. 초기 대화라면 반드시 조건부로 다음 원칙을 포함하세요: “이 답장 뒤 새로 무응답이 생기면 비긴급 상황에서는 약 3일 정도 기다린 뒤 한 번만 담백하게 확인하고, 그 확인에도 다시 무응답이면 멈춘다.” 2~3시간·하루만으로 관계 종료를 권하지 말 것'''
assert old in s, 'quick nextAction anchor missing'
s=s.replace(old,new,1)

assert '2026-08-23-potentia-v22-timing-enforced' in s
assert '반드시 조건부로 다음 원칙을 포함하세요' in s
p.write_text(s,encoding='utf-8')
print('Potentia v22 quick timing patch applied')
