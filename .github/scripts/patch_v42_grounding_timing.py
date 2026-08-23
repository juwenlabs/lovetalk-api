from pathlib import Path
p=Path('server.js')
s=p.read_text(encoding='utf-8')
assert '2026-08-23-potentia-v41-availability-boundaries' in s
s=s.replace('const SERVER_VERSION = "2026-08-23-potentia-v41-availability-boundaries";', 'const SERVER_VERSION = "2026-08-23-potentia-v42-grounding-timing";', 1)

# Reusable user-availability parser. A prior "내가 ... 상대가 화요일 된다고" clause must not be mistaken for user availability.
anchor='''function applyAnalysisPolicyGuards(parsed,reqBody,isDetail){'''
helper='''function hasExplicitUserAvailability(compact,dayName=""){
  const src=String(compact||"");
  const day=String(dayName||"").trim();
  const re=/(?:나는|내가|저는|저도|나도|사용자)([^.\\n]{0,100})/g;
  let m;
  while((m=re.exec(src))){
    const tail=m[1]||"";
    const dayIdx=day?tail.indexOf(day):-1;
    if(day && dayIdx<0) continue;
    const afterDay=day?tail.slice(dayIdx+day.length):tail;
    const availMatch=afterDay.match(/(?:가능|괜찮|돼|된다|시간\\s*됨)/);
    if(!availMatch) continue;
    const availIdx=(day?dayIdx+day.length:0)+availMatch.index;
    if(/상대/.test(tail.slice(0,availIdx))) continue;
    return true;
  }
  return false;
}

function applyAnalysisPolicyGuards(parsed,reqBody,isDetail){'''
assert anchor in s
s=s.replace(anchor,helper,1)

# Detail mode: determine availability from a clause that actually belongs to the user.
old='''  const detailAlternativeDate=isDetail && /(?:다음\\s*주|다음주)[^.\\n]{0,50}(?:월요일|화요일|수요일|목요일|금요일|토요일|일요일)[^.\\n]{0,30}(?:가능|된|괜찮)/.test(compact);
  const detailUserAvailability=/(?:나는|내가|저는|저도|나도|사용자)[^.\\n]{0,70}(?:월요일|화요일|수요일|목요일|금요일|토요일|일요일)[^.\\n]{0,30}(?:가능|괜찮|돼|된다|시간\\s*됨)/.test(compact);'''
new='''  const detailAlternativeDate=isDetail && /(?:다음\\s*주|다음주)[^.\\n]{0,50}(?:월요일|화요일|수요일|목요일|금요일|토요일|일요일)[^.\\n]{0,30}(?:가능|된|괜찮)/.test(compact);
  const detailAltMatch=compact.match(/(다음\\s*주|다음주)\\s*(월요일|화요일|수요일|목요일|금요일|토요일|일요일)(?:\\s*(오전|오후|저녁))?/);
  const detailAltDay=detailAltMatch?.[2]||"";
  const detailUserAvailability=detailAltDay?hasExplicitUserAvailability(compact,detailAltDay):false;'''
assert old in s
s=s.replace(old,new,1)

# Quick mode: story views never prove interest, and 48h means roughly one more day to the total-three-day checkpoint.
anchor='''  const oneDayNoResponse='''
insert='''  const storyViewNoResponse=/스토리/.test(compact) && /(?:답(?:장)?(?:이)?\\s*(?:없|안)|무응답|읽씹)/.test(compact);
  if(storyViewNoResponse && !/(?:약속\\s*당일|오늘[^.\\n]{0,30}약속|응급|긴급)/.test(compact)){
    return {
      meaning:"상대가 메시지에는 답하지 않았지만 SNS 스토리를 봤다는 두 사실만 확인됩니다. 스토리 조회는 답장 의사나 호감을 증명하는 행동이 아닙니다.",
      emotion:"스토리를 봤다는 단일 SNS 신호로 관심이 있다·없다를 확정하지 않습니다.",
      caution:"스토리 조회를 재연락의 명분으로 쓰거나 '봤으면서 왜 답 안 해?'처럼 추궁하지 마세요.",
      advice:"SNS 활동과 메시지 참여를 분리해서 보세요. 비긴급 무응답은 처음 메시지를 보낸 시점부터 총 약 3일을 기준으로 보고, 그 전에는 새 메시지를 만들지 않는 편이 안전합니다.",
      nextAction:"지금은 스토리를 이유로 다시 연락하지 마세요. 처음 메시지 기준 약 3일이 됐는데도 답이 없고 후속 연락을 아직 한 번도 하지 않았다면 그때 낮은 압력의 확인을 딱 한 번만 고려하세요.",
      replies:[]
    };
  }

  const twoDayNoResponse=/(?:48\\s*시간|이틀|2\\s*일)[^.\\n]{0,70}(?:답(?:장)?(?:이)?\\s*(?:없|안)|무응답|읽씹)/.test(compact) || /(?:답(?:장)?(?:이)?\\s*(?:없|안)|무응답|읽씹)[^.\\n]{0,70}(?:48\\s*시간|이틀|2\\s*일)/.test(compact);
  if(twoDayNoResponse && !/(?:약속\\s*당일|오늘[^.\\n]{0,30}약속|응급|긴급)/.test(compact)){
    return {
      meaning:"비긴급 상황에서 마지막 메시지 후 약 48시간 동안 답이 없다는 사실만 확인됩니다. 이틀 무응답만으로 상대의 마음을 확정할 수 없습니다.",
      emotion:"무응답 이유는 알 수 없으므로 바쁨·피곤함·관심 저하를 사실처럼 만들지 않습니다.",
      caution:"지금 재촉하거나, 여기서 다시 3일을 추가해 총 5일 이상 기다리는 식으로 계산하지 마세요.",
      advice:"초기 비긴급 무응답은 처음 메시지를 보낸 시점부터 총 약 3일을 기준으로 봅니다. 이미 48시간이 지났다면 약 하루 정도 더 기다리는 방향입니다.",
      nextAction:"지금은 새 메시지를 보내지 마세요. 약 하루 정도 더 지나 처음 메시지 기준 총 약 3일이 됐는데도 답이 없고 후속 연락을 한 번도 하지 않았다면 낮은 압력의 확인을 한 번만 고려하세요.",
      replies:[]
    };
  }

  const oneDayNoResponse='''
