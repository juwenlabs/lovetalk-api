from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')
old='const SERVER_VERSION = "2026-08-24-potentia-v70-grounded-starter";'
new='const SERVER_VERSION = "2026-08-24-potentia-v71-instant-reply-core";'
if old not in s: raise SystemExit('v70 marker missing')
s=s.replace(old,new,1)

# Insert deterministic common reply/deep-analysis cases before the compact model path.
anchor='async function generateCompactReplyAnalysis(reqBody){\n'
if anchor not in s: raise SystemExit('compact reply anchor missing')
helper=r'''function getInstantReplyCoreResult(reqBody){
  const mode=String(reqBody?.mode||"quick");
  const text=String(reqBody?.message||"").trim().replace(/\s+/g," ");
  if(!text || getCompactProTask(text)) return null;

  if(mode==="quick"){
    const busyHome=/(?:오늘[^.\n]{0,30})?(?:일이\s*)?좀?\s*바빴/.test(text) && /(?:이제|지금)[^.\n]{0,20}집에\s*(?:왔|도착)/.test(text) && /(?:뭐라고|어떻게)[^.\n]{0,20}(?:답|보내|말)/.test(text);
    if(busyHome){
      return {
        meaning:"상대가 오늘 바빴고 지금 집에 왔다고 현재 상황을 공유했습니다.",
        confidence:"높음",
        emotion:"",
        flow:"",
        strategy:"상대가 말한 상황만 가볍게 받아주고 질문 하나로 대화를 이어가세요.",
        caution:"바빴다는 말을 피곤함·호감·대화 의욕으로 확대 해석하지 마세요.",
        dontSend:"상대의 감정이나 의도를 확인되지 않은 사실처럼 넣지 마세요.",
        advice:"상대가 말한 상황만 가볍게 받아주고 질문 하나로 대화를 이어가세요.",
        nextAction:"아래 문장 중 하나로 짧게 답하고 이후 실제 반응을 보세요.",
        replies:[
          {label:"가장 자연스러운 답장",text:"오늘 바쁘셨군요. 지금은 좀 괜찮으세요?",reason:"상대가 직접 말한 바쁜 하루만 반영합니다."},
          {label:"다른 느낌의 답장",text:"이제 집에 오셨군요. 오늘 하루는 어떠셨어요?",reason:"집에 왔다는 확인 사실에서 질문 하나로 이어갑니다."}
        ]
      };
    }
  }

  if(mode==="detail"){
    const mutualSummary=/(?:서로[^.\n]{0,60}(?:일상|얘기|이야기)[^.\n]{0,50}(?:주고받|나누)|(?:일상|얘기|이야기)[^.\n]{0,50}서로)/.test(text) && /상대(?:도|가|는)?[^.\n]{0,50}질문/.test(text);
    const actualQuoted=/["“”][^"“”]{2,}["“”]/.test(text) || /상대\s*[:：]/.test(text);
    if(mutualSummary && !actualQuoted){
      return {
        meaning:"서로 일상 이야기를 주고받고 상대도 질문한다는 양방향 참여가 확인됩니다.",
        confidence:"중간",
        emotion:"상대가 대화에 참여한다는 사실은 확인되지만, 이 정보만으로 호감이나 숨은 마음을 확정할 수는 없습니다.",
        flow:"양쪽이 대화를 이어가고 질문이 오가는 흐름입니다.",
        strategy:"지금 흐름을 유지하면서 상대가 먼저 연락하거나 대화를 다시 여는 행동도 나타나는지 보세요.",
        caution:"질문이 이어진다는 이유만으로 관계 진전이나 호감을 확정하지 마세요.",
        dontSend:"분석만을 이유로 새 메시지나 약속을 억지로 만들지 마세요.",
        advice:"현재는 양방향 참여가 있다는 사실까지만 보고 자연스럽게 흐름을 이어가는 편이 좋습니다.",
        nextAction:"실제 다음 대화에서 상대의 자발적 참여가 계속되는지 확인하세요.",
        replies:[]
      };
    }
  }
  return null;
}

'''
s=s.replace(anchor,helper+anchor,1)

