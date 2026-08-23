from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')

assert '2026-08-23-potentia-v30-starter-json-recovery' in s, 'expected v30 server not found'
s=s.replace('const SERVER_VERSION = "2026-08-23-potentia-v30-starter-json-recovery";', 'const SERVER_VERSION = "2026-08-23-potentia-v31-analysis-stability";', 1)

# Two rejected meeting proposals with no alternative: do not revive contact with a generic 3-day follow-up.
anchor='''  const explicitRomanticRejection=/(?:이성적으로[^.\\n]{0,20}(?:아니|아닌)|마음이\\s*없|더\\s*만나[^.\\n]{0,20}(?:않|안)|만나고\\s*싶지)/.test(compact);'''
insert='''  const repeatedRejectionNoAlternative=/(?:두\\s*번|2\\s*번|두번)[^.\\n]{0,100}(?:거절|어렵|안\\s*된|못\\s*만나)[^.\\n]{0,160}(?:대안|다른\\s*날짜|다른날짜|날짜\\s*제안)[^.\\n]{0,80}(?:없|않|전혀)/.test(compact);
  const explicitRomanticRejection=/(?:이성적으로[^.\\n]{0,20}(?:아니|아닌)|마음이\\s*없|더\\s*만나[^.\\n]{0,20}(?:않|안)|만나고\\s*싶지)/.test(compact);
  if(repeatedRejectionNoAlternative){
    out.replies=[
      {label:"가장 자연스럽게",text:"알겠습니다.",reason:"두 번의 약속 제안이 거절되고 대안 날짜가 없으므로 추가 제안 없이 짧게 수용하는 형태입니다."},
      {label:"조금 더 정중하게",text:"알겠어요. 일정 잘 보내세요.",reason:"추가 만남 여지를 요구하지 않고 현재 대화를 정리합니다."},
      {label:"답장이 이미 끝났다면",text:"새 메시지를 보내지 마세요.",reason:"이미 마지막 거절에 답했다면 불안을 줄이기 위한 후속 연락을 더 만들 필요가 없습니다."}
    ];
    out.caution="세 번째 약속 제안, 3일 뒤 확인 연락, 다른 명분을 만든 재접근처럼 사용자의 투자만 늘리는 행동은 피하세요.";
    out.dontSend="이번 주가 안 되면 다음 주는 어때요, 며칠 뒤 다시 연락할게요처럼 약속이나 후속 연락을 계속 이어가는 문장은 보내지 마세요.";
    out.confidence="높음";
    out.advice="약속 제안이 두 번 거절됐고 상대의 대안 날짜도 없다면 여기서 멈추는 것이 맞습니다. 상대가 먼저 구체적으로 참여하기 전에는 새 약속이나 확인 연락을 만들지 마세요.";
    out.nextAction="아직 마지막 거절에 답하지 않았다면 짧게 한 번 수용하고 끝내세요. 이미 답했다면 새 메시지를 보내지 말고 상대가 먼저 구체적으로 연락하거나 일정을 제안할 때까지 추가 연락하지 마세요.";
  }'''
assert anchor in s, 'repeated rejection guard anchor missing'
s=s.replace(anchor,insert,1)

# Compact report/memory PRO tasks before generation so detail output is less likely to hit max_tokens.
old='''async function generateAnalysisResult(reqBody){
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
  parsed=applyAnalysisPolicyGuards(parsed,reqBody||{},isDetail);'''
new='''async function generateAnalysisResult(reqBody){
  const {content,isDetail,selectedSituation}=buildAnalysisContent(reqBody||{});
  const model=isDetail?"claude-sonnet-5":"claude-haiku-4-5";
  const taskMessage=String(reqBody?.message||"");
  const isMemoryTask=isDetail && /\\[PRO\\s*상대별\\s*AI\\s*기억\\s*강화\\]/.test(taskMessage);
  const isMonthlyTask=isDetail && /\\[PRO\\s*월간\\s*관계\\s*리포트\\]/.test(taskMessage);
  const compactProTask=isMemoryTask||isMonthlyTask;
  const compactInstruction={type:"text",text:"\\n[출력 길이 제한] 이 작업은 장기 저장/요약용입니다. 모든 필수 섹션과 reply1~3은 유지하되 각 섹션은 핵심 1~2문장만 쓰고 전체를 약 1700자 안에 끝내세요. 반복 설명은 금지하고 nextAction까지 반드시 완결하세요."};
  const requestContent=compactProTask ? (Array.isArray(content)?[...content,compactInstruction]:String(content)+compactInstruction.text) : content;
  let ai=await anthropic.messages.create({model,system:POTENTIA_SYSTEM_PROMPT,max_tokens:isDetail?(compactProTask?1800:1900):750,messages:[{role:"user",content:requestContent}]});
  let parsed=parseAnalysisSectionsText(getClaudeText(ai),isDetail,selectedSituation);
  if(ai.stop_reason==="max_tokens" || !validAnalysisResult(parsed,isDetail)){
    const retryInstruction={type:"text",text:`중요: 이전 출력이 너무 길거나 불완전했습니다. 위의 모든 [[section]]과 reply1~3을 빠짐없이 유지하되 전체를 ${compactProTask?"1500":"2200"}자 안으로 압축해 처음부터 다시 출력하세요. 각 섹션은 핵심만 쓰고 nextAction은 반드시 완결된 문장으로 끝내세요. 코드블록과 머리말은 금지합니다.`};
    const retryContent=Array.isArray(requestContent)?[...requestContent,retryInstruction]:String(requestContent)+retryInstruction.text;
    ai=await anthropic.messages.create({model,system:POTENTIA_SYSTEM_PROMPT,max_tokens:isDetail?(compactProTask?1900:2100):900,messages:[{role:"user",content:retryContent}]});
    parsed=parseAnalysisSectionsText(getClaudeText(ai),isDetail,selectedSituation);
  }
  if(ai.stop_reason==="max_tokens" && !analysisEndingLooksComplete(parsed)){
    if(compactProTask && validAnalysisResult(parsed,isDetail)){
      parsed.nextAction=isMemoryTask
        ? "확인된 사실과 최소 2회 이상 반복 관찰된 행동 패턴만 장기 기억에 저장하고, 감정 가설·호감 추정·조언은 저장하지 마세요."
        : "확인된 행동 변화만 월간 기록으로 남기고, 다음 달에는 상대 참여와 사용자 과투자 변화를 다시 비교하세요.";
    }else throw new Error("AI 상세 분석이 끝까지 생성되지 않아 다시 시도해 주세요.");
  }
  if(!validAnalysisResult(parsed,isDetail)) throw new Error("AI 분석 섹션을 정상적으로 파싱하지 못했습니다.");
  parsed=applyAnalysisPolicyGuards(parsed,reqBody||{},isDetail);'''
assert old in s, 'analysis generator anchor missing'
s=s.replace(old,new,1)

assert '2026-08-23-potentia-v31-analysis-stability' in s
assert 'repeatedRejectionNoAlternative' in s
assert 'compactProTask' in s
p.write_text(s,encoding='utf-8')
print('Potentia v31 analysis stability patch applied')