assert anchor in s
s=s.replace(anchor,insert,1)

# Counterpart date proposal: check whether the user explicitly said they are available before confirming.
anchor='''  const concreteAlternativeDate='''
insert='''  const counterpartDateProposal=/상대(?:가|는)?[^.\\n]{0,110}(?:다음\\s*주|다음주)\\s*(?:월요일|화요일|수요일|목요일|금요일|토요일|일요일)[^.\\n]{0,35}(?:가능|된|괜찮)/.test(compact);
  if(counterpartDateProposal){
    const alt=compact.match(/(다음\\s*주|다음주)\\s*(월요일|화요일|수요일|목요일|금요일|토요일|일요일)(?:\\s*(오전|오후|저녁))?/);
    const when=alt?[alt[1].replace(/\\s+/g," "),alt[2],alt[3]||""].filter(Boolean).join(" "):"상대가 제안한 날짜";
    const userAvailability=alt?.[2]?hasExplicitUserAvailability(compact,alt[2]):false;
    if(!userAvailability){
      return {
        meaning:`상대가 ${when}을(를) 구체적으로 제안했지만 사용자가 그 시간에 가능한지는 아직 확인되지 않았습니다.`,
        emotion:"구체적인 날짜 제시는 일정 조율 참여 행동이지만 호감의 크기를 확정하는 근거는 아닙니다.",
        caution:"사용자 일정이 확인되지 않았는데 약속을 확정하거나 기대감·설렘을 새로 만들어 보내지 마세요.",
        advice:"사용자의 실제 일정부터 확인한 뒤 가능할 때만 상대 제안을 확정하세요.",
        nextAction:`${when} 가능 여부를 먼저 확인하세요. 확인 전에는 아래처럼 일정 확인 후 답하겠다고 보내는 편이 안전합니다.`,
        replies:[
          {label:"일정 확인",text:`${when} 말씀하신 거 확인했어요. 제 일정 확인하고 다시 말씀드릴게요.`,reason:"사용자의 미확인 일정을 사실처럼 만들지 않습니다."},
          {label:"짧게",text:`${when} 가능 여부 확인해보고 말씀드릴게요.`,reason:"성급한 약속 확정을 피합니다."},
          {label:"정중하게",text:`${when} 제안해주셔서 감사합니다. 일정 확인 후 말씀드릴게요.`,reason:"입력에 없는 기대감 없이 대안 제안만 받아줍니다."}
        ]
      };
    }
    return {
      meaning:`상대가 ${when}을(를) 제안했고 사용자도 해당 날짜가 가능하다고 명시했습니다. 일정 확정 단계입니다.`,
      emotion:"서로 가능한 시간이 확인됐다는 일정 참여 사실만 사용하고 호감 강도는 단정하지 않습니다.",
      caution:"상대가 사용자를 위해 일정을 '맞춰줬다'고 입력되지 않았다면 그런 배려 사실을 새로 만들지 마세요.",
      advice:"확인된 날짜를 짧게 수락하고 아직 정하지 않은 장소나 구체적 시간 중 하나만 다음으로 조율하세요.",
      nextAction:`${when}을(를) 수락한 뒤 다음 요소 하나만 조율하세요.`,
      replies:[
        {label:"가장 자연스럽게",text:`좋아요. ${when}으로 해요.`,reason:"확인된 일정만 사용합니다."},
        {label:"정중하게",text:`좋습니다. ${when}에 뵈어요.`,reason:"상대가 일정을 맞춰줬다는 근거 없는 의미를 붙이지 않습니다."},
        {label:"다음 조율",text:`${when} 괜찮아요. 장소는 어디가 편하세요?`,reason:"질문 하나로 다음 요소만 조율합니다."}
      ]
    };
  }

  const concreteAlternativeDate='''
