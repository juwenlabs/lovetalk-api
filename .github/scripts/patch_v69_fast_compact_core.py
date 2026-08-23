from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')
old='const SERVER_VERSION = "2026-08-24-potentia-v68-fast-reply-starter";'
new='const SERVER_VERSION = "2026-08-24-potentia-v69-fast-compact-core";'
if old not in s: raise SystemExit('v68 marker missing')
s=s.replace(old,new,1)

# Dedicated short-system starter generation: same guards, less prompt overhead.
anchor='async function generateStarterResult(reqBody){\n'
if anchor not in s: raise SystemExit('starter function anchor missing')
starter_helper=r'''async function createFastStarterJson({content,advanced=false}){
  const system=`너는 썸톡 AI의 짧은 선톡 추천 엔진이다. 사용자가 준 사실만 사용한다. 입력에 없는 감정·경험·날짜·장소·날씨·과거 대화·공통 취향을 만들지 않는다. 차단·연락중단·명확한 거절·경계는 우회하거나 설득하지 않는다. 초기 관계는 존댓말을 기본으로 하고, 실제 대화에 웃음표현이 없으면 ㅋㅋ·ㅎㅎ·ㅎ를 먼저 넣지 않는다. 사용자가 말하지 않았는데 '생각났어요','기대돼요','저도 좋아해요','어제 얘기했던' 같은 1인칭 사실이나 과거 맥락을 만들지 않는다. 바로 보낼 수 있는 짧은 문장 3개만 JSON으로 출력한다.`;
  const prompt=String(content)+`\n\n[빠른 출력] 같은 설명을 반복하지 말고 JSON 하나만 완전하게 출력하세요. reason은 각각 짧은 한 문장입니다.`;
  async function run(maxTokens,extra=""){
    const ai=await anthropic.messages.create({model:"claude-haiku-4-5",system,max_tokens:maxTokens,messages:[{role:"user",content:prompt+extra}]});
    try{return parseClaudeJson(ai);}catch(e){
      const recovered=recoverReplyArrayJson(getClaudeText(ai));
      if(recovered)return recovered;
      throw e;
    }
  }
  try{return await run(advanced?400:340);}
  catch(_){return await run(advanced?520:460,"\n반드시 reply 3개를 모두 닫은 유효한 JSON만 출력하세요.");}
}

'''
s=s.replace(anchor,starter_helper+anchor,1)
old_call='let parsed=await createJsonWithRetry({model:"claude-haiku-4-5",maxTokens:advanced?430:330,retryMaxTokens:advanced?580:450,content:prompt});'
new_call='let parsed=await createFastStarterJson({content:prompt,advanced:!!advanced});'
if old_call not in s: raise SystemExit('v68 starter call missing')
s=s.replace(old_call,new_call,1)

