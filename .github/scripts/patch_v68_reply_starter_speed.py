from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')
old='const SERVER_VERSION = "2026-08-23-potentia-v67-grounded-fast-pro-final";'
new='const SERVER_VERSION = "2026-08-24-potentia-v68-fast-reply-starter";'
if old not in s: raise SystemExit('v67 marker missing')
s=s.replace(old,new,1)

# Keep starter output compact so normal and PRO starter requests finish sooner.
old_starter='let parsed=await createJsonWithRetry({model:"claude-haiku-4-5",maxTokens:advanced?620:420,retryMaxTokens:advanced?760:560,content:prompt});'
new_starter='let parsed=await createJsonWithRetry({model:"claude-haiku-4-5",maxTokens:advanced?430:330,retryMaxTokens:advanced?580:450,content:prompt});'
if old_starter not in s: raise SystemExit('starter token anchor missing')
s=s.replace(old_starter,new_starter,1)
s=s.replace('- 각 reason에는 왜 지금 이 문장이 적합한지 1~2문장으로 구체적으로 설명하세요.','- 각 reason은 왜 적합한지 짧은 1문장으로만 설명하세요.',1)

anchor='async function generateAnalysisResult(reqBody){\n'
if anchor not in s: raise SystemExit('analysis anchor missing')
code=r'''async function generateCompactReplyAnalysis(reqBody){
  const mode=String(reqBody?.mode||"quick");
  if(mode!=="quick" && mode!=="detail") return null;
  const message=String(reqBody?.message||"");
  if(getCompactProTask(message)) return null;

  const {relation,nickname,tone,image,images,profile,recentMemory,selectedSituation}=reqBody||{};
  const hasSingleImage=!!image?.data;
  const hasImages=Array.isArray(images)&&images.some(img=>img?.data);
  const common=buildCommonPrompt({relation,nickname,message,tone,profile,recentMemory,selectedSituation,hasImages,hasSingleImage});
  const isDetail=mode==="detail";
  const prompt=`${common}\n\n[빠른 답장 분석]\n${isDetail?"상대의 반응과 대화 흐름을 한 단계 더 깊게 보되, 같은 뜻을 반복하지 마세요.":"지금 답장에 필요한 핵심만 빠르게 정리하세요."}\n확인된 사실과 정보 한계를 우선하고 입력에 없는 감정·일정·장소·활동·과거 사건·미래 약속을 만들지 마세요. 차단·명확한 거절·경계·안전 위험은 우회하거나 설득하지 않습니다. 사용자의 실제 가능 일정이 없으면 임의의 날짜·시간을 만들지 않습니다. 질문은 추천 문장 하나당 최대 하나입니다.\n반드시 JSON 하나만 출력하세요.\n{"meaning":"핵심 분석 1~2문장","confidence":"높음|중간|낮음","signal":"${isDetail?"상대 반응/대화 흐름 1~2문장":"필요한 경우만 짧은 반응 해석 1문장"}","action":"지금 할 행동 또는 한 줄 조언 1~2문장","caution":"주의할 점 1문장","dontSend":"보내지 말아야 할 행동/문장 1문장","replies":[{"label":"자연스럽게","text":"실제로 보낼 짧은 답장","reason":"짧은 이유"},{"label":"다른 톤","text":"실제로 보낼 짧은 답장","reason":"짧은 이유"}]}`;
  const content=[];
  const allowed=["image/jpeg","image/png","image/webp"];
  const imageList=Array.isArray(images)&&images.length?images.slice(0,15):(image?.data?[image]:[]);
  for(const img of imageList){
    if(!img?.data) continue;
    const mediaType=allowed.includes(img.mediaType)?img.mediaType:"image/jpeg";
    content.push({type:"image",source:{type:"base64",media_type:mediaType,data:img.data}});
  }
  content.push({type:"text",text:prompt});
  const system=`너는 썸톡 AI의 빠른 답장 코치다. 사실과 추론을 분리하고 입력에 없는 사실을 만들지 않는다. 명확한 거절·차단·경계·안전 위험을 존중한다. 단일 신호로 호감이나 속마음을 확정하지 않는다. 사용자가 그대로 보내도 거짓이 되지 않는 짧은 답장만 만든다. JSON 외 텍스트는 출력하지 않는다.`;
  async function run(maxTokens,extra=""){
    const c=extra?[...content,{type:"text",text:extra}]:content;
    const ai=await anthropic.messages.create({model:"claude-haiku-4-5",system,max_tokens:maxTokens,messages:[{role:"user",content:c}]});
    return parseClaudeJson(ai);
  }
  let raw;
  try{ raw=await run(isDetail?560:430); }
  catch(_){ raw=await run(isDetail?720:580,"JSON을 완전한 형태로 더 짧게 다시 출력하세요."); }
  let out={
    meaning:String(raw?.meaning||"").trim(),
    confidence:/^(높음|중간|낮음)$/.test(String(raw?.confidence||"").trim())?String(raw.confidence).trim():"낮음",
    emotion:String(raw?.signal||"").trim(),
    flow:String(raw?.signal||"").trim(),
    strategy:String(raw?.action||"").trim(),
    caution:String(raw?.caution||"").trim(),
    dontSend:String(raw?.dontSend||"").trim(),
    advice:String(raw?.action||"").trim(),
    nextAction:String(raw?.action||"").trim(),
    replies:[]
  };
  const list=Array.isArray(raw?.replies)?raw.replies:[];
  out.replies=list.slice(0,2).map((x,i)=>sanitizeReplyObject(x,selectedSituation,["가장 자연스러운 답장","다른 느낌의 답장"][i]||"추천"));
  if(!out.meaning||!out.strategy||!out.caution||out.replies.length<2) throw new Error("빠른 답장 분석 결과가 불완전합니다.");
  out=applyAnalysisPolicyGuards(out,reqBody||{},isDetail);
  if(Array.isArray(out.replies)) out.replies=out.replies.slice(0,2);
  if(isDetail && !/^(높음|중간|낮음)$/.test(String(out.confidence||"").trim())) out.confidence="낮음";
  return out;
}

'''
s=s.replace(anchor,code+anchor,1)

old_start='''async function generateAnalysisResult(reqBody){
  const directDetail=getDeterministicDetailAnalysis(reqBody||{});
  if(directDetail) return {parsed:directDetail,isDetail:true};
  const compactPro=await generateCompactProResult(reqBody||{});
  if(compactPro) return {parsed:compactPro,isDetail:true};
  const directQuick=getDeterministicQuickAnalysis(reqBody||{});
  if(directQuick) return {parsed:directQuick,isDetail:false};
  const {content,isDetail,selectedSituation}=buildAnalysisContent(reqBody||{});'''
new_start='''async function generateAnalysisResult(reqBody){
  const directDetail=getDeterministicDetailAnalysis(reqBody||{});
  if(directDetail) return {parsed:directDetail,isDetail:true};
  const compactPro=await generateCompactProResult(reqBody||{});
  if(compactPro) return {parsed:compactPro,isDetail:true};
  const directQuick=getDeterministicQuickAnalysis(reqBody||{});
  if(directQuick) return {parsed:directQuick,isDetail:false};
  const fastReply=await generateCompactReplyAnalysis(reqBody||{});
  if(fastReply) return {parsed:fastReply,isDetail:String(reqBody?.mode||"")==="detail"};
  const {content,isDetail,selectedSituation}=buildAnalysisContent(reqBody||{});'''
if old_start not in s: raise SystemExit('generateAnalysisResult start missing')
s=s.replace(old_start,new_start,1)

p.write_text(s,encoding='utf-8')
