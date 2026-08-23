from pathlib import Path
p=Path('server.js')
s=p.read_text(encoding='utf-8')
assert '2026-08-23-potentia-v43-day-binding-location-safety' in s
s=s.replace('const SERVER_VERSION = "2026-08-23-potentia-v43-day-binding-location-safety";', 'const SERVER_VERSION = "2026-08-23-potentia-v44-deterministic-edges";', 1)

# 1) Consensual, time-limited location sharing: grounded deterministic response before coercion guard.
anchor='''  const liveLocationPressure='''
insert=r'''  const consensualTemporaryLocation=/(?:실시간\s*위치|위치\s*공유|위치정보)/.test(compact) && /(?:동의|합의)/.test(compact) && /(?:만날\s*때까지|도착할\s*때까지|일시적|잠깐|한시적)/.test(compact) && !/(?:싫다고|거절|강요|압박|항상|상시|사랑하면)/.test(compact);
  if(consensualTemporaryLocation){
    return {
      meaning:"두 사람이 만남을 위한 편의 목적으로, 서로 동의해 필요한 시간 동안만 위치를 공유하기로 한 상황입니다.",
      emotion:"이 합의만으로 관계 감정이나 신뢰 수준을 추가로 해석할 필요는 없습니다.",
      caution:"사용자가 말하지 않은 출발 시각·도착 시각·현재 이동 상태를 새로 만들지 마세요. 일회성 합의를 상시 위치공유 약속으로 확대하지도 마세요.",
      advice:"서로 합의한 범위와 종료 시점만 짧게 확인하면 충분합니다.",
      nextAction:"아래 문장 중 하나로 만날 때까지만 공유한다는 범위를 확인하고, 약속된 범위를 넘겨 계속 공유할 필요는 없습니다.",
      replies:[
        {label:"가장 자연스럽게",text:"좋아, 만날 때까지만 위치 공유하자.",reason:"사용자가 말한 합의 범위만 그대로 확인합니다."},
        {label:"조금 더 명확하게",text:"응, 서로 동의한 대로 만날 때까지만 공유하자.",reason:"상호 동의와 한시적 범위를 분명히 합니다."},
        {label:"간결하게",text:"좋아. 필요한 동안만 위치 공유하자.",reason:"출발·도착 같은 미확인 행동을 만들지 않습니다."}
      ]
    };
  }

  const liveLocationPressure='''
assert anchor in s
s=s.replace(anchor,insert,1)

# 2) Very short nonurgent silence: no reply candidates and no 6-8 hour chasing rule.
anchor='''  const storyViewNoResponse='''
insert=r'''  const veryShortNoResponse=/(?:1\s*시간|한\s*시간|2\s*시간|두\s*시간)[^.\n]{0,70}(?:답(?:장)?(?:이)?\s*(?:없|안)|무응답|읽씹)/.test(compact) || /(?:답(?:장)?(?:이)?\s*(?:없|안)|무응답|읽씹)[^.\n]{0,70}(?:1\s*시간|한\s*시간|2\s*시간|두\s*시간)/.test(compact);
  if(veryShortNoResponse && !/(?:약속\s*당일|오늘[^.\n]{0,30}약속|응급|긴급)/.test(compact)){
    return {
      meaning:"비긴급 상황에서 메시지를 보낸 뒤 약 1~2시간 답이 없다는 사실만 확인됩니다. 이 정도 시간만으로 상대의 마음이나 참여도를 판단할 수 없습니다.",
      emotion:"답이 없는 이유는 알 수 없으므로 바쁨·피곤함·관심 저하를 추정하지 않습니다.",
      caution:"지금 추가 메시지를 보내거나 6~8시간 뒤 다시 확인하는 별도 전략을 만들지 마세요. 답장 시간을 계산해 밀당하지도 마세요.",
      advice:"지금은 새 메시지를 보내지 않고 상대가 답할 시간을 주는 것이 맞습니다. 초기 비긴급 무응답은 처음 메시지를 보낸 시점부터 총 약 3일을 기준으로 봅니다.",
      nextAction:"지금은 기다리세요. 처음 메시지 기준 약 3일이 됐는데도 답이 없고 후속 연락을 한 번도 하지 않았다면 그때 낮은 압력의 확인을 한 번만 고려하세요.",
      replies:[]
    };
  }

  const storyViewNoResponse='''
