from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')
old='const SERVER_VERSION = "2026-08-24-potentia-v75-reply-detail-mode";'
new='const SERVER_VERSION = "2026-08-24-potentia-v76-reply-detail-safety";'
if old not in s: raise SystemExit('v75 marker missing')
s=s.replace(old,new,1)

anchor='''  const compact=msg.replace(/\\s+/g," ");\n\n  // Potentia no-reply rule:'''
insert='''  const compact=msg.replace(/\\s+/g," ");\n  const replyDetailRequested=!!reqBody?.replyDetailMode;\n  const explicitNoContactBoundary=/(?:차단(?:했|당했|됐|되어|함)|더\\s*이상\\s*연락(?:하지|\\s*하지\\s*말|하지마)|연락\\s*(?:하지\\s*말|하지마|중단))/.test(compact);\n  if(isDetail && replyDetailRequested && explicitNoContactBoundary){\n    out.replies=[];\n    out.confidence="높음";\n    out.caution="상대가 연락 중단이나 차단 의사를 명확히 한 경우 다른 채널로 우회하거나 이유를 묻기 위해 다시 연락하지 마세요.";\n    out.dontSend="마지막으로 한 번만, 이유만 알려줘처럼 추가 연락을 이어가는 문장은 보내지 마세요.";\n    out.advice="지금은 답장을 만드는 것보다 상대의 명확한 연락 경계를 존중하고 연락을 멈추는 것이 맞습니다.";\n    out.nextAction="새 메시지를 보내지 말고 연락을 중단하세요.";\n    return out;\n  }\n\n  // Potentia no-reply rule:'''
if anchor not in s: raise SystemExit('applyAnalysisPolicyGuards compact anchor missing')
s=s.replace(anchor,insert,1)

old2='''    const isReplyDetailRequest=!!reqBody?.replyDetailMode;'''
new2='''    const isReplyDetailRequest=replyDetailRequested;'''
if old2 not in s: raise SystemExit('v75 reply detail declaration missing')
s=s.replace(old2,new2,1)

p.write_text(s,encoding='utf-8')
