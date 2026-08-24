const fs = require("fs");
const path = require("path");

const serverPath = path.join(process.cwd(), "server.js");
let src = fs.readFileSync(serverPath, "utf8");

if (src.includes("2026-08-24-potentia-v79-reply-quality-gate")) {
  console.log("v79 reply quality gate already applied");
  process.exit(0);
}

src = src.replace(
  /const SERVER_VERSION = \"[^\"]+\";/,
  'const SERVER_VERSION = "2026-08-24-potentia-v79-reply-quality-gate";'
);

const middlewareMarker = 'app.use(express.json({ limit: "35mb" }));';
const middleware = `\n\n// v79: suspicious reply payloads are repaired only when needed.\napp.use((req,res,next)=>{\n  const originalJson=res.json.bind(res);\n  res.json=function(payload){\n    const send=(value)=>originalJson(value);\n    if(!payload || !Array.isArray(payload.replies) || payload.replies.length===0) return send(payload);\n    Promise.resolve(applyReplyQualityGate(payload,req.body||{},req.path||\"\"))\n      .then(send)\n      .catch((error)=>{\n        console.error(\"답장 품질 필터 오류:\",error?.message||error);\n        send(payload);\n      });\n    return res;\n  };\n  next();\n});`;

if (!src.includes(middlewareMarker)) throw new Error("middleware marker not found");
src = src.replace(middlewareMarker, middlewareMarker + middleware);

