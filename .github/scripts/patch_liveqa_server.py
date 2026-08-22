from pathlib import Path
import re

p=Path('server.js')
s=p.read_text(encoding='utf-8')

assert '2026-08-23-potentia-v26-final' in s, 'expected v26 server not found'
s=s.replace('const SERVER_VERSION = "2026-08-23-potentia-v26-final";', 'const SERVER_VERSION = "2026-08-23-potentia-v27-unified-guards";', 1)

# Final deterministic policy layer. The model still writes naturally, but high-value
# manual rules are corrected after generation instead of trusting prompt adherence alone.
guard_code=r'''
function applyAnalysisPolicyGuards(parsed,reqBody,isDetail){
  const out=(parsed&&typeof parsed==="object")?parsed:{replies:[]};
  const msg=String(reqBody?.message||"");
  const situation=String(reqBody?.selectedSituation||"");
  const compact=msg.replace(/\s+/g," ");

  // Potentia no-reply rule: if the user already waited about 3 days and has not
  // sent a follow-up, the next action is ONE low-pressure check now, not 3 more days.
  const waited3=/(?:3\s*일|사흘)/.test(compact);
  const noResponse=/(?:답(?:장)?(?:이)?\s*(?:없|안\s*왔|오지)|무응답|읽씹)/.test(compact);
  const noFollow=/(?:후속[^.\n]{0,50}(?:아직|한\s*번도|안\s*보냈|보내지\s*않|없)|한\s*번도\s*보내지)/.test(compact);
  const followAlreadySent=/(?:후속|확인)[^.\n]{0,50}(?:보냈|보낸|전송)/.test(compact) && !noFollow;
  const nonUrgent=/(?:비긴급|급하지\s*않|일반적인)/.test(compact) || situation.includes("읽씹");
  if(!isDetail && waited3 && noResponse && noFollow && !followAlreadySent && nonUrgent){
    out.replies=[
      {label:"가장 자연스러운 답장",text:"요즘 바쁜 것 같네요. 여유 생기면 편하게 연락 주세요.",reason:"이미 충분히 기다린 뒤 보내는 한 번의 낮은 압력 확인이라 답을 재촉하지 않아요."},
      {label:"조금 더 따뜻한 답장",text:"일정 여유 생기면 편하게 연락 주세요.",reason:"상대가 답할 선택권을 남기면서 추가 압박을 만들지 않아요."},
      {label:"조금 더 여유 있는 답장",text:"괜찮아요. 편할 때 연락 주세요.",reason:"무응답 이유를 추궁하지 않고 한 번만 문을 열어두는 표현이에요."}
    ];
    out.caution="무응답 이유를 추궁하거나 질문을 연달아 보내지 마세요. 이번 한 번의 확인 뒤에도 답이 없으면 추가 연락을 반복하지 않는 것이 맞아요.";
    out.advice="이미 약 3일을 기다렸다면 지금은 낮은 압력의 확인 메시지를 딱 한 번 보내도 됩니다.";
    out.nextAction="지금 위 문장 중 하나를 한 번만 보내세요. 그 확인에도 다시 무응답이면 또 며칠을 세어 두 번째 후속 연락을 만들지 말고 여기서 멈추세요.";
  }

  // PRO confession: describe only participation facts that are actually present.
  // Do not invent a previous mood, shared place, or relationship progression.
  if(isDetail && /\[PRO\s*고백\s*타이밍\]/.test(msg)){
    const facts=[];
    if(/두\s*번[^.\n]{0,30}단둘이/.test(compact)) facts.push("두 번의 단둘 만남");
    if(/(?:상대도\s*)?먼저\s*연락|선연락/.test(compact)) facts.push("상대의 선연락");
    if(/다음\s*만남[^.\n]{0,40}(?:먼저\s*)?제안|만남\s*날짜[^.\n]{0,40}(?:먼저\s*)?제안/.test(compact)) facts.push("상대의 다음 만남 제안");
    if(/서로\s*질문|질문[^.\n]{0,30}자기\s*이야기/.test(compact)) facts.push("양방향 질문과 자기 이야기");
    if(facts.length){
      out.flow=`입력에서 확인되는 참여 행동은 ${facts.join(", ")}입니다. 이 밖의 이전 분위기·장소·과거 사건은 입력에 없으므로 판단 근거로 추가하지 않습니다.`;
    }
  }
  return out;
}

async function generateAnalysisResult(reqBody){
  const {content,isDetail,selectedSituation}=buildAnalysisContent(reqBody||{});
  const model=isDetail?"claude-sonnet-5":"claude-haiku-4-5";
  let ai=await anthropic.messages.create({model,system:POTENTIA_SYSTEM_PROMPT,max_tokens:isDetail?1900:750,messages:[{role:"user",content}]});
  let parsed=parseAnalysisSectionsText(getClaudeText(ai),isDetail,selectedSituation);
  if(ai.stop_reason==="max_tokens" || !validAnalysisResult(parsed,isDetail)){
    const retryContent=Array.isArray(content)?[...content,{type:"text",text:`중요: 이전 출력이 너무 길거나 불완전했습니다. 위의 모든 [[section]]과 reply1~3을 빠짐없이 유지하되 전체를 약 2200자 안으로 압축해 처음부터 다시 출력하세요. 각 섹션의 글자 제한을 지키고 nextAction은 반드시 완결된 문장으로 끝내세요. 코드블록과 머리말은 금지합니다.`}]:content;
    ai=await anthropic.messages.create({model,system:POTENTIA_SYSTEM_PROMPT,max_tokens:isDetail?2100:900,messages:[{role:"user",content:retryContent}]});
    parsed=parseAnalysisSectionsText(getClaudeText(ai),isDetail,selectedSituation);
  }
  if(ai.stop_reason==="max_tokens" && !analysisEndingLooksComplete(parsed)) throw new Error("AI 상세 분석이 끝까지 생성되지 않아 다시 시도해 주세요.");
  if(!validAnalysisResult(parsed,isDetail)) throw new Error("AI 분석 섹션을 정상적으로 파싱하지 못했습니다.");
  parsed=applyAnalysisPolicyGuards(parsed,reqBody||{},isDetail);
  return {parsed,isDetail};
}
'''

