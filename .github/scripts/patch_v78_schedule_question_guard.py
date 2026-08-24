from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')
old='const SERVER_VERSION = "2026-08-24-potentia-v77-openai-terra";'
new='const SERVER_VERSION = "2026-08-24-potentia-v78-openai-schedule-guard";'
if old not in s: raise SystemExit('v77 version marker missing')
s=s.replace(old,new,1)

anchor='''  const compact=msg.replace(/\\s+/g," ");\n  const replyDetailRequested=!!reqBody?.replyDetailMode;'''
insert=r'''  const compact=msg.replace(/\s+/g," ");
  const replyDetailRequested=!!reqBody?.replyDetailMode;

  // Direct schedule questions such as "내일 뭐해?" must never invent the user's availability.
  const asksUserSchedule=/(?:오늘|내일|주말|이번\s*주말)[^.?？!]{0,18}(?:뭐\s*(?:해|하니|하냐|하세요|하실|할\s*거)|시간\s*(?:돼|되니|되세요|괜찮))/.test(compact);
  const explicitUserSchedule=/(?:나는|내가|저는|저도|나도|사용자)[^.?!？!]{0,100}(?:일정|약속|출근|회사|근무|일\s*해|쉬어|쉰|집에|가능|시간\s*돼|안\s*돼|어려워|어렵|바빠|한가)/.test(compact);
  if(asksUserSchedule && !explicitUserSchedule){
    const polite=/(?:뭐\s*하세요|뭐\s*하실|시간\s*되세요|괜찮으세요)/.test(compact);
    out.meaning="상대가 사용자의 일정이나 가능 여부를 물었습니다. 사용자의 실제 일정은 입력되지 않았습니다.";
    out.confidence="높음";
    out.caution="사용자가 말하지 않은 일정·약속·바쁨·휴식 여부를 만들어 답하지 마세요.";
    out.dontSend="평일이라 어려워요, 약속은 없어요, 집에 있을 것 같아요처럼 확인되지 않은 사용자 일정을 사실처럼 보내지 마세요.";
    out.advice="실제 일정을 모르는 상태에서는 일정 사실을 만들지 말고 상대가 왜 물었는지 자연스럽게 확인하세요.";
    out.nextAction="아래 문장 중 하나로 질문의 의도를 먼저 확인한 뒤 실제 일정이 필요할 때 사용자 본인이 확인해 답하세요.";
    out.replies=polite?[
      {label:"자연스럽게",text:"왜요, 무슨 일 있어요?",reason:"사용자의 일정을 만들지 않고 상대가 물은 이유만 확인합니다."},
      {label:"조금 더 가볍게",text:"내일이요? 왜 물어보세요?",reason:"일정 가능 여부를 추정하지 않습니다."},
      {label:"조금 더 여유 있게",text:"혹시 무슨 일 있으세요?",reason:"거짓 일정 없이 상대의 용건을 먼저 확인합니다."}
    ]:[
      {label:"자연스럽게",text:"왜, 무슨 일 있어?",reason:"사용자의 일정을 만들지 않고 상대가 물은 이유만 확인합니다."},
      {label:"조금 더 가볍게",text:"왜? 내일 뭐 하려고?",reason:"일정 가능 여부를 추정하지 않고 상대의 의도를 확인합니다."},
      {label:"조금 더 여유 있게",text:"내일? 왜 물어봐?",reason:"거짓 일정 없이 질문에 자연스럽게 반응합니다."}
    ];
    return out;
  }'''
if anchor not in s: raise SystemExit('applyAnalysisPolicyGuards anchor missing')
s=s.replace(anchor,insert,1)

p.write_text(s,encoding='utf-8')