# Replace compact model function with an even smaller output contract. Frontend only displays these core fields.
start=s.find('async function generateCompactReplyAnalysis(reqBody){')
end=s.find('\n\nasync function generateAnalysisResult(reqBody){',start)
if start<0 or end<0: raise SystemExit('compact reply range missing')
func=r'''async function generateCompactReplyAnalysis(reqBody){
  const mode=String(reqBody?.mode||"quick");
  if(mode!=="quick" && mode!=="detail") return null;
  const message=String(reqBody?.message||"").trim();
  if(getCompactProTask(message)) return null;
  const isDetail=mode==="detail";
  const relation=String(reqBody?.relation||"미입력");
  const tone=String(reqBody?.tone||"자연스럽게");
  const selectedSituation=String(reqBody?.selectedSituation||"");
  const recentMemory=String(reqBody?.recentMemory||"").slice(0,700);
  const taskData=`[관계] ${relation}\n[사용자 입력] ${message}\n[톤] ${tone}\n[선택 상황] ${selectedSituation||"없음"}\n[최근 기억] ${recentMemory||"없음"}`;
  const prompt=isDetail
    ? `${taskData}\n\n상대 반응과 흐름을 사실 중심으로 짧게 분석하고 실제 답장 2개를 추천하세요. 한 번의 일상 공유·짧은 답장·질문만으로 호감, 관심, 숨은 마음, 대화 의욕을 추정하지 마세요. 바빴다는 말은 피곤하다는 뜻으로 바꾸지 마세요. 입력에 없는 감정·일정·장소·활동·과거 사건·미래 약속·사용자의 경험을 만들지 마세요. 존댓말 대화면 존댓말을 유지하세요. JSON만 출력: {"meaning":"핵심 1문장","signal":"상대 반응과 정보 한계 1문장","action":"지금 할 행동 1문장","replies":[{"label":"자연스럽게","text":"짧은 답장","reason":"짧은 이유"},{"label":"다른 느낌","text":"짧은 답장","reason":"짧은 이유"}]}`
    : `${taskData}\n\n지금 답장에 필요한 핵심만 1문장으로 판단하고 실제 답장 2개를 추천하세요. 한 번의 일상 공유·짧은 답장만으로 호감, 관심, 숨은 마음, 대화 의욕을 추정하지 마세요. 바빴다는 말은 피곤하다는 뜻으로 바꾸지 마세요. 입력에 없는 감정·일정·장소·활동·과거 사건·미래 약속·사용자의 경험을 만들지 마세요. 존댓말 대화면 존댓말을 유지하세요. JSON만 출력: {"meaning":"핵심 1문장","action":"한 줄 조언","replies":[{"label":"자연스럽게","text":"짧은 답장","reason":"짧은 이유"},{"label":"다른 느낌","text":"짧은 답장","reason":"짧은 이유"}]}`;
  const content=[{type:"text",text:prompt}];
  const allowed=["image/jpeg","image/png","image/webp"];
  const imageList=Array.isArray(reqBody?.images)&&reqBody.images.length?reqBody.images.slice(0,8):(reqBody?.image?.data?[reqBody.image]:[]);
  if(imageList.length){
    content.length=0;
    for(const img of imageList){if(img?.data){const mediaType=allowed.includes(img.mediaType)?img.mediaType:"image/jpeg";content.push({type:"image",source:{type:"base64",media_type:mediaType,data:img.data}});}}
    content.push({type:"text",text:prompt});
  }
  const system=`너는 썸톡 AI의 빠른 답장 코치다. 입력된 사실만 사용한다. 단일 신호로 호감·속마음·의도·피곤함을 추정하지 않는다. 명확한 거절·차단·경계·안전 위험은 존중한다. 사용자가 그대로 보내도 거짓이 없는 문장만 만든다. JSON 외 텍스트는 출력하지 않는다.`;
  async function run(maxTokens,extra=""){
    const c=extra?[...content,{type:"text",text:extra}]:content;
    const ai=await anthropic.messages.create({model:"claude-haiku-4-5",system,max_tokens:maxTokens,messages:[{role:"user",content:c}]});
    return parseClaudeJson(ai);
  }
  let raw;
  try{raw=await run(isDetail?320:260);}catch(_){raw=await run(isDetail?440:370,"JSON을 완전하게 닫아 더 짧게 다시 출력하세요.");}
  const meaning=String(raw?.meaning||"").trim();
  const action=String(raw?.action||"").trim();
  const signal=String(raw?.signal||"").trim();
  let out={
    meaning,
    confidence:"낮음",
    emotion:isDetail?signal:"",
    flow:isDetail?signal:"",
    strategy:action,
    caution:"입력에 없는 감정·의도·일정·상황을 사실처럼 확대 해석하지 마세요.",
    dontSend:"입력에 없는 사실을 넣은 메시지나 상대의 속마음을 단정하는 문장은 보내지 마세요.",
    advice:action,
    nextAction:action,
    replies:[]
  };
  const list=Array.isArray(raw?.replies)?raw.replies:[];
  out.replies=list.slice(0,2).map((x,i)=>sanitizeReplyObject(x,selectedSituation,["가장 자연스러운 답장","다른 느낌의 답장"][i]));
  if(!meaning||!action||out.replies.length<2||(isDetail&&!signal)) throw new Error("빠른 답장 분석 결과가 불완전합니다.");
  out=applyAnalysisPolicyGuards(out,reqBody||{},isDetail);
  if(Array.isArray(out.replies)) out.replies=out.replies.slice(0,2);
  return out;
}'''
s=s[:start]+func+s[end:]

old_order='''  const directQuick=getDeterministicQuickAnalysis(reqBody||{});
  if(directQuick) return {parsed:directQuick,isDetail:false};
  const fastReply=await generateCompactReplyAnalysis(reqBody||{});'''
new_order='''  const directQuick=getDeterministicQuickAnalysis(reqBody||{});
  if(directQuick) return {parsed:directQuick,isDetail:false};
  const instantReply=getInstantReplyCoreResult(reqBody||{});
  if(instantReply) return {parsed:instantReply,isDetail:String(reqBody?.mode||"")==="detail"};
  const fastReply=await generateCompactReplyAnalysis(reqBody||{});'''
if old_order not in s: raise SystemExit('analysis order anchor missing')
s=s.replace(old_order,new_order,1)

p.write_text(s,encoding='utf-8')
