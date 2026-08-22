from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')

assert '2026-08-23-potentia-v25-no-reply-separated' in s, 'expected v25 server not found'
s=s.replace('const SERVER_VERSION = "2026-08-23-potentia-v25-no-reply-separated";', 'const SERVER_VERSION = "2026-08-23-potentia-v26-final";', 1)

old='''    "읽씹 당했어":`- 읽씹을 추궁하거나 '왜 읽고 답 안 해?' 같은 공격적 표현은 금지합니다.\n- 같은 내용을 반복해서 보내지 말고 상황에 따라 기다리는 선택도 제안하세요.`,'''
new='''    "읽씹 당했어":`- 읽씹을 추궁하거나 '왜 읽고 답 안 해?' 같은 공격적 표현은 금지합니다.\n- 같은 내용을 반복해서 보내지 말고 상황에 따라 기다리는 선택도 제안하세요.\n- 초기 비긴급 관계에서 사용자가 이미 약 3일 기다렸고 아직 후속 연락을 보내지 않았다면, 지금은 딱 한 번만 낮은 압력의 확인 메시지를 제안하세요. 예: '요즘 바쁜 것 같네요. 여유 생기면 편하게 연락 주세요.' 또는 '일정 여유 생기면 편하게 연락 주세요.'\n- 그 한 번의 후속 확인에도 다시 무응답이면 추가 3일 대기 후 또 보내는 식으로 반복하지 말고 더 보내지 않는 것으로 종료하세요.\n- '혹시 요즘 바빠요?'처럼 답을 재촉하는 질문보다 선택권을 남기는 서술형 문장을 우선하고, '무슨 하고 지내세요?'처럼 어색한 문장을 만들지 마세요.`,'''
assert old in s, 'read-ignore situation rule anchor missing'
s=s.replace(old,new,1)

old='''- 초기 비긴급 무응답은 기본적으로 최소 약 3일 정도 기다린 뒤 한 번만 담백하게 확인하고, 그 확인에도 다시 무응답이면 종료한다. 한두 시간, 2~3시간, 하루 정도의 무응답만으로 추가 연락 종료를 권하지 않는다. 다만 약속 당일·안전·긴급 일정은 즉시 확인한다.'''
new='''- 초기 비긴급 무응답은 기본적으로 최소 약 3일 정도 기다린 뒤 한 번만 담백하게 확인한다. 사용자가 이미 약 3일을 기다린 상태라면 지금 그 한 번의 확인을 할 수 있다. 그 확인 메시지에도 다시 무응답이면 또 3일을 세어 두 번째·세 번째 후속 연락을 만들지 말고 종료한다. 한두 시간, 2~3시간, 하루 정도의 무응답만으로 추가 연락 종료를 권하지 않는다. 다만 약속 당일·안전·긴급 일정은 즉시 확인한다.'''
assert old in s, 'system no-reply anchor missing'
s=s.replace(old,new,1)

# Make quick-mode action explicit for already-waited cases.
old='''[[nextAction]]\n지금 연락할지 기다릴지와 바로 할 행동을 1~2문장으로 구체적으로 안내. 초기 대화에서 상대가 다시 짧게 답하면 ‘3일 기다림’을 적용하지 말고 반복되는 참여 패턴을 더 본다. 오직 답장을 보낸 뒤 새로 무응답이 생긴 경우에만 비긴급 상황에서 약 3일 정도 기다린 뒤 한 번 담백하게 확인하고, 그 확인에도 다시 무응답이면 멈춘다. 2~3시간·하루만으로 관계 종료를 권하지 말 것'''
new='''[[nextAction]]\n지금 연락할지 기다릴지와 바로 할 행동을 1~2문장으로 구체적으로 안내. 초기 대화에서 상대가 다시 짧게 답하면 ‘3일 기다림’을 적용하지 말고 반복되는 참여 패턴을 더 본다. 아직 후속 연락 전이고 이미 약 3일 무응답을 기다린 경우에는 지금 한 번만 낮은 압력의 확인을 제안하고, 그 확인에도 다시 무응답이면 추가 후속 연락 없이 종료한다고 명확히 안내한다. 아직 3일이 지나지 않은 새 비긴급 무응답이라면 약 3일 정도 기다린 뒤 한 번만 확인한다. 2~3시간·하루만으로 관계 종료를 권하지 말 것'''
assert old in s, 'quick no-reply action anchor missing'
s=s.replace(old,new,1)

assert '2026-08-23-potentia-v26-final' in s
assert '추가 후속 연락 없이 종료' in s
p.write_text(s,encoding='utf-8')
print('Potentia v26 final no-reply patch applied')
