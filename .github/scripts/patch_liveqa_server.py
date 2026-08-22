from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')

assert '2026-08-23-potentia-v23-tone-context' in s, 'expected v23 server not found'
s=s.replace('const SERVER_VERSION = "2026-08-23-potentia-v23-tone-context";', 'const SERVER_VERSION = "2026-08-23-potentia-v24-source-case";', 1)

old='''- 상대가 “그냥 누워 있어요”라고 한 번 짧게 답한 경우 관심 없음으로 확정하지 않는다. 포텐티아 매뉴얼의 안전한 예시처럼 “오늘 좀 피곤하셨나 봐요. 하루는 어땠어요?”처럼 가벼운 가능성 표현 + 개방형 질문 하나로 한 번 더 자연스럽게 확인할 수 있다. 다만 입력에 없는 시간대(저녁/아침), 구체적 활동(몸 푸는 중, 운동 중), 장소를 사실처럼 만들어내지 않는다.'''
new='''- 상대가 “그냥 누워 있어요”라고 한 번 짧게 답한 경우 관심 없음으로 확정하지 않는다. 초기 존댓말 관계라면 추천 후보는 다음 안전한 형태에서 벗어나지 않는다: “오늘 좀 피곤하셨나 봐요. 하루는 어땠어요?”, “그렇군요. 오늘은 어떻게 보내셨어요?”, “누워 계시는군요. 오늘 하루는 어떠셨어요?” 이 케이스에서 “그렇구나”, “그래,”, “무슨 하다가 쉬는 거예요?”, “좋은 시간이네요”, 입력에 없는 저녁/아침·운동·미래 약속을 새로 만들지 않는다.'''
assert old in s, 'source case system rule missing'
s=s.replace(old,new,1)

old='''특히 입력에 상대의 “그냥 누워 있어요” 같은 한 번의 짧은 답장이 있다면, reply 후보 중 하나는 포텐티아 매뉴얼 예시처럼 가벼운 가능성 표현 + 개방형 질문 하나를 한 답장 안에 담으세요. 초기 관계라면 모든 reply 후보는 처음부터 끝까지 존댓말을 유지하세요. 입력에 없는 시간대·구체적 활동·장소·미래 약속은 만들지 마세요.'''
new='''특히 입력에 상대의 “그냥 누워 있어요”라는 한 번의 짧은 답장이 있고 초기 존댓말 관계라면 reply 후보 3개는 아래처럼 사실을 덧붙이지 않는 자연스러운 존댓말 형태를 사용하세요.\n1) 오늘 좀 피곤하셨나 봐요. 하루는 어땠어요?\n2) 그렇군요. 오늘은 어떻게 보내셨어요?\n3) 누워 계시는군요. 오늘 하루는 어떠셨어요?\n이 경우 반말 시작+존댓말 끝, 문법이 어색한 질문, 입력에 없는 시간대·활동·장소·미래 약속을 만들지 마세요.'''
assert old in s, 'quick source case rule missing'
s=s.replace(old,new,1)

assert '2026-08-23-potentia-v24-source-case' in s
assert '무슨 하다가 쉬는 거예요?' in s
p.write_text(s,encoding='utf-8')
print('Potentia v24 source case patch applied')
