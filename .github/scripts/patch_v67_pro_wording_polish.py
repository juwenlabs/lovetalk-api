from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')
old='const SERVER_VERSION = "2026-08-23-potentia-v66-grounded-fast-pro";'
new='const SERVER_VERSION = "2026-08-23-potentia-v67-grounded-fast-pro-final";'
if old not in s: raise SystemExit('v66 marker missing')
s=s.replace(old,new,1)
old_text='meaning:`상대가 보드게임을 좋아한다고 직접 말했고 사용자는 ${when}이 가능하다고 밝혔습니다. 이 두 사실만으로 가볍게 만남을 제안할 근거는 충분합니다.`,'
new_text='meaning:`상대가 보드게임을 좋아한다고 직접 말했고 사용자의 실제 가능 일정은 ${when}입니다. 이 두 사실만으로 가볍게 만남을 제안할 근거는 충분합니다.`,'
if old_text not in s: raise SystemExit('wording anchor missing')
s=s.replace(old_text,new_text,1)
p.write_text(s,encoding='utf-8')