marker='app.post("/api/love-analysis", async (req,res)=>{'
assert marker in s, 'analysis endpoint marker missing'
s=s.replace(marker,guard_code+'\n'+marker,1)

# Non-streaming endpoint now uses the shared generation + deterministic policy layer.
pattern=r'app\.post\("/api/love-analysis", async \(req,res\)=>\{.*?\n\}\);\n\nfunction setStreamHeaders'
replacement='''app.post("/api/love-analysis", async (req,res)=>{
  try{
    const {parsed}=await generateAnalysisResult(req.body||{});
    res.json({...parsed,serverVersion:SERVER_VERSION});
  }catch(error){console.error("Claude API 오류:",error);res.status(error?.statusCode||500).json({error:"AI 분석을 생성하지 못했습니다.",detail:error?.message||"알 수 없는 오류",serverVersion:SERVER_VERSION});}
});

function setStreamHeaders'''
s,n=re.subn(pattern,replacement,s,count=1,flags=re.S)
assert n==1, f'non-stream endpoint replacement count={n}'

# The app actually uses the SSE endpoint for normal analysis. Buffer the AI result,
# run the SAME policy guards, then send the sections over SSE. This keeps the app
# transport unchanged while preventing stream/non-stream behavior drift.
pattern=r'app\.post\("/api/love-analysis-stream",async\(req,res\)=>\{.*?\}\);\n\napp\.post\("/api/starter-stream"'
replacement='''app.post("/api/love-analysis-stream",async(req,res)=>{
  try{
    setStreamHeaders(res);
    const {parsed,isDetail}=await generateAnalysisResult(req.body||{});
    const order=isDetail?["meaning","emotion","flow","strategy","caution","reply1","reply2","reply3","advice","nextAction"]:["meaning","emotion","caution","reply1","reply2","reply3","advice","nextAction"];
    for(const name of order){
      let value;
      if(name.startsWith("reply")){
        const idx=(Number(name.replace("reply",""))||1)-1;
        value=parsed.replies?.[idx];
      }else value=parsed[name];
      if(value!==undefined && value!==null && value!=="") sendSse(res,"section",{name,value});
    }
    sendSse(res,"done",{serverVersion:SERVER_VERSION});
    if(!res.writableEnded)res.end();
  }catch(error){console.error("스트리밍 분석 API 오류:",error);if(!res.headersSent)return res.status(error?.statusCode||500).json({error:"스트리밍 분석을 생성하지 못했습니다.",detail:error?.message||"알 수 없는 오류",serverVersion:SERVER_VERSION});if(!res.writableEnded){sendSse(res,"error",{message:error?.message||"스트리밍 오류"});res.end();}}
});

app.post("/api/starter-stream"'''
s,n=re.subn(pattern,replacement,s,count=1,flags=re.S)
assert n==1, f'stream endpoint replacement count={n}'

assert '2026-08-23-potentia-v27-unified-guards' in s
assert 'function applyAnalysisPolicyGuards' in s
assert 'async function generateAnalysisResult' in s
assert 'await generateAnalysisResult(req.body||{})' in s
p.write_text(s,encoding='utf-8')
print('Potentia v27 unified analysis guards patch applied')