const functionMarker = 'const POTENTIA_SYSTEM_PROMPT = `';
const qualityFunctions = `
function normalizeReplyForCompare(text){
  return String(text||\"\").toLowerCase().replace(/[^0-9a-z가-힣]/g,\"\");
}

function bigramSet(text){
  const s=normalizeReplyForCompare(text);
  const out=new Set();
  if(s.length<2){if(s)out.add(s);return out;}
  for(let i=0;i<s.length-1;i++) out.add(s.slice(i,i+2));
  return out;
}

function replySimilarity(a,b){
  const A=bigramSet(a),B=bigramSet(b);
  if(!A.size||!B.size) return 0;
  let inter=0;
  for(const x of A) if(B.has(x)) inter++;
  return inter/(A.size+B.size-inter);
}

function userScheduleWasProvided(context){
  return /(?:나는|내가|저는|저도|나도|사용자)[^.?!？!\\n]{0,120}(?:일정|약속|출근|퇴근|회사|근무|일\\s*해|쉬어|쉰|집에|가능|시간\\s*돼|시간\\s*안|안\\s*돼|어려워|어렵|바빠|한가)/.test(String(context||\"\"));
}

function directScheduleQuestion(context){
  return /(?:오늘|내일|주말|이번\\s*주말)[^.?？!\\n]{0,20}(?:뭐\\s*(?:해|하니|하냐|하세요|하실|할\\s*거)|시간\\s*(?:돼|되니|되세요|괜찮))/.test(String(context||\"\"));
}

function scheduleFallbackReplies(context){
  const polite=/(?:뭐\\s*하세요|뭐\\s*하실|시간\\s*되세요|괜찮으세요)/.test(String(context||\"\"));
  return polite?[
    {label:\"자연스럽게\",text:\"왜요, 무슨 일 있어요?\",reason:\"사용자의 일정을 만들지 않고 상대가 물은 이유만 확인합니다.\"},
    {label:\"조금 더 가볍게\",text:\"왜 물어보세요? 무슨 일 있으세요?\",reason:\"일정 가능 여부를 추정하지 않고 용건을 먼저 확인합니다.\"},
    {label:\"조금 더 여유 있게\",text:\"혹시 뭐 하려고 물어보신 거예요?\",reason:\"거짓 일정 없이 상대의 의도를 자연스럽게 확인합니다.\"}
  ]:[
    {label:\"자연스럽게\",text:\"왜, 무슨 일 있어?\",reason:\"사용자의 일정을 만들지 않고 상대가 물은 이유만 확인합니다.\"},
    {label:\"조금 더 가볍게\",text:\"왜? 뭐 하려고?\",reason:\"일정 가능 여부를 추정하지 않고 상대의 의도를 확인합니다.\"},
    {label:\"조금 더 여유 있게\",text:\"왜 물어봐? 무슨 일 있어?\",reason:\"거짓 일정 없이 질문에 자연스럽게 반응합니다.\"}
  ];
}

function hasGroundingForClaim(context,kind){
  const c=String(context||\"\");
  const map={
    busy:/(?:나는|내가|저는|저도|나도|사용자)[^.\\n]{0,100}(?:바빠|바쁠|시간\\s*없|일정|근무|출근|회사)/,
    home:/(?:나는|내가|저는|저도|나도|사용자)[^.\\n]{0,100}(?:집에|집에서|귀가)/,
    rest:/(?:나는|내가|저는|저도|나도|사용자)[^.\\n]{0,100}(?:쉬어|쉬고|쉰|휴식)/,
    noPlan:/(?:나는|내가|저는|저도|나도|사용자)[^.\\n]{0,100}(?:약속\\s*없|일정\\s*없|별\\s*일\\s*없|계획\\s*없)/,
    commonLike:/(?:나는|내가|저는|저도|나도|사용자)[^.\\n]{0,100}(?:좋아|즐겨|자주)/,
    experience:/(?:나는|내가|저는|저도|나도|사용자)[^.\\n]{0,100}(?:가봤|해봤|먹어봤|본\\s*적|경험)/,
    emotion:/(?:나는|내가|저는|저도|나도|사용자)[^.\\n]{0,100}(?:생각났|기대|설레|보고\\s*싶)/
  };
  return map[kind]?map[kind].test(c):false;
}

function collectReplyQualityIssues(replies,context){
  const issues=[];
  const list=Array.isArray(replies)?replies:[];
  const texts=list.map(x=>String(x?.text||\"\").trim()).filter(Boolean);
  if(texts.length<3) issues.push(\"추천 답장이 3개가 아님\");

  for(let i=0;i<texts.length;i++){
    const t=texts[i];
    if(t.length>140) issues.push(\`답장 \\${i+1}이 너무 김\`);
    if(/(?:상대방|사용자는|AI|분석 결과|추천 답장)/.test(t)) issues.push(\`답장 \\${i+1}에 메타 표현 포함\`);
    if(/아직\\s*안\\s*봤는데|그냥\\s*평범한\\s*것\\s*같은데/.test(t)) issues.push(\`답장 \\${i+1}이 질문 맥락과 어색함\`);
    if(/(?:바빠|바쁠|시간\\s*없|출근|퇴근|회사\\s*가|근무)/.test(t) && !hasGroundingForClaim(context,\"busy\")) issues.push(\`답장 \\${i+1}이 사용자 바쁨/근무를 지어냄\`);
    if(/(?:집에\\s*있|집에서\\s*있)/.test(t) && !hasGroundingForClaim(context,\"home\")) issues.push(\`답장 \\${i+1}이 사용자 위치를 지어냄\`);
    if(/(?:쉬고\\s*있|쉴\\s*거|쉬려고|쉬는\\s*중)/.test(t) && !hasGroundingForClaim(context,\"rest\")) issues.push(\`답장 \\${i+1}이 사용자 휴식 일정을 지어냄\`);
    if(/(?:약속|일정|계획)[^.!?]{0,10}(?:없|없어|없는데)/.test(t) && !hasGroundingForClaim(context,\"noPlan\")) issues.push(\`답장 \\${i+1}이 약속 없음 사실을 지어냄\`);
    if(/(?:나도|저도)[^.!?]{0,20}(?:좋아|자주|즐겨)/.test(t) && !hasGroundingForClaim(context,\"commonLike\")) issues.push(\`답장 \\${i+1}이 공통 취향을 지어냄\`);
    if(/(?:나도|저도)?[^.!?]{0,20}(?:가봤|해봤|먹어봤)/.test(t) && !hasGroundingForClaim(context,\"experience\")) issues.push(\`답장 \\${i+1}이 사용자 경험을 지어냄\`);
    if(/(?:생각났|기대돼|기대되|설레|보고\\s*싶었)/.test(t) && !hasGroundingForClaim(context,\"emotion\")) issues.push(\`답장 \\${i+1}이 사용자 감정을 지어냄\`);
    if(/(?:그때|전에|아까)[^.!?]{0,24}(?:말한|얘기한|이야기한)/.test(t) && !/(?:그때|전에|아까)[^.\\n]{0,50}(?:말|얘기|이야기)/.test(String(context||\"\"))) issues.push(\`답장 \\${i+1}이 없는 과거 대화를 만듦\`);
  }

  for(let i=0;i<texts.length;i++){
    for(let j=i+1;j<texts.length;j++){
      if(replySimilarity(texts[i],texts[j])>=0.72) issues.push(\`답장 \\${i+1}과 \\${j+1}이 너무 비슷함\`);
    }
  }
  return [...new Set(issues)];
}

function parseQualityRepairJson(text){
  const cleaned=String(text||\"\").replace(/^\\s*\\`\\`\\`json/i,\"\").replace(/^\\s*\\`\\`\\`/i,\"\").replace(/\\`\\`\\`\\s*$/i,\"\").trim();
  const a=cleaned.indexOf(\"{\"),b=cleaned.lastIndexOf(\"}\");
  if(a<0||b<=a) throw new Error(\"quality repair JSON not found\");
  return JSON.parse(cleaned.slice(a,b+1));
}

async function repairReplySet(replies,context,issues){
  const system=\`너는 썸톡 AI의 최종 답장 품질 검수기다. 이미 생성된 답장 중 부자연스럽거나 사실을 지어낸 부분을 고친다. 사용자가 입력하지 않은 일정, 위치, 감정, 취향, 경험, 과거 대화, 약속 여부를 절대 만들지 않는다. 상대 질문에 직접 반응하고 실제 한국 카카오톡에서 보낼 법한 짧은 문장으로 쓴다. 세 답장은 말투와 접근이 서로 분명히 달라야 한다. 차단, 연락중단, 명확한 거절 같은 경계를 약화시키지 않는다. JSON 외 텍스트는 출력하지 않는다.\`;
  const prompt=JSON.stringify({
    task:\"아래 원문 맥락만 근거로 추천 답장 3개를 다시 작성하세요. 검수 문제를 모두 제거하세요.\",
    context:String(context||\"\").slice(0,9000),
    detectedIssues:issues,
    currentReplies:(Array.isArray(replies)?replies:[]).slice(0,3),
    output:{replies:[{label:\"자연스럽게\",text:\"짧은 답장\",reason:\"짧은 이유\"},{label:\"다정하게\",text:\"짧은 답장\",reason:\"짧은 이유\"},{label:\"여유 있게\",text:\"짧은 답장\",reason:\"짧은 이유\"}]}
  });
  const ai=await openAICompatCreate({system,max_tokens:520,messages:[{role:\"user\",content:prompt}]});
  const parsed=parseQualityRepairJson(ai?.content?.[0]?.text||\"\");
  if(!Array.isArray(parsed?.replies)||parsed.replies.length<3) throw new Error(\"quality repair returned fewer than 3 replies\");
  return parsed.replies.slice(0,3).map((x,i)=>({
    label:String(x?.label||[\"자연스럽게\",\"다정하게\",\"여유 있게\"][i]),
    text:String(x?.text||\"\").trim(),
    reason:String(x?.reason||\"\").trim()
  }));
}

async function applyReplyQualityGate(payload,reqBody,pathName){
  if(!payload || !Array.isArray(payload.replies) || payload.replies.length===0) return payload;
  const context=[
    reqBody?.message,reqBody?.text,reqBody?.conversation,reqBody?.selectedSituation,
    reqBody?.relation,reqBody?.starterGoal,reqBody?.goal,reqBody?.recentContext
  ].filter(Boolean).map(String).join(\"\\n\");

  // Schedule questions with no user schedule are deterministic: never let a model invent availability.
  if(directScheduleQuestion(context) && !userScheduleWasProvided(context)){
    return {...payload,replies:scheduleFallbackReplies(context),qualityGate:\"schedule-grounding\",serverVersion:SERVER_VERSION};
  }

  const issues=collectReplyQualityIssues(payload.replies,context);
  if(!issues.length) return {...payload,qualityGate:\"pass\",serverVersion:SERVER_VERSION};

  try{
    let repaired=await repairReplySet(payload.replies,context,issues);
    let remaining=collectReplyQualityIssues(repaired,context);
    if(remaining.length){
      repaired=await repairReplySet(repaired,context,remaining);
      remaining=collectReplyQualityIssues(repaired,context);
    }
    if(!remaining.length){
      return {...payload,replies:repaired,qualityGate:\"repaired\",qualityIssues:issues,serverVersion:SERVER_VERSION};
    }
    console.warn(\"답장 품질 필터 재검수 미통과:\",remaining,\"path=\",pathName);
  }catch(error){
    console.error(\"답장 품질 재생성 실패:\",error?.message||error,\"path=\",pathName);
  }

  // If repair fails, keep current payload rather than inventing a generic off-topic fallback.
  return {...payload,qualityGate:\"repair-failed\",qualityIssues:issues,serverVersion:SERVER_VERSION};
}

`;

if (!src.includes(functionMarker)) throw new Error("function marker not found");
src = src.replace(functionMarker, qualityFunctions + functionMarker);

fs.writeFileSync(serverPath, src, "utf8");
console.log("Applied Potentia v79 reply quality gate");