# Replace ordinary reply/detail AI path with a smaller grounded response contract.
start=s.find('async function generateCompactReplyAnalysis(reqBody){')
end=s.find('\n\nasync function generateAnalysisResult(reqBody){',start)
if start<0 or end<0: raise SystemExit('compact reply function range missing')
new_func=r'''async function generateCompactReplyAnalysis(reqBody){
  const mode=String(reqBody?.mode||"quick");
  if(mode!=="quick" && mode!=="detail") return null;
  const message=String(reqBody?.message||"").trim();
  if(getCompactProTask(message)) return null;
  const isDetail=mode==="detail";
  const relation=String(reqBody?.relation||"미입력");
  const nickname=String(reqBody?.nickname||"미입력");
  const tone=String(reqBody?.tone||"자연스럽게");
  const recentMemory=String(reqBody?.recentMemory||"").slice(0,1200);
  const selectedSituation=String(reqBody?.selectedSituation||"");
  const profile=reqBody?.profile?JSON.stringify(reqBody.profile).slice(0,1000):"없음";
  const image=reqBody?.image;
  const images=reqBody?.images;
  const hasSingleImage=!!image?.data;
  const hasImages=Array.isArray(images)&&images.some(img=>img?.data);
  const taskData=`[현재 관계] ${relation}\n[상대] ${nickname}\n[사용자 입력] ${message||((hasImages||hasSingleImage)?"첨부 스크린샷 중심 분석":"입력 없음")}\n[원하는 톤] ${tone}\n[선택 상황] ${selectedSituation||"없음"}\n[프로필] ${profile}\n[최근 기억] ${recentMemory||"없음"}`;
  const prompt=isDetail
    ? `${taskData}\n\n상대의 반응과 대화 흐름을 분석하고 실제 답장 2개를 추천하세요. 단일 일상 공유·짧은 답장만으로 호감, 관심, '나를 의식함', 대화 의욕을 추정하지 마세요. 확인된 사실과 정보 한계를 분리하세요. 입력에 없는 감정·일정·장소·활동·과거 사건·미래 약속을 만들지 마세요. 사용자가 말하지 않은 1인칭 감정·경험도 답장에 넣지 마세요. 초기 존댓말 대화라면 존댓말을 유지하세요. 질문은 문장당 최대 하나입니다. JSON만 출력: {"meaning":"핵심 1문장","confidence":"높음|중간|낮음","signal":"상대 반응/정보 한계 1문장","action":"지금 할 행동 1문장","caution":"주의 1문장","replies":[{"label":"자연스럽게","text":"짧은 답장","reason":"짧은 이유"},{"label":"다른 느낌","text":"짧은 답장","reason":"짧은 이유"}]}`
    : `${taskData}\n\n지금 답장에 필요한 핵심만 판단하고 실제 답장 2개를 추천하세요. 단일 일상 공유·짧은 답장만으로 호감, 관심, '나를 의식함', 대화 의욕을 추정하지 마세요. 입력에 없는 감정·일정·장소·활동·과거 사건·미래 약속을 만들지 마세요. 사용자가 말하지 않은 1인칭 감정·경험도 넣지 마세요. 초기 존댓말 대화라면 존댓말을 유지하세요. 질문은 문장당 최대 하나입니다. JSON만 출력: {"meaning":"핵심 1문장","action":"한 줄 조언","caution":"주의 1문장","replies":[{"label":"자연스럽게","text":"짧은 답장","reason":"짧은 이유"},{"label":"다른 느낌","text":"짧은 답장","reason":"짧은 이유"}]}`;
  const content=[];
  const allowed=["image/jpeg","image/png","image/webp"];
  const imageList=Array.isArray(images)&&images.length?images.slice(0,10):(image?.data?[image]:[]);
  for(const img of imageList){
    if(!img?.data) continue;
    const mediaType=allowed.includes(img.mediaType)?img.mediaType:"image/jpeg";
    content.push({type:"image",source:{type:"base64",media_type:mediaType,data:img.data}});
  }
  content.push({type:"text",text:prompt});
  const system=`너는 썸톡 AI의 빠른 답장 코치다. 사실과 추론을 분리한다. 한 번의 신호로 상대의 호감·속마음·의도를 단정하거나 가능성이 높다고 말하지 않는다. 입력에 없는 사실을 만들지 않는다. 명확한 거절·차단·연락중단·경계·안전 위험을 존중한다. 답장은 사용자가 그대로 보내도 거짓이 없어야 한다. JSON 외 텍스트는 출력하지 않는다.`;
  async function run(maxTokens,extra=""){
    const c=extra?[...content,{type:"text",text:extra}]:content;
    const ai=await anthropic.messages.create({model:"claude-haiku-4-5",system,max_tokens:maxTokens,messages:[{role:"user",content:c}]});
    return parseClaudeJson(ai);
  }
  let raw;
  try{raw=await run(isDetail?390:300);}
  catch(_){raw=await run(isDetail?520:420,"JSON을 완전하게 닫아 더 짧게 다시 출력하세요.");}
  const meaning=String(raw?.meaning||"").trim();
  const action=String(raw?.action||"").trim();
  const signal=String(raw?.signal||"").trim();
  const caution=String(raw?.caution||"").trim();
  let out={
    meaning,
    confidence:isDetail && /^(높음|중간|낮음)$/.test(String(raw?.confidence||"").trim())?String(raw.confidence).trim():"낮음",
    emotion:isDetail?signal:"",
    flow:isDetail?signal:"",
    strategy:action,
    caution,
    dontSend:caution,
    advice:action,
    nextAction:action,
    replies:[]
  };
  const list=Array.isArray(raw?.replies)?raw.replies:[];
  out.replies=list.slice(0,2).map((x,i)=>sanitizeReplyObject(x,selectedSituation,["가장 자연스러운 답장","다른 느낌의 답장"][i]));
  if(!meaning||!action||!caution||out.replies.length<2||(isDetail&&!signal)) throw new Error("빠른 답장 분석 결과가 불완전합니다.");
  out=applyAnalysisPolicyGuards(out,reqBody||{},isDetail);
  if(Array.isArray(out.replies)) out.replies=out.replies.slice(0,2);
  return out;
}'''
s=s[:start]+new_func+s[end:]

p.write_text(s,encoding='utf-8')
