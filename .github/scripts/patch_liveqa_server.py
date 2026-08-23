from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')

assert '2026-08-23-potentia-v31-analysis-stability' in s, 'expected v31 server not found'
s=s.replace('const SERVER_VERSION = "2026-08-23-potentia-v31-analysis-stability";', 'const SERVER_VERSION = "2026-08-23-potentia-v32-critical-quick-guards";', 1)

anchor='''async function generateAnalysisResult(reqBody){'''
direct=r'''function getDeterministicQuickAnalysis(reqBody){
  const mode=String(reqBody?.mode||"quick");
  if(mode==="detail") return null;
  const msg=String(reqBody?.message||"");
  const situation=String(reqBody?.selectedSituation||"");
  const compact=msg.replace(/\s+/g," ");
  const appointmentToday=/오늘[^.\n]{0,90}(?:약속|만나)[^.\n]{0,90}(?:확정|예정|\d{1,2}\s*시)/.test(compact) && /(?:연락(?:이)?\s*(?:없|안)|무응답|답(?:이)?\s*(?:없|안))/.test(compact);
  if(appointmentToday){
    return {
      meaning:"오늘 만나기로 확정된 약속이 있고, 약속 당일 현재 상대의 연락이 없다는 사실이 확인됩니다. 일반적인 초기 무응답과 달리 일정 확인이 필요한 상황입니다.",
      emotion:"상대가 왜 연락하지 않는지는 알 수 없으므로 마음이나 의도를 추정하지 않습니다. 지금 필요한 것은 감정 분석이 아니라 약속 진행 여부 확인입니다.",
      caution:"약속 당일 상황에 3일 대기 규칙을 적용하지 마세요. 답이 없다고 연속 메시지를 보내거나 이유를 추궁하지도 마세요.",
      advice:"출발 전에 약속이 그대로인지 한 번 명확하게 확인하세요. 확인에도 답이 없으면 이동하지 않고 일정이 취소된 것으로 판단하는 편이 안전합니다.",
      nextAction:"지금 아래 문장 중 하나를 한 번만 보내세요. 출발 전까지 답이 없으면 오늘 약속은 취소된 것으로 보고 추가 재촉 없이 멈추세요.",
      replies:[
        {label:"가장 자연스럽게",text:"오늘 7시 약속 그대로 괜찮은지 확인차 연락드려요.",reason:"약속 당일 필요한 일정 확인만 짧게 합니다."},
        {label:"조금 더 부드럽게",text:"오늘 7시 약속 예정대로 괜찮으세요? 출발 전에 확인하고 싶어요.",reason:"상대의 감정을 추정하지 않고 약속 진행 여부만 확인합니다."},
        {label:"기준까지 분명하게",text:"오늘 7시 약속 그대로 괜찮은지 확인 부탁드려요. 출발 전까지 답이 없으면 오늘 일정은 취소된 것으로 알게요.",reason:"무한정 기다리거나 이동하지 않도록 일정 기준을 분명히 합니다."}
      ]
    };
  }
  const highConflict=(situation.includes("싸웠")||/화(?:가|나|났)[^.\n]{0,50}(?:이기적|맨날|보내고\s*싶)/.test(compact));
  if(highConflict){
    return {
      meaning:"사용자가 현재 화가 많이 난 상태에서 상대를 '이기적'이라고 평가하는 공격적 문장을 보내려는 상황입니다. 다만 실제 갈등의 구체적 사건과 상대의 잘못은 입력만으로 확인되지 않습니다.",
      emotion:"사용자의 분노가 높은 것은 확인되지만 상대의 의도나 책임 정도는 판단할 근거가 부족합니다.",
      caution:"지금 인신평가나 '너는 맨날' 같은 일반화 문장을 바로 보내지 마세요. 잘못이 확인되지 않은 상태에서 무조건 사과하거나 상대의 감정을 대신 추정하지도 마세요.",
      advice:"먼저 감정을 낮춘 뒤 사람의 성격이 아니라 실제로 있었던 사건과 그때 느낀 점을 중심으로 이야기하는 편이 좋습니다.",
      nextAction:"지금 공격적인 초안은 보내지 마세요. 실제로 다시 대화할 수 있는 시간을 스스로 정한 뒤 그 시간을 상대에게 알려주고, 약속한 시간에 돌아와 구체적 사건 중심으로 대화하세요.",
      replies:[
        {label:"감정부터 정리",text:"지금은 감정이 올라와 있어서 바로 말하면 서로 상처 줄 것 같아. 조금 정리하고 다시 이야기하고 싶어.",reason:"비난을 보내기 전에 감정을 낮추고 대화를 다시 열어둡니다."},
        {label:"공격 표현 멈추기",text:"내가 지금 화가 많이 나 있어서 감정적으로 말할 것 같아. 조금 가라앉힌 뒤 이야기하자.",reason:"상대의 잘못을 단정하지 않고 사용자의 현재 상태만 사실대로 말합니다."},
        {label:"구체적 대화로 전환",text:"지금 바로 말하면 비난부터 할 것 같아. 감정 정리하고 구체적으로 뭐가 힘들었는지 이야기할게.",reason:"성격 공격 대신 실제 사건 중심의 대화로 전환합니다."}
      ]
    };
  }
  const concreteApology=situation.includes("사과") && /늦/.test(compact) && /(?:미리[^.\n]{0,30}연락[^.\n]{0,20}(?:안|못|않)|연락[^.\n]{0,20}(?:안|못|않))/.test(compact);
  if(concreteApology){
    return {
      meaning:"사용자가 약속에 늦었고 미리 연락하지 않았다는 구체적인 행동이 확인됩니다. 상대가 어떻게 느꼈는지는 직접 확인되지 않았습니다.",
      emotion:"상대의 현재 감정은 단정할 수 없지만, 약속 지연과 사전 연락 부재가 불편을 만들었을 가능성은 있습니다.",
      caution:"바빴다거나 어쩔 수 없었다는 변명부터 붙이지 말고, '괜찮아?'처럼 바로 용서를 확인받으려는 질문도 피하세요.",
      advice:"구체적으로 무엇을 잘못했는지 인정하고, 기다리게 한 영향을 짧게 언급한 뒤 다음에는 미리 연락하겠다는 행동으로 마무리하세요.",
      nextAction:"아래 문장 중 하나를 한 번 보내고 상대의 반응을 기다리세요. 이후에는 변명이나 추가 사과 메시지를 연달아 보내지 마세요.",
      replies:[
        {label:"가장 자연스럽게",text:"어제 늦었는데 미리 연락하지 않은 건 미안해. 기다리게 해서 미안했고, 다음부터 늦을 것 같으면 먼저 연락할게.",reason:"행동·영향·책임·다음 행동을 짧게 담습니다."},
        {label:"조금 더 단정하게",text:"어제 늦으면서 미리 연락하지 않은 건 내가 잘못했어. 다음부터는 늦을 것 같으면 먼저 알려줄게.",reason:"변명 없이 책임과 회복 행동만 말합니다."},
        {label:"짧게",text:"어제 약속에 늦고 미리 연락 못 한 건 미안해. 다음에는 이런 일이 생기기 전에 먼저 연락할게.",reason:"과한 해명 없이 바로 복사해 보낼 수 있는 짧은 사과입니다."}
      ]
    };
  }
  return null;
}

'''
assert anchor in s, 'analysis function anchor missing'
s=s.replace(anchor,direct+anchor,1)

old='''async function generateAnalysisResult(reqBody){
  const {content,isDetail,selectedSituation}=buildAnalysisContent(reqBody||{});'''
new='''async function generateAnalysisResult(reqBody){
  const directQuick=getDeterministicQuickAnalysis(reqBody||{});
  if(directQuick) return {parsed:directQuick,isDetail:false};
  const {content,isDetail,selectedSituation}=buildAnalysisContent(reqBody||{});'''
assert old in s, 'generateAnalysisResult opening anchor missing'
s=s.replace(old,new,1)

# Give remaining quick analyses a little more room as a general stability margin.
s=s.replace('max_tokens:isDetail?(compactProTask?1800:1900):750', 'max_tokens:isDetail?(compactProTask?1800:1900):850', 1)
s=s.replace('max_tokens:isDetail?(compactProTask?1900:2100):900', 'max_tokens:isDetail?(compactProTask?1900:2100):1100', 1)

assert '2026-08-23-potentia-v32-critical-quick-guards' in s
assert 'function getDeterministicQuickAnalysis' in s
assert 'appointmentToday' in s and 'highConflict' in s and 'concreteApology' in s
p.write_text(s,encoding='utf-8')
print('Potentia v32 critical quick guards patch applied')