assert anchor in s
s=s.replace(anchor,insert,1)

# 3) Full deterministic PRO scheduling result when counterpart's day is impossible for user and user supplies a real alternative.
anchor='''async function generateAnalysisResult(reqBody){'''
insert=r'''function getDeterministicDetailAnalysis(reqBody){
  if(String(reqBody?.mode||"")!=="detail") return null;
  const msg=String(reqBody?.message||"");
  const compact=msg.replace(/\s+/g," ");
  const counterpart=compact.match(/(?:상대(?:가|는)?[^.\n]{0,120})?(다음\s*주|다음주)\s*(월요일|화요일|수요일|목요일|금요일|토요일|일요일)(?:\s*(오전|오후|저녁))?[^.\n]{0,35}(?:가능|된|괜찮)/);
  if(!counterpart) return null;
  const day=counterpart[2];
  if(!hasExplicitUserUnavailability(compact,day)) return null;
  const alt=getExplicitUserAlternative(compact,day);
  if(!alt) return null;
  const counterWhen=[counterpart[1].replace(/\s+/g," "),day,counterpart[3]||""].filter(Boolean).join(" ");
  const altWhen=alt.when;
  return {
    meaning:`상대는 ${counterWhen}을(를) 제안했지만 사용자는 ${day}은 어렵고 ${altWhen}은 가능하다고 명시했습니다. 지금은 감정 분석보다 실제 일정 조율이 우선입니다.`,
    confidence:"높음",
    emotion:"상대가 대안 날짜를 말한 것은 일정 조율 참여 행동이지만 호감의 크기를 확정하는 근거는 아닙니다.",
    flow:`상대의 ${counterWhen} 제안과 사용자의 ${day} 불가·${altWhen} 가능 정보가 확인됩니다.`,
    strategy:`사용자가 불가능한 ${day}은 짧게 거절하고 실제 가능한 ${altWhen}을(를) 한 번 대안으로 제시합니다.`,
    caution:`${day}이 안 되는 이유를 입력에 없는 업무·약속·개인 사정으로 만들어 설명하지 마세요.`,
    dontSend:`${day} 좋아요, 그때 봐요처럼 불가능한 날짜를 수락하거나 '일이 있어서'처럼 입력에 없는 이유를 붙인 문장은 보내지 마세요.`,
    replies:[
      {label:"가장 자연스러운 답장",text:`${day}은 어려운데 ${altWhen}은 괜찮아요. ${altWhen}은 어떠세요?`,reason:"입력된 일정 사실만 사용합니다."},
      {label:"조금 더 정중한 답장",text:`말씀하신 ${day}은 어렵고 저는 ${altWhen}이 가능합니다. 괜찮으실까요?`,reason:"없는 이유를 만들지 않고 실제 대안만 제시합니다."},
      {label:"조금 더 여유 있는 답장",text:`${day}은 어렵습니다. ${altWhen}은 가능해요.`,reason:"가장 간결하게 일정 사실만 전달합니다."}
    ],
    advice:`${day}이 어렵다는 사실과 ${altWhen}이 가능하다는 사실만 전달하면 충분합니다.`,
    nextAction:`지금 ${altWhen}을(를) 한 번 제안하고 상대의 가능 여부를 기다리세요. 상대도 어렵다면 실제 가능한 다른 시간만 조율하세요.`
  };
}

async function generateAnalysisResult(reqBody){
  const directDetail=getDeterministicDetailAnalysis(reqBody||{});
  if(directDetail) return {parsed:directDetail,isDetail:true};'''
assert anchor in s
s=s.replace(anchor,insert,1)

assert '2026-08-23-potentia-v44-deterministic-edges' in s
assert 'consensualTemporaryLocation' in s and 'veryShortNoResponse' in s and 'getDeterministicDetailAnalysis' in s
p.write_text(s,encoding='utf-8')
print('Potentia v44 deterministic edge patch applied')
