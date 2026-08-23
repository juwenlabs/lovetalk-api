from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')
old='2026-08-23-potentia-v49-priority-boundaries'
new='2026-08-23-potentia-v50-detail-completion-resilience'
assert old in s, 'v49 base version missing'
s=s.replace(f'const SERVER_VERSION = "{old}";', f'const SERVER_VERSION = "{new}";', 1)

old_request='''  const compactInstruction={type:"text",text:"\\n[출력 길이 제한] 이 작업은 장기 저장/요약용입니다. 모든 필수 섹션과 reply1~3은 유지하되 각 섹션은 핵심 1~2문장만 쓰고 전체를 약 1700자 안에 끝내세요. 반복 설명은 금지하고 nextAction까지 반드시 완결하세요."};
  const requestContent=compactProTask ? (Array.isArray(content)?[...content,compactInstruction]:String(content)+compactInstruction.text) : content;
  let ai=await anthropic.messages.create({model,system:POTENTIA_SYSTEM_PROMPT,max_tokens:isDetail?(compactProTask?1800:1900):850,messages:[{role:"user",content:requestContent}]});'''
new_request='''  const compactInstruction={type:"text",text:"\\n[출력 길이 제한] 이 작업은 장기 저장/요약용입니다. 모든 필수 섹션과 reply1~3은 유지하되 각 섹션은 핵심 1~2문장만 쓰고 전체를 약 1700자 안에 끝내세요. 반복 설명은 금지하고 nextAction까지 반드시 완결하세요."};
  const detailInstruction={type:"text",text:"\\n[상세분석 출력 길이] 모든 필수 섹션과 reply1~3을 유지하되 각 섹션은 핵심 1~2문장, 각 추천문장은 1문장으로 쓰고 전체를 약 1900자 안에 끝내세요. 입력에 없는 감정·일정·사실을 만들지 말고 nextAction까지 반드시 완결하세요."};
  const requestContent=compactProTask
    ? (Array.isArray(content)?[...content,compactInstruction]:String(content)+compactInstruction.text)
    : (isDetail ? (Array.isArray(content)?[...content,detailInstruction]:String(content)+detailInstruction.text) : content);
  let ai=await anthropic.messages.create({model,system:POTENTIA_SYSTEM_PROMPT,max_tokens:isDetail?(compactProTask?1800:2100):850,messages:[{role:"user",content:requestContent}]});'''
assert old_request in s, 'detail request block missing'
s=s.replace(old_request,new_request,1)

old_retry='''    ai=await anthropic.messages.create({model,system:POTENTIA_SYSTEM_PROMPT,max_tokens:isDetail?(compactProTask?1900:2100):1100,messages:[{role:"user",content:retryContent}]});'''
new_retry='''    ai=await anthropic.messages.create({model,system:POTENTIA_SYSTEM_PROMPT,max_tokens:isDetail?(compactProTask?1900:2300):1100,messages:[{role:"user",content:retryContent}]});'''
assert old_retry in s, 'detail retry token block missing'
s=s.replace(old_retry,new_retry,1)

old_tail='''  if(ai.stop_reason==="max_tokens" && !analysisEndingLooksComplete(parsed)){
    if(compactProTask && validAnalysisResult(parsed,isDetail)){
      parsed.nextAction=isMemoryTask
        ? "확인된 사실과 최소 2회 이상 반복 관찰된 행동 패턴만 장기 기억에 저장하고, 감정 가설·호감 추정·조언은 저장하지 마세요."
        : "확인된 행동 변화만 월간 기록으로 남기고, 다음 달에는 상대 참여와 사용자 과투자 변화를 다시 비교하세요.";
    }else throw new Error("AI 상세 분석이 끝까지 생성되지 않아 다시 시도해 주세요.");
  }'''
new_tail='''  if(ai.stop_reason==="max_tokens" && !analysisEndingLooksComplete(parsed)){
    const hasDetailCore=!!(isDetail && parsed && parsed.meaning && parsed.emotion && parsed.flow && parsed.strategy && parsed.caution && parsed.advice && Array.isArray(parsed.replies) && parsed.replies.length>=3);
    if(compactProTask && validAnalysisResult(parsed,isDetail)){
      parsed.nextAction=isMemoryTask
        ? "확인된 사실과 최소 2회 이상 반복 관찰된 행동 패턴만 장기 기억에 저장하고, 감정 가설·호감 추정·조언은 저장하지 마세요."
        : "확인된 행동 변화만 월간 기록으로 남기고, 다음 달에는 상대 참여와 사용자 과투자 변화를 다시 비교하세요.";
    }else if(hasDetailCore){
      parsed.nextAction="확인된 사실과 상대의 실제 참여만 기준으로 다음 행동을 한 단계씩 결정하세요. 입력에 없는 감정·일정은 만들지 말고, 상대 참여가 불분명하면 사용자의 연락이나 제안을 더 늘리지 마세요.";
    }else throw new Error("AI 상세 분석이 끝까지 생성되지 않아 다시 시도해 주세요.");
  }'''
assert old_tail in s, 'detail max-token fallback block missing'
s=s.replace(old_tail,new_tail,1)

p.write_text(s,encoding='utf-8')
print('patched',new)
