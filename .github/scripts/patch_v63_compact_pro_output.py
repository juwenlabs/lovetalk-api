from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')
old='const SERVER_VERSION = "2026-08-23-potentia-v62-fast-pro-short-system";'
new='const SERVER_VERSION = "2026-08-23-potentia-v63-compact-pro-output";'
if old not in s: raise SystemExit('v62 marker missing')
s=s.replace(old,new,1)

anchor='async function generateAnalysisResult(reqBody){\n'
if anchor not in s: raise SystemExit('generateAnalysisResult anchor missing')

code=r'''function getCompactProTask(message){
  const m=String(message||"");
  if(/\[PRO\s*고백\s*타이밍\]/.test(m)) return "confession";
  if(/\[PRO\s*데이트\s*타이밍\]/.test(m)) return "date";
  if(/\[PRO\s*위험\s*신호\s*감지\]/.test(m)) return "risk";
  if(/\[PRO\s*월간\s*관계\s*리포트\]/.test(m)) return "monthly";
  if(/\[PRO\s*상대별\s*AI\s*기억\s*강화\]/i.test(m)) return "memory";
  return "";
}

async function generateCompactProResult(reqBody){
  if(String(reqBody?.mode||"")!=="detail" || !reqBody?.advanced) return null;
  const task=getCompactProTask(reqBody?.message);
  if(!task) return null;
  const {relation,nickname,message,tone,image,images,profile,recentMemory,selectedSituation}=reqBody||{};
  const hasSingleImage=!!image?.data;
  const hasImages=Array.isArray(images)&&images.some(img=>img?.data);
  const common=buildCommonPrompt({relation,nickname,message,tone,profile,recentMemory,selectedSituation,hasImages,hasSingleImage});
  const rules={
    confession:"고백 타이밍을 판단한다. 상호 질문만으로 고백 가능이라고 보지 말고 실제 만남, 상대 선연락·대화 재개·구체적 일정 참여를 본다. 고백보다 먼저 필요한 행동이 있으면 action에 그 행동을 쓴다. 보내는 문장이 아직 필요 없으면 replies는 빈 배열이다.",
    date:"약속 제안 타이밍을 판단한다. 상대가 실제로 말한 활동·취향과 사용자가 실제로 가능하다고 밝힌 일정만 제안문에 사용한다. 사용자 가능 일정이 없으면 날짜·시간·장소를 만들지 않는다. 반복 거절과 대안 없음이면 추가 제안을 만들지 않는다.",
    risk:"안전 위험과 일반 관계 압박을 분리한다. 협박·폭력·스토킹·금전·계정/개인정보·권력관계·경계 무시는 우선한다. 애매한 재촉·짧은 답장 등을 호감이나 관심 신호로 환산하지 않는다. 위험을 과장하지 않고 확인 사실과 불확실성을 구분한다.",
    monthly:"최근 기록에 실제로 적힌 행동만 비교한다. 이전 AI 분석은 추론 후보이며 사실로 재사용하지 않는다. 선연락·질문·대화 재개·만남 제안·일정 조율·대안·무응답·거절·과투자의 반복과 변화만 요약한다. 횟수나 비율이 없으면 균형을 단정하지 않는다. replies는 반드시 빈 배열이다.",
    memory:"장기 기억 후보를 정리한다. meaning에는 사용자가 직접 말했거나 기록에서 확인되는 사실만, signal에는 최소 2회 이상 확인된 행동 패턴만 넣는다. 숨은 마음·호감 퍼센트·애착유형·성격·AI 조언은 저장 사실이 아니다. replies는 반드시 빈 배열이다."
  }[task];
  const wantsReplies=!['monthly','memory'].includes(task);
  const prompt=`${common}\n\n[PRO 전용 빠른 분석]\n${rules}\n필요한 정보만 짧게 작성하세요. 같은 뜻을 반복하지 마세요. 입력에 없는 감정·일정·장소·활동·과거 사건·미래 약속·대기 기간을 만들지 마세요. 질문은 추천문장 하나당 최대 하나입니다.\n반드시 아래 JSON 하나만 출력하세요.\n{"meaning":"핵심 판단 1~2문장","confidence":"높음|중간|낮음","signal":"확인된 상대 참여/행동과 정보 한계 1~2문장","action":"지금 할 행동 1~2문장","caution":"피할 행동 1문장","dontSend":"보내지 말아야 할 행동/문장 1문장","replies":${wantsReplies?'[{"label":"추천","text":"실제로 보낼 수 있는 짧은 문장","reason":"짧은 이유"}]':'[]'}}`;
  const content=[];
  const allowed=["image/jpeg","image/png","image/webp"];
  const imageList=Array.isArray(images)&&images.length?images.slice(0,15):(image?.data?[image]:[]);
  for(const img of imageList){
    if(!img?.data) continue;
    const mediaType=allowed.includes(img.mediaType)?img.mediaType:"image/jpeg";
    content.push({type:"image",source:{type:"base64",media_type:mediaType,data:img.data}});
  }
  content.push({type:"text",text:prompt});
  const system=`너는 썸톡 AI PRO의 빠른 관계 분석 엔진이다. 사실과 추론을 분리하고, 명확한 거절·차단·경계·안전 위험을 존중한다. 입력에 없는 사실을 만들지 않는다. 단일 신호로 호감이나 속마음을 확정하지 않는다. 사용자가 그대로 실행해도 거짓이 되지 않는 조언과 문장만 만든다. JSON 외의 텍스트는 출력하지 않는다.`;
  async function run(maxTokens,extra=""){
    const c=extra?(Array.isArray(content)?[...content,{type:"text",text:extra}]:content):content;
    const ai=await anthropic.messages.create({model:"claude-haiku-4-5",system,max_tokens:maxTokens,messages:[{role:"user",content:c}]});
    return parseClaudeJson(ai);
  }
  let raw;
  try{ raw=await run(wantsReplies?850:620); }
  catch(_){ raw=await run(wantsReplies?1050:800,"반드시 완전한 JSON 하나만 짧게 다시 출력하세요."); }
  const out={
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
  if(wantsReplies) out.replies=list.slice(0,3).map((x,i)=>sanitizeReplyObject(x,selectedSituation,["가장 자연스러운 답장","조금 더 다정한 답장","조금 더 여유 있는 답장"][i]||"추천"));
  if(task==="monthly"||task==="memory") out.replies=[];
  const placeholder=/(?:\[[^\]]+\]|○○|상대\s*메시지\s*필요|구체적\s*답장\s*필요)/;
  out.replies=out.replies.filter(x=>x?.text&&!placeholder.test(String(x.text)));
  if(!out.meaning||!out.emotion||!out.strategy||!out.caution){
    throw new Error("PRO 빠른 분석 결과가 불완전합니다.");
  }
  return out;
}

'''
s=s.replace(anchor,code+anchor,1)

old_start='''async function generateAnalysisResult(reqBody){
  const directDetail=getDeterministicDetailAnalysis(reqBody||{});
  if(directDetail) return {parsed:directDetail,isDetail:true};
  const directQuick=getDeterministicQuickAnalysis(reqBody||{});'''
new_start='''async function generateAnalysisResult(reqBody){
  const directDetail=getDeterministicDetailAnalysis(reqBody||{});
  if(directDetail) return {parsed:directDetail,isDetail:true};
  const compactPro=await generateCompactProResult(reqBody||{});
  if(compactPro) return {parsed:compactPro,isDetail:true};
  const directQuick=getDeterministicQuickAnalysis(reqBody||{});'''
if old_start not in s: raise SystemExit('generateAnalysisResult start block missing')
s=s.replace(old_start,new_start,1)

p.write_text(s,encoding='utf-8')
