from pathlib import Path

p = Path('server.js')
s = p.read_text(encoding='utf-8')
old_ver = 'const SERVER_VERSION = "2026-08-23-potentia-v53-single-question-preference-starter";'
new_ver = 'const SERVER_VERSION = "2026-08-23-potentia-v54-unavailable-boundary-priority";'
assert old_ver in s, 'v53 base version missing'
s = s.replace(old_ver, new_ver, 1)

anchor = '''function getDeterministicQuickAnalysis(reqBody){
  const mode=String(reqBody?.mode||"quick");
  if(mode==="detail") return null;
  const msg=String(reqBody?.message||"");
  const situation=String(reqBody?.selectedSituation||"");
  const relation=String(reqBody?.relation||"");
  const compact=msg.replace(/\\s+/g," ");

'''
assert anchor in s, 'quick-analysis anchor missing'
insert = r'''  // v54: explicit contact boundaries and unknown user availability outrank
  // ordinary reply generation. Do not create a personal apology after a
  // work-only boundary, and do not invent future dates or follow-up cadences
  // when the user has said the proposed time is unavailable and alternatives
  // are not yet known.
  const workOnlyContactBoundary=/상대(?:가|는)?[^.\n]{0,140}(?:(?:업무\s*외(?:에는)?)[^.\n]{0,45}(?:연락|메시지)[^.\n]{0,40}(?:하지\s*말|말아|삼가)|(?:개인|사적)(?:적으로)?\s*(?:연락|메시지)[^.\n]{0,40}(?:하지\s*말|말아|삼가))/.test(compact);
  if(workOnlyContactBoundary){
    return {
      meaning:"상대가 업무 외 개인 연락을 하지 말아 달라고 명확히 요청했습니다. 사과 목적이라도 새 개인 연락을 보내는 것은 그 경계를 다시 넘는 행동이 될 수 있습니다.",
      emotion:"상대가 왜 이런 경계를 정했는지 또는 현재 어떤 감정인지까지는 입력만으로 단정하지 않습니다.",
      caution:"'마지막으로 한 번만' 개인 메시지를 보내거나, 며칠·일주일 뒤 다시 연락하거나, 따로 만나서 설명하려고 하지 마세요.",
      advice:"개인 연락은 여기서 중단하고, 실제 업무에 필요한 내용이 있을 때만 공식적인 업무 채널과 업무 범위 안에서 소통하세요.",
      nextAction:"지금은 개인 사과 메시지도 보내지 마세요. 이후에는 실제 업무상 필요한 연락만 업무 채널에서 하세요.",
      replies:[]
    };
  }

  const counterpartTodayProposal=/(?:상대(?:가|는)?[^.\n]{0,90})?(?:오늘(?:\s*(?:저녁|밤))?)[^.\n]{0,55}(?:보자|만나자|만나|만날|볼까|보는)/.test(compact);
  const userUnavailableToday=/(?:나는|내가|저는|저도|사용자)[^.\n]{0,120}(?:야근|오늘[^.\n]{0,45}(?:못\s*만나|만나기\s*어렵|어렵|안\s*돼|불가능)|(?:못\s*만나|만나기\s*어렵))/.test(compact);
  const alternativesUnknown=/(?:다른|대안|가능한)[^.\n]{0,45}(?:날짜|일정|시간)[^.\n]{0,45}(?:아직\s*)?(?:모르|미정|정해지지|없)/.test(compact) || /(?:날짜|일정|시간)[^.\n]{0,45}(?:아직\s*)?(?:모르|미정|정해지지)/.test(compact);
  if(counterpartTodayProposal && userUnavailableToday && alternativesUnknown){
    const hasOvertime=/야근/.test(compact);
    const first=hasOvertime?"오늘은 야근이라 어려워요. 제 일정 확인하고 다시 말씀드릴게요.":"오늘은 어려워요. 제 일정 확인하고 다시 말씀드릴게요.";
    return {
      meaning:"상대가 오늘 만남을 제안했지만 사용자는 오늘은 어렵다고 밝혔고, 다른 가능한 날짜는 아직 확인되지 않았습니다.",
      emotion:"사용자가 아쉽다거나 미안하다고 말하지 않았으므로 그런 감정을 새로 만들지 않습니다. 상대의 반응도 미리 추정하지 않습니다.",
      caution:"입력에 없는 '다음 주', 특정 요일, 또는 '2~3일 뒤 다시 연락' 같은 추적 일정을 만들지 마세요. 사용자가 말하지 않은 아쉬움·미안함도 답장에 넣지 마세요.",
      advice:"오늘이 어렵다는 사실만 전달하고 실제 가능한 일정을 먼저 확인하세요. 가능한 날짜가 확인된 뒤에만 그 실제 날짜를 제안하면 됩니다.",
      nextAction:"아래 문장 중 하나로 오늘은 어렵다고 답하세요. 그 뒤에는 고정된 며칠 규칙을 만들지 말고, 사용자의 실제 가능 일정이 확인됐을 때만 다시 일정 조율을 하세요.",
      replies:[
        {label:"가장 자연스럽게",text:first,reason:"확인된 불가 사유와 일정 확인 필요만 전달합니다."},
        {label:"조금 더 정중하게",text:"오늘 저녁은 어렵습니다. 가능한 일정이 확인되면 말씀드릴게요.",reason:"대안 날짜를 임의로 만들지 않습니다."},
        {label:"간결하게",text:"오늘은 어렵고, 제 일정 확인 후 가능할 때 말씀드릴게요.",reason:"사용자가 말하지 않은 감정이나 후속 연락 시점을 만들지 않습니다."}
      ]
    };
  }

'''
s = s.replace(anchor, anchor + insert, 1)
p.write_text(s, encoding='utf-8')
