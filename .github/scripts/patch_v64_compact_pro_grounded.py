from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')
old='const SERVER_VERSION = "2026-08-23-potentia-v63-compact-pro-output";'
new='const SERVER_VERSION = "2026-08-23-potentia-v64-compact-pro-grounded";'
if old not in s: raise SystemExit('v63 marker missing')
s=s.replace(old,new,1)

# Preserve three useful alternatives when a sendable message is appropriate.
s=s.replace(
  '"replies":${wantsReplies?\'[{"label":"추천","text":"실제로 보낼 수 있는 짧은 문장","reason":"짧은 이유"}]\':\'[]\'}',
  '"replies":${wantsReplies?\'보낼 문장이 실제로 필요하면 서로 역할이 다른 짧은 대안 3개를 배열로 만들고, 아직 보낼 필요가 없거나 근거가 부족하면 빈 배열 []\':\'[]\'}',
  1
)

# Slightly lower generous budgets without forcing truncation; retry remains available.
s=s.replace('raw=await run(wantsReplies?850:620);','raw=await run(wantsReplies?760:560);',1)
s=s.replace('raw=await run(wantsReplies?1050:800,"반드시 완전한 JSON 하나만 짧게 다시 출력하세요.");','raw=await run(wantsReplies?980:760,"반드시 완전한 JSON 하나만 짧게 다시 출력하세요.");',1)

anchor='''  const list=Array.isArray(raw?.replies)?raw.replies:[];
  if(wantsReplies) out.replies=list.slice(0,3).map((x,i)=>sanitizeReplyObject(x,selectedSituation,["가장 자연스러운 답장","조금 더 다정한 답장","조금 더 여유 있는 답장"][i]||"추천"));
  if(task==="monthly"||task==="memory") out.replies=[];
  const placeholder=/(?:\\[[^\\]]+\\]|○○|상대\\s*메시지\\s*필요|구체적\\s*답장\\s*필요)/;
  out.replies=out.replies.filter(x=>x?.text&&!placeholder.test(String(x.text)));
  if(!out.meaning||!out.emotion||!out.strategy||!out.caution){'''
replacement='''  const list=Array.isArray(raw?.replies)?raw.replies:[];
  if(wantsReplies) out.replies=list.slice(0,3).map((x,i)=>sanitizeReplyObject(x,selectedSituation,["가장 자연스러운 답장","조금 더 다정한 답장","조금 더 여유 있는 답장"][i]||"추천"));
  if(task==="monthly"||task==="memory") out.replies=[];

  const rawMessage=String(reqBody?.message||"");
  const marker="[사용자 입력]";
  const userText=(rawMessage.includes(marker)?rawMessage.slice(rawMessage.lastIndexOf(marker)+marker.length):rawMessage.replace(/^\\s*\\[PRO[^\\]]+\\]\\s*/,"")).trim();
  const hasChannel=/(?:카카오톡|카톡|문자|메신저|DM|디엠|인스타|SNS)/i.test(userText);
  if(!hasChannel){
    for(const key of ["meaning","emotion","flow","strategy","caution","dontSend","advice","nextAction"]){
      out[key]=String(out[key]||"").replace(/카카오톡|카톡|문자\\s*대화|문자|메신저|DM|디엠/gi,"대화");
    }
  }

  const explicitWait=/(?:\\d+\\s*(?:일|주|주일|시간|분)|하루|이틀|사흘|며칠|일주일|한\\s*달)[^.\\n]{0,60}(?:기다|관찰|연락|답|확인)/.test(userText);
  const inventedPeriod=/(?:\\d+\\s*~\\s*\\d+\\s*(?:일|주)|\\d+\\s*(?:일|주)\\s*(?:더|동안|뒤)|며칠\\s*(?:더|동안|뒤)|한두\\s*번\\s*(?:더|관찰))/;
  if(!explicitWait && inventedPeriod.test(String(out.strategy||""))){
    const safeAction={
      risk:"사용자의 평소 답장 리듬을 유지하고, 같은 압박이나 경계 무시가 실제로 반복되는지 다음 대화에서 확인하세요.",
      confession:"고백을 서두르지 말고 실제 만남과 상대의 자발적 연락·대화 재개·구체적 일정 참여가 확인되는지 먼저 보세요.",
      date:"상대의 실제 참여와 사용자의 실제 가능한 일정을 확인한 뒤에만 만남 제안을 구체화하세요.",
      monthly:"입력된 기록에서 확인되는 행동 변화만 비교하고, 별도의 임의 대기 기간을 만들지 마세요.",
      memory:"확인된 사실과 반복 관찰된 행동만 기억 후보로 남기고 임의의 관찰 기간을 만들지 마세요."
    }[task];
    out.strategy=safeAction; out.advice=safeAction; out.nextAction=safeAction;
  }

  const metaReply=/(?:메시지\\s*전문|스크린샷|공유해|보여줄\\s*수|보여줘|입력해|정보가\\s*필요|구체적\\s*대화.*필요|정확한.*내용.*필요)/;
  const placeholder=/(?:\\[[^\\]]+\\]|○○|상대\\s*메시지\\s*필요|구체적\\s*답장\\s*필요)/;
  out.replies=out.replies.filter(x=>x?.text&&!placeholder.test(String(x.text))&&!metaReply.test(String(x.text)));

  const asksForReply=/(?:뭐라고\\s*(?:답|보내|말)|어떻게\\s*답|답장\\s*(?:추천|뭐|어떻게)|보낼\\s*(?:말|문장)|문장\\s*추천)/.test(userText);
  if(task==="risk" && !asksForReply) out.replies=[];

  if(!out.meaning||!out.emotion||!out.strategy||!out.caution){'''
if anchor not in s: raise SystemExit('v63 postprocess anchor missing')
s=s.replace(anchor,replacement,1)

p.write_text(s,encoding='utf-8')
