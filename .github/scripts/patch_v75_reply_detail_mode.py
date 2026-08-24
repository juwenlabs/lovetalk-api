from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')

old='const SERVER_VERSION = "2026-08-24-potentia-v74-three-replies";'
new='const SERVER_VERSION = "2026-08-24-potentia-v75-reply-detail-mode";'
if old not in s:
    raise SystemExit('v74 version marker missing')
s=s.replace(old,new,1)

anchor='''    if(!isNamedProTask && !looksLikeDirectDialogue){'''
replacement='''    const isReplyDetailRequest=!!reqBody?.replyDetailMode;\n    if(!isNamedProTask && !looksLikeDirectDialogue && !isReplyDetailRequest){'''
count=s.count(anchor)
if count < 1:
    raise SystemExit('reply wipe anchor missing')
s=s.replace(anchor,replacement)

p.write_text(s,encoding='utf-8')
print('patched replyDetailMode guards:',count)
