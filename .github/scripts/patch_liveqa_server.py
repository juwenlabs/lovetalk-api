from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')

assert '2026-08-23-potentia-v22-timing-enforced' in s, 'expected v22 server not found'
s=s.replace('const SERVER_VERSION = "2026-08-23-potentia-v22-timing-enforced";', 'const SERVER_VERSION = "2026-08-23-potentia-v23-tone-context";', 1)

old='''- 번호 교환 직후·소개팅·앱 매칭·초기 낯선 관계에서 사용자가 이미 반말 관계라고 명시하지 않았다면 존댓말을 기본으로 한다. 상대 이름은 첫 메시지에 꼭 필요하지 않으면 생략하고 불필요하게 반복하지 않는다.'''
new='''- 번호 교환 직후·소개팅·앱 매칭·초기 낯선 관계에서 사용자가 이미 반말 관계라고 명시하지 않았다면 존댓말을 기본으로 한다. 한 답장 안에서도 처음부터 끝까지 존댓말을 유지하고 ‘그렇구나, ...했어요?’, ‘그래, ...해요?’처럼 반말 시작 + 존댓말 끝을 섞지 않는다. 상대 이름은 첫 메시지에 꼭 필요하지 않으면 생략하고 불필요하게 반복하지 않는다.'''
assert old in s, 'initial tone anchor missing'
s=s.replace(old,new,1)

old='''- ‘그때 얘기했던 데’, ‘아까 말한 카페’, ‘전에 말한 전시’처럼 입력에 실제로 등장하지 않은 공유 장소·대화 주제·과거 사건을 만들어 답장 명분으로 쓰지 않는다. ‘초반 어색함이 없었다’처럼 입력에 없는 관계 평가도 사실처럼 보태지 않는다.'''
new='''- ‘그때 얘기했던 데’, ‘아까 말한 카페’, ‘전에 말한 전시’처럼 입력에 실제로 등장하지 않은 공유 장소·대화 주제·과거 사건을 만들어 답장 명분으로 쓰지 않는다. ‘초반 어색함이 없었다’처럼 입력에 없는 관계 평가도 사실처럼 보태지 않는다.
- 입력에 다음 만남·약속·통화 계획이 실제로 확인되지 않았다면 ‘나중에 뵐 때’, ‘다음에 만나서’, ‘그날 보자’처럼 미래 만남이 이미 잡힌 것처럼 말하지 않는다. 약속이 없는 초기 대화에서는 현재 대화만 자연스럽게 이어가거나 마무리한다.'''
assert old in s, 'future-context anchor missing'
s=s.replace(old,new,1)

old='''특히 입력에 상대의 “그냥 누워 있어요” 같은 한 번의 짧은 답장이 있다면, reply 후보 중 하나는 포텐티아 매뉴얼 예시처럼 가벼운 가능성 표현 + 개방형 질문 하나를 한 답장 안에 담으세요. 입력에 없는 시간대·구체적 활동·장소는 만들지 마세요.'''
new='''특히 입력에 상대의 “그냥 누워 있어요” 같은 한 번의 짧은 답장이 있다면, reply 후보 중 하나는 포텐티아 매뉴얼 예시처럼 가벼운 가능성 표현 + 개방형 질문 하나를 한 답장 안에 담으세요. 초기 관계라면 모든 reply 후보는 처음부터 끝까지 존댓말을 유지하세요. 입력에 없는 시간대·구체적 활동·장소·미래 약속은 만들지 마세요.'''
assert old in s, 'quick example anchor missing'
s=s.replace(old,new,1)

assert '2026-08-23-potentia-v23-tone-context' in s
assert '반말 시작 + 존댓말 끝' in s
assert '미래 만남이 이미 잡힌 것처럼 말하지 않는다' in s
p.write_text(s,encoding='utf-8')
print('Potentia v23 tone/context patch applied')
