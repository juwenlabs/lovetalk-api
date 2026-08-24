from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')

old='const SERVER_VERSION = "2026-08-24-potentia-v73-tiered-replies";'
new='const SERVER_VERSION = "2026-08-24-potentia-v74-three-replies";'
if old not in s: raise SystemExit('v73 marker missing')
s=s.replace(old,new,1)

# Both free and PRO starter flows now return three suggestions.
repls=[
('const desiredStarterReplies=advanced?3:1;','const desiredStarterReplies=3;'),
('const starterLimit=advanced?3:1;','const starterLimit=3;'),
('const starterLimit=req.body?.advanced?3:1;','const starterLimit=3;'),
('const desiredReplyCount=isDetail?3:1;','const desiredReplyCount=3;'),
('return {...parsed,replies:parsed.replies.slice(0,paid?3:1)};','return {...parsed,replies:parsed.replies.slice(0,3)};'),
]
for a,b in repls:
    if a not in s: raise SystemExit('missing anchor: '+a)
    s=s.replace(a,b,1)

old='''${advanced\n  ? '{"replies":[{"label":"자연스럽게","text":"먼저 보낼 메시지","reason":"이유 1문장"},{"label":"다정하게","text":"먼저 보낼 메시지","reason":"이유 1문장"},{"label":"센스 있게","text":"먼저 보낼 메시지","reason":"이유 1문장"}]}'\n  : '{"replies":[{"label":"자연스럽게","text":"가장 자연스러운 먼저 보낼 메시지","reason":"이유 1문장"}]}' }'''
new=''''{"replies":[{"label":"자연스럽게","text":"먼저 보낼 메시지","reason":"이유 1문장"},{"label":"다정하게","text":"먼저 보낼 메시지","reason":"이유 1문장"},{"label":"센스 있게","text":"먼저 보낼 메시지","reason":"이유 1문장"}]}''' 
if old not in s: raise SystemExit('starter JSON tier anchor missing')
s=s.replace(old,new,1)

# Quick/free reply compact path should ask for and validate three answers too.
old='''    : `${taskData}\\n\\n지금 답장에 필요한 핵심만 1문장으로 판단하고 실제 답장 1개를 추천하세요.'''
new='''    : `${taskData}\\n\\n지금 답장에 필요한 핵심만 1문장으로 판단하고 실제 답장 3개를 추천하세요.'''
if old not in s: raise SystemExit('quick prompt count anchor missing')
s=s.replace(old,new,1)

old='''JSON만 출력: {"meaning":"핵심 1문장","action":"한 줄 조언","replies":[{"label":"자연스럽게","text":"짧은 답장","reason":"짧은 이유"}]}`;'''
new='''JSON만 출력: {"meaning":"핵심 1문장","action":"한 줄 조언","replies":[{"label":"자연스럽게","text":"짧은 답장","reason":"짧은 이유"},{"label":"다정하게","text":"짧은 답장","reason":"짧은 이유"},{"label":"조금 더 여유 있게","text":"짧은 답장","reason":"짧은 이유"}]}`;'''
if old not in s: raise SystemExit('quick JSON count anchor missing')
s=s.replace(old,new,1)

old='''  try{raw=await run(isDetail?430:190);}catch(_){raw=await run(isDetail?560:290,"JSON을 완전하게 닫아 더 짧게 다시 출력하세요.");}'''
new='''  try{raw=await run(isDetail?430:360);}catch(_){raw=await run(isDetail?560:480,"JSON을 완전하게 닫아 더 짧게 다시 출력하세요.");}'''
if old not in s: raise SystemExit('compact token anchor missing')
s=s.replace(old,new,1)

# Quick/common instant case previously had two cards; add a grounded third one.
old='''          {label:"가장 자연스러운 답장",text:"오늘 바쁘셨군요. 지금은 좀 괜찮으세요?",reason:"상대가 직접 말한 바쁜 하루만 반영합니다."},\n          {label:"다른 느낌의 답장",text:"이제 집에 오셨군요. 오늘 하루는 어떠셨어요?",reason:"집에 왔다는 확인 사실에서 질문 하나로 이어갑니다."}\n        ]'''
new='''          {label:"가장 자연스러운 답장",text:"오늘 바쁘셨군요. 지금은 좀 괜찮으세요?",reason:"상대가 직접 말한 바쁜 하루만 반영합니다."},\n          {label:"다른 느낌의 답장",text:"이제 집에 오셨군요. 오늘 하루는 어떠셨어요?",reason:"집에 왔다는 확인 사실에서 질문 하나로 이어갑니다."},\n          {label:"조금 더 가볍게",text:"오늘 많이 바쁘셨네요. 지금은 좀 여유가 생기셨어요?",reason:"상대가 말한 바쁜 하루와 귀가 사실만 사용합니다."}\n        ]'''
if old not in s: raise SystemExit('quick instant reply anchor missing')
s=s.replace(old,new,1)

# Streaming free analysis must emit all three reply cards.
old='''    const order=isDetail?["meaning","confidence","emotion","flow","strategy","caution","dontSend","reply1","reply2","reply3","advice","nextAction"]:["meaning","emotion","caution","reply1","advice","nextAction"];'''
new='''    const order=isDetail?["meaning","confidence","emotion","flow","strategy","caution","dontSend","reply1","reply2","reply3","advice","nextAction"]:["meaning","emotion","caution","reply1","reply2","reply3","advice","nextAction"];'''
if old not in s: raise SystemExit('analysis stream order anchor missing')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
