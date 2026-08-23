from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')
old='const SERVER_VERSION = "2026-08-23-potentia-v56-unknown-date-block-bypass";'
new='const SERVER_VERSION = "2026-08-23-potentia-v57-no-send-detail-replies";'
if old not in s:
    raise SystemExit('v56 version anchor not found')
s=s.replace(old,new,1)

anchor='''  return out;\n}\n\nfunction getDeterministicQuickAnalysis(reqBody){'''
if anchor not in s:
    raise SystemExit('applyAnalysisPolicyGuards end anchor not found')
insert='''  // v57: when a detailed analysis concludes that the user should not send a\n  // new message and should wait for the counterpart's voluntary participation,\n  // reply cards must be empty. Action instructions are not sendable replies.\n  if(isDetail){\n    const actionText=[out.advice,out.nextAction,out.dontSend].filter(Boolean).join(" ");\n    const noNewMessage=/(?:지금|현재|당분간)[^.\\n]{0,90}(?:먼저\\s*연락(?:할|하지|을)?|새\\s*메시지|추가\\s*메시지|새\\s*대화)[^.\\n]{0,70}(?:아니|말|않|중단|보내지|기다)|상대(?:의|가)?[^.\\n]{0,70}(?:자발적\\s*연락|먼저\\s*연락)[^.\\n]{0,60}기다/.test(actionText);\n    if(noNewMessage){\n      out.replies=[];\n      const inputHasExplicitWait=/(?:하루|이틀|사흘|\\d+\\s*일|며칠|일주일|주일|시간\\s*뒤|분\\s*뒤)[^.\\n]{0,50}(?:기다|연락|보내)/.test(compact);\n      if(!inputHasExplicitWait){\n        out.nextAction="지금은 새 메시지를 먼저 보내지 말고 상대가 스스로 연락하거나 대화를 시작하는지 확인하세요. 상대의 자발적 참여가 생기기 전에는 사용자의 선연락 횟수를 더 늘리지 마세요.";\n      }\n    }\n  }\n  return out;\n}\n\nfunction getDeterministicQuickAnalysis(reqBody){'''
s=s.replace(anchor,insert,1)
p.write_text(s,encoding='utf-8')
print('patched v57')
