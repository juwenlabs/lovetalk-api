from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')

assert '2026-08-23-potentia-v24-source-case' in s, 'expected v24 server not found'
s=s.replace('const SERVER_VERSION = "2026-08-23-potentia-v24-source-case";', 'const SERVER_VERSION = "2026-08-23-potentia-v25-no-reply-separated";', 1)

old='''특히 입력에 상대의 “그냥 누워 있어요”라는 한 번의 짧은 답장이 있고 초기 존댓말 관계라면 reply 후보 3개는 아래처럼 사실을 덧붙이지 않는 자연스러운 존댓말 형태를 사용하세요.\n1) 오늘 좀 피곤하셨나 봐요. 하루는 어땠어요?\n2) 그렇군요. 오늘은 어떻게 보내셨어요?\n3) 누워 계시는군요. 오늘 하루는 어떠셨어요?\n이 경우 반말 시작+존댓말 끝, 문법이 어색한 질문, 입력에 없는 시간대·활동·장소·미래 약속을 만들지 마세요.'''
new='''특히 입력에 상대의 “그냥 누워 있어요”라는 한 번의 짧은 답장이 있고 초기 존댓말 관계라면 reply 후보 3개는 아래처럼 사실을 덧붙이지 않는 자연스러운 존댓말 형태를 사용하세요.\n1) 오늘 좀 피곤하셨나 봐요. 하루는 어땠어요?\n2) 그렇군요. 오늘은 어떻게 보내셨어요?\n3) 누워 계시는군요. 오늘 하루는 어떠셨어요?\n이 경우 meaning은 ‘상대가 누워 있다고 짧게 답했다’는 확인 사실과 정보 한계만 설명하고 휴식 중이라고 확정하지 마세요. 반말 시작+존댓말 끝, 문법이 어색한 질문, 입력에 없는 시간대·활동·장소·미래 약속을 만들지 마세요.'''
assert old in s, 'source-case quick anchor missing'
s=s.replace(old,new,1)

old='''[[nextAction]]\n지금 연락할지 기다릴지와 바로 할 행동을 1~2문장으로 구체적으로 안내. 초기 대화라면 반드시 조건부로 다음 원칙을 포함하세요: “이 답장 뒤 새로 무응답이 생기면 비긴급 상황에서는 약 3일 정도 기다린 뒤 한 번만 담백하게 확인하고, 그 확인에도 다시 무응답이면 멈춘다.” 2~3시간·하루만으로 관계 종료를 권하지 말 것'''
new='''[[nextAction]]\n지금 연락할지 기다릴지와 바로 할 행동을 1~2문장으로 구체적으로 안내. 초기 대화에서 상대가 다시 짧게 답하면 ‘3일 기다림’을 적용하지 말고 반복되는 참여 패턴을 더 본다. 오직 답장을 보낸 뒤 새로 무응답이 생긴 경우에만 비긴급 상황에서 약 3일 정도 기다린 뒤 한 번 담백하게 확인하고, 그 확인에도 다시 무응답이면 멈춘다. 2~3시간·하루만으로 관계 종료를 권하지 말 것'''
assert old in s, 'next-action timing anchor missing'
s=s.replace(old,new,1)

assert '2026-08-23-potentia-v25-no-reply-separated' in s
assert '오직 답장을 보낸 뒤 새로 무응답이 생긴 경우에만' in s
p.write_text(s,encoding='utf-8')
print('Potentia v25 no-reply separation patch applied')