assert anchor in s
s=s.replace(anchor,insert,1)

# Existing fallback alternative-date branch also uses the safer user-availability parser.
old='''    const userAvailability=/(?:나는|내가|저는|저도|나도|사용자)[^.\\n]{0,70}(?:월요일|화요일|수요일|목요일|금요일|토요일|일요일)[^.\\n]{0,30}(?:가능|괜찮|돼|된다|시간\\s*됨)/.test(compact);'''
new='''    const userAvailability=alt?.[2]?hasExplicitUserAvailability(compact,alt[2]):false;'''
assert old in s
s=s.replace(old,new,1)

# First app conversation: common hobbies use counterpart-provided topic only, never invented user preferences/plans.
anchor='''  const appMatchCookingFirst='''
insert='''  const appMatchGeneralHobby=/(?:앱\\s*매칭|소개팅\\s*앱|매칭\\s*첫\\s*대화)/.test(relation) && /(?:아직[^.\\n]{0,30}답장|답장[^.\\n]{0,20}안)/.test(compact) && /(?:전시|여행|음악|독서|책|운동)[^.\\n]{0,30}좋아/.test(compact);
  if(appMatchGeneralHobby){
    let replies;
    if(/전시/.test(compact)) replies=[
      {label:"가장 자연스럽게",text:"어떤 전시 좋아하세요?",reason:"상대가 실제로 말한 전시 관심사만 사용합니다."},
      {label:"조금 더 구체적으로",text:"요즘 관심 가는 전시 있으세요?",reason:"사용자 취향을 새로 만들지 않고 상대의 관심사를 묻습니다."},
      {label:"가볍게 이어가기",text:"최근에 본 전시 중 기억에 남는 게 있으세요?",reason:"가짜 공통점이나 사용자 계획 없이 질문 하나로 이어갑니다."}
    ];
    else if(/여행/.test(compact)) replies=[
      {label:"가장 자연스럽게",text:"어떤 여행지 좋아하세요?",reason:"상대가 말한 여행 관심사만 사용합니다."},
      {label:"조금 더 구체적으로",text:"여행은 어떤 스타일 좋아하세요?",reason:"사용자 경험을 지어내지 않습니다."},
      {label:"가볍게 이어가기",text:"최근에 가보고 싶은 곳 있으세요?",reason:"상대의 취향을 질문으로 확인합니다."}
    ];
    else if(/음악/.test(compact)) replies=[
      {label:"가장 자연스럽게",text:"어떤 음악 좋아하세요?",reason:"상대가 제공한 관심사만 사용합니다."},
      {label:"조금 더 구체적으로",text:"요즘 자주 듣는 음악 있으세요?",reason:"사용자 취향을 공통점으로 만들지 않습니다."},
      {label:"가볍게 이어가기",text:"좋아하는 가수나 장르 있으세요?",reason:"질문 하나로 대화 소재를 넓힙니다."}
    ];
    else if(/(?:독서|책)/.test(compact)) replies=[
      {label:"가장 자연스럽게",text:"어떤 책 좋아하세요?",reason:"상대가 말한 독서 관심사만 사용합니다."},
      {label:"조금 더 구체적으로",text:"요즘 읽고 있는 책 있으세요?",reason:"사용자 경험을 지어내지 않습니다."},
      {label:"가볍게 이어가기",text:"좋아하는 장르 있으세요?",reason:"가짜 공통점 없이 질문 하나로 이어갑니다."}
    ];
    else replies=[
      {label:"가장 자연스럽게",text:"어떤 운동 좋아하세요?",reason:"상대가 말한 운동 관심사만 사용합니다."},
      {label:"조금 더 구체적으로",text:"요즘 주로 어떤 운동 하세요?",reason:"사용자 경험을 지어내지 않습니다."},
      {label:"가볍게 이어가기",text:"운동은 어떤 종목 좋아하세요?",reason:"상대의 취향을 질문으로 확인합니다."}
    ];
    return {
      meaning:"상대가 첫 대화에서 자신의 관심사를 하나 공유했고 사용자는 아직 답장하지 않은 상태입니다.",
      emotion:"한 번의 취미 공유만으로 호감이나 참여 수준을 확정하지 않습니다.",
      caution:"'저도 좋아해요·저도 자주 가요·저도 해보고 싶어요'처럼 사용자가 말하지 않은 취향·경험·계획을 새로 만들지 마세요.",
      advice:"상대가 실제로 제공한 관심사 안에서 질문 하나로 자연스럽게 이어가세요.",
      nextAction:"아래 문장 중 하나를 답장하고 이후 상대가 구체적으로 답하거나 역질문하는지 확인하세요.",
      replies
    };
  }

  const appMatchCookingFirst='''
assert anchor in s
s=s.replace(anchor,insert,1)

assert '2026-08-23-potentia-v42-grounding-timing' in s
assert 'storyViewNoResponse' in s and 'twoDayNoResponse' in s and 'appMatchGeneralHobby' in s and 'hasExplicitUserAvailability' in s
p.write_text(s,encoding='utf-8')
print('Potentia v42 grounding/timing patch applied')
