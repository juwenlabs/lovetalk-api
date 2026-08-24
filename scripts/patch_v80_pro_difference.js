const fs=require("fs");
const path=require("path");
const serverPath=path.join(process.cwd(),"server.js");
let src=fs.readFileSync(serverPath,"utf8");

if(src.includes("2026-08-24-potentia-v80-pro-differentiation")){
  console.log("v80 PRO differentiation already applied");
}else{
  if(!src.includes("2026-08-24-potentia-v79-reply-quality-gate")){
    require("./patch_v79_reply_quality_gate_fixed.js");
    src=fs.readFileSync(serverPath,"utf8");
  }

  src=src.replace(/const SERVER_VERSION = "[^"]+";/,'const SERVER_VERSION = "2026-08-24-potentia-v80-pro-differentiation";');

  const marker='async function applyReplyQualityGate(payload,reqBody,pathName){';
  const helper=String.raw`
async function enhanceProReplySet(replies,reqBody,pathName){
  const context=[
    reqBody?.message,
    reqBody?.text,
    reqBody?.conversation,
    reqBody?.selectedSituation,
    reqBody?.relation,
    reqBody?.starterGoal,
    reqBody?.goal
  ].filter(Boolean).map(String).join("\n");
  const profile=reqBody?.profile&&typeof reqBody.profile==="object"?reqBody.profile:{};
  const recent=reqBody?.recentMemory&&typeof reqBody.recentMemory==="object"?reqBody.recentMemory:reqBody?.recentMemory||"";
  const isStarter=String(pathName||"").includes("starter");
  const system=isStarter
    ? "너는 썸톡 AI PRO의 선톡 전략 코치다. 무료 버전보다 한 단계 깊게 관계 단계, 상대의 실제 참여 신호, 사용자의 목적, 저장된 프로필과 최근 기억을 함께 고려한다. 단, 입력에 없는 사실·감정·일정·취향·경험은 절대 만들지 않는다. 세 문장은 1) 가장 자연스러운 기본안 2) 관계를 한 단계 진전시키는 안 3) 부담을 최소화하며 반응을 확인하는 안으로 역할이 뚜렷하게 달라야 한다. 단순 말투 바꾸기만 하지 말고 접근 전략 자체를 다르게 한다. 실제 한국 카카오톡에서 바로 보낼 수 있게 짧고 자연스럽게 쓴다. JSON 외 텍스트는 출력하지 않는다."
    : "너는 썸톡 AI PRO의 답장 전략 코치다. 무료 버전보다 한 단계 깊게 상대가 방금 한 말의 기능, 최근 대화 흐름, 관계 단계, 사용자의 목적, 저장된 프로필과 최근 기억을 함께 고려한다. 단, 입력에 없는 사실·감정·일정·취향·경험은 절대 만들지 않는다. 세 문장은 1) 가장 자연스럽게 이어가는 안 2) 온도를 조금 높이는 안 3) 여유 있게 상대 반응을 확인하는 안으로 역할이 뚜렷하게 달라야 한다. 단순 어미나 이모티콘만 바꾸지 말고 대화 전략 자체를 다르게 한다. 실제 한국 카카오톡에서 바로 보낼 수 있게 짧고 자연스럽게 쓴다. JSON 외 텍스트는 출력하지 않는다.";
  const prompt=JSON.stringify({
    task:isStarter?"PRO 선톡 3개를 전략적으로 다시 작성하세요.":"PRO 답장 3개를 전략적으로 다시 작성하세요.",
    context:String(context||"").slice(0,9000),
    profile,
    recentMemory:recent,
    currentReplies:(Array.isArray(replies)?replies:[]).slice(0,3),
    rules:[
      "확인되지 않은 사용자 일정·감정·경험·취향을 만들지 않는다",
      "세 답장은 표현만 바꾼 중복이 아니라 목적과 접근법이 달라야 한다",
      "상대의 질문이나 마지막 메시지에 직접 반응한다",
      "차단·연락중단·명확한 거절은 우회하지 않는다"
    ],
    output:{replies:isStarter?[
      {label:"가장 자연스러운 접근",text:"짧은 선톡",reason:"왜 지금 관계 흐름에 맞는지"},
      {label:"관계 진전형",text:"짧은 선톡",reason:"어떤 반응을 확인하려는지"},
      {label:"부담 최소화형",text:"짧은 선톡",reason:"왜 부담이 낮은지"}
    ]:[
      {label:"가장 자연스러운 답장",text:"짧은 답장",reason:"왜 현재 흐름에 맞는지"},
      {label:"온도 높이기",text:"짧은 답장",reason:"관계를 어떻게 한 단계 진전시키는지"},
      {label:"여유 있게",text:"짧은 답장",reason:"상대 반응을 어떻게 확인하는지"}
    ]}
  });
  const ai=await openAICompatCreate({system,max_tokens:650,messages:[{role:"user",content:prompt}]});
  const parsed=parseQualityRepairJson(ai?.content?.[0]?.text||"");
  if(!Array.isArray(parsed?.replies)||parsed.replies.length<3) throw new Error("PRO enhancement returned fewer than 3 replies");
  return parsed.replies.slice(0,3).map((x,i)=>({
    label:String(x?.label|| (isStarter?["가장 자연스러운 접근","관계 진전형","부담 최소화형"][i]:["가장 자연스러운 답장","온도 높이기","여유 있게"][i])),
    text:String(x?.text||"").trim(),
    reason:String(x?.reason||"").trim()
  }));
}
function proScheduleFallbackReplies(context){
  const polite=/(?:뭐\s*하세요|뭐\s*하실|시간\s*되세요|괜찮으세요)/.test(String(context||""));
  return polite?[
    {label:"가장 자연스러운 답장",text:"왜요, 무슨 일 있으세요?",reason:"일정을 지어내지 않고 상대의 용건을 먼저 확인합니다."},
    {label:"온도 높이기",text:"왜 물어보세요? 혹시 같이 뭐 하려고요?",reason:"가능 여부를 단정하지 않으면서 상대의 제안 의도를 조금 더 직접 확인합니다."},
    {label:"여유 있게",text:"무슨 일인지 먼저 들어볼게요.",reason:"사용자 일정을 공개하지 않고 상대가 먼저 구체적으로 말하게 합니다."}
  ]:[
    {label:"가장 자연스러운 답장",text:"왜, 무슨 일 있어?",reason:"일정을 지어내지 않고 상대의 용건을 먼저 확인합니다."},
    {label:"온도 높이기",text:"왜? 혹시 같이 뭐 하려고?",reason:"가능 여부를 단정하지 않으면서 상대의 제안 의도를 조금 더 직접 확인합니다."},
    {label:"여유 있게",text:"일단 무슨 일인지 들어볼게.",reason:"사용자 일정을 만들지 않고 상대가 먼저 구체적으로 말하게 합니다."}
  ];
}
`;
  if(!src.includes(marker)) throw new Error("v80 applyReplyQualityGate marker not found");
  src=src.replace(marker,helper+"\n"+marker);

  const oldContext='  const context=[reqBody?.message,reqBody?.text,reqBody?.conversation,reqBody?.selectedSituation,reqBody?.relation,reqBody?.starterGoal,reqBody?.goal,reqBody?.recentContext].filter(Boolean).map(String).join("\\n");\n  if(directScheduleQuestion(context) && !userScheduleWasProvided(context)) return {...payload,replies:scheduleFallbackReplies(context),qualityGate:"schedule-grounding",serverVersion:SERVER_VERSION};';
  const newContext='  const context=[reqBody?.message,reqBody?.text,reqBody?.conversation,reqBody?.selectedSituation,reqBody?.relation,reqBody?.starterGoal,reqBody?.goal,reqBody?.recentContext].filter(Boolean).map(String).join("\\n");\n  const isPro=!!(reqBody?.advanced || reqBody?.replyDetailMode);\n  if(directScheduleQuestion(context) && !userScheduleWasProvided(context)) return {...payload,replies:isPro?proScheduleFallbackReplies(context):scheduleFallbackReplies(context),qualityGate:isPro?"pro-schedule-grounding":"schedule-grounding",proEnhanced:isPro,serverVersion:SERVER_VERSION};';
  if(!src.includes(oldContext)) throw new Error("v80 context marker not found");
  src=src.replace(oldContext,newContext);

  const oldPass='  const issues=collectReplyQualityIssues(payload.replies,context);\n  if(!issues.length) return {...payload,qualityGate:"pass",serverVersion:SERVER_VERSION};';
  const newPass='  const issues=collectReplyQualityIssues(payload.replies,context);\n  if(!issues.length){\n    if(isPro){\n      try{\n        const proReplies=await enhanceProReplySet(payload.replies,reqBody,pathName);\n        const proIssues=collectReplyQualityIssues(proReplies,context);\n        if(!proIssues.length) return {...payload,replies:proReplies,qualityGate:"pro-enhanced",proEnhanced:true,serverVersion:SERVER_VERSION};\n        console.warn("PRO 재작성 품질 재검수 미통과:",proIssues,"path=",pathName);\n      }catch(error){console.error("PRO 전략형 재작성 실패:",error?.message||error,"path=",pathName);}\n    }\n    return {...payload,qualityGate:"pass",proEnhanced:false,serverVersion:SERVER_VERSION};\n  }';
  if(!src.includes(oldPass)) throw new Error("v80 pass marker not found");
  src=src.replace(oldPass,newPass);

  const oldRepaired='    if(!remaining.length) return {...payload,replies:repaired,qualityGate:"repaired",qualityIssues:issues,serverVersion:SERVER_VERSION};';
  const newRepaired='    if(!remaining.length){\n      if(isPro){\n        try{\n          const proReplies=await enhanceProReplySet(repaired,reqBody,pathName);\n          const proIssues=collectReplyQualityIssues(proReplies,context);\n          if(!proIssues.length) return {...payload,replies:proReplies,qualityGate:"pro-repaired-enhanced",qualityIssues:issues,proEnhanced:true,serverVersion:SERVER_VERSION};\n        }catch(error){console.error("PRO 보정 후 전략형 재작성 실패:",error?.message||error,"path=",pathName);}\n      }\n      return {...payload,replies:repaired,qualityGate:"repaired",qualityIssues:issues,proEnhanced:false,serverVersion:SERVER_VERSION};\n    }';
  if(!src.includes(oldRepaired)) throw new Error("v80 repaired marker not found");
  src=src.replace(oldRepaired,newRepaired);

  fs.writeFileSync(serverPath,src,"utf8");
  console.log("Applied Potentia v80 PRO differentiation");
}
