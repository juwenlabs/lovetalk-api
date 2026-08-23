from pathlib import Path
p=Path('server.js')
s=p.read_text(encoding='utf-8')
assert '2026-08-23-potentia-v42-grounding-timing' in s
s=s.replace('const SERVER_VERSION = "2026-08-23-potentia-v42-grounding-timing";', 'const SERVER_VERSION = "2026-08-23-potentia-v43-day-binding-location-safety";', 1)

# 1) Bind availability evidence to the SAME day; stop at the next weekday and let explicit negatives override.
start=s.index('function hasExplicitUserAvailability(')
end=s.index('\n\nfunction applyAnalysisPolicyGuards', start)
new_helpers=r'''function hasExplicitUserAvailability(compact,dayName=""){
  const src=String(compact||"");
  const day=String(dayName||"").trim();
  if(!day) return false;
  const userRe=/(?:나는|내가|저는|저도|나도|사용자)([^.\n]{0,160})/g;
  const weekdayRe=/(월요일|화요일|수요일|목요일|금요일|토요일|일요일)/g;
  let m;
  while((m=userRe.exec(src))){
    const tail=m[1]||"";
    let searchFrom=0;
    while(true){
      const dayIdx=tail.indexOf(day,searchFrom);
      if(dayIdx<0) break;
      const after=tail.slice(dayIdx+day.length);
      const nextDay=after.match(weekdayRe);
      const sameDaySegment=nextDay?after.slice(0,nextDay.index):after;
      if(/(?:안\s*되|안\s*돼|안됨|불가능|어렵|힘들|못\s*(?:가|해|돼)|시간\s*안)/.test(sameDaySegment)){
        searchFrom=dayIdx+day.length;
        continue;
      }
      if(/(?:가능|괜찮|돼|된다|시간\s*됨|시간\s*돼)/.test(sameDaySegment)) return true;
      searchFrom=dayIdx+day.length;
    }
  }
  return false;
}
function hasExplicitUserUnavailability(compact,dayName=""){
  const src=String(compact||"");
  const day=String(dayName||"").trim();
  if(!day) return false;
  const userRe=/(?:나는|내가|저는|저도|나도|사용자)([^.\n]{0,160})/g;
  const weekdayRe=/(월요일|화요일|수요일|목요일|금요일|토요일|일요일)/;
  let m;
  while((m=userRe.exec(src))){
    const tail=m[1]||"";
    let searchFrom=0;
    while(true){
      const dayIdx=tail.indexOf(day,searchFrom);
      if(dayIdx<0) break;
      const after=tail.slice(dayIdx+day.length);
      const nextDay=after.match(weekdayRe);
      const sameDaySegment=nextDay?after.slice(0,nextDay.index):after;
      if(/(?:안\s*되|안\s*돼|안됨|불가능|어렵|힘들|못\s*(?:가|해|돼)|시간\s*안)/.test(sameDaySegment)) return true;
      searchFrom=dayIdx+day.length;
    }
  }
  return false;
}
function getExplicitUserAlternative(compact,excludeDay=""){
  const days=["월요일","화요일","수요일","목요일","금요일","토요일","일요일"];
  for(const day of days){
    if(day===excludeDay) continue;
    if(hasExplicitUserAvailability(compact,day)){
      const userRe=/(?:나는|내가|저는|저도|나도|사용자)([^.\n]{0,160})/g;
      let m;
      while((m=userRe.exec(String(compact||"")))){
        const tail=m[1]||""; const idx=tail.indexOf(day); if(idx<0) continue;
        const after=tail.slice(idx+day.length);
        const beforeNext=(after.match(/월요일|화요일|수요일|목요일|금요일|토요일|일요일/));
        const seg=beforeNext?after.slice(0,beforeNext.index):after;
        const part=(seg.match(/\s*(오전|오후|저녁)/)||[])[1]||"";
        return {day,part,when:[day,part].filter(Boolean).join(" ")};
      }
      return {day,part:"",when:day};
    }
  }
  return null;
}'''
s=s[:start]+new_helpers+s[end:]

# 2) In PRO detail, if counterpart day is unavailable and the user supplied a real alternative, use that alternative rather than generic schedule checking.
anchor='''  if(detailAlternativeDate && !detailUserAvailability){
    const alt=compact.match(/(다음\\s*주|다음주)\\s*(월요일|화요일|수요일|목요일|금요일|토요일|일요일)(?:\\s*(오전|오후|저녁))?/);
    const when=alt?[alt[1].replace(/\\s+/g," "),alt[2],alt[3]||""].filter(Boolean).join(" "):"상대가 제안한 날짜";'''
replace='''  if(detailAlternativeDate && !detailUserAvailability){
    const alt=compact.match(/(다음\\s*주|다음주)\\s*(월요일|화요일|수요일|목요일|금요일|토요일|일요일)(?:\\s*(오전|오후|저녁))?/);
    const when=alt?[alt[1].replace(/\\s+/g," "),alt[2],alt[3]||""].filter(Boolean).join(" "):"상대가 제안한 날짜";
    const userAlternative=detailAltDay?getExplicitUserAlternative(compact,detailAltDay):null;
    if(userAlternative && hasExplicitUserUnavailability(compact,detailAltDay)){
      const altWhen=userAlternative.when;
      out.replies=[
        {label:"실제 가능한 대안",text:`${detailAltDay}은 어려운데 ${altWhen}은 괜찮아요. ${altWhen}은 어떠세요?`,reason:"사용자가 실제로 불가능하다고 한 날짜는 거절하고 실제 가능한 대안만 제안합니다."},
        {label:"조금 더 정중하게",text:`말씀하신 ${detailAltDay}은 어렵고 저는 ${altWhen}이 가능합니다. ${altWhen}은 괜찮으실까요?`,reason:"상대 제안과 사용자 일정을 구분해 조율합니다."},
        {label:"간결하게",text:`${detailAltDay}은 어렵습니다. ${altWhen}은 가능해요.`,reason:"입력된 일정 사실만 사용합니다."}
      ];
      out.caution=`사용자가 ${detailAltDay}은 어렵다고 명시했으므로 그 날짜를 수락하거나 확정하지 마세요.`;
      out.dontSend=`${detailAltDay} 좋아요, 그때 봐요처럼 사용자의 불가능한 날짜를 수락하는 문장은 보내지 마세요.`;
      out.advice=`상대 제안을 거절하는 대신 사용자가 실제로 가능한 ${altWhen}을(를) 대안으로 제시하는 것이 맞습니다.`;
      out.nextAction=`${altWhen}을(를) 한 번 제안하고 상대가 가능한지 확인하세요. 상대도 어렵다고 하면 사용자가 실제로 가능한 범위 안에서만 다시 조율하세요.`;
      return out;
    }'''
assert anchor in s
s=s.replace(anchor,replace,1)

# 3) Deterministic coercive live-location boundary. One-time consensual logistics won't match because pressure/refusal cues are required.
anchor='''  const phonePasswordPressure='''
insert=r'''  const liveLocationPressure=/(?:실시간\s*위치|위치\s*공유|위치정보)/.test(compact) && /(?:항상|계속|상시|싫다고|거절|요구|사랑하면|켜\s*두|켜두)/.test(compact);
  if(liveLocationPressure){
    return {
      meaning:"상대가 사랑이나 관계를 이유로 실시간 위치를 계속 공유하라고 요구하고 사용자가 원하지 않는다는 경계가 존중되지 않는 상황입니다.",
      emotion:"상대의 동기를 불안·통제 욕구로 단정하지 않더라도 반복되는 위치공유 요구 자체는 개인정보 경계 문제입니다.",
      caution:"원하지 않는 실시간 위치공유를 신뢰 증명으로 켜두지 마세요. 문제를 해결하기 위해 단둘이 직접 만나야 한다고 권하지도 마세요.",
      advice:"짧고 분명하게 위치공유를 원하지 않는다고 말하고, 압박이 반복되면 같은 논쟁을 계속하기보다 연락·접촉을 줄이고 신뢰할 수 있는 사람에게 상황을 공유하는 것을 고려하세요.",
      nextAction:"아래 문장 중 하나로 경계를 한 번 분명히 전달하세요. 요구나 압박이 계속되거나 안전이 걱정되면 단둘이 만나서 해결하려 하지 말고 안전한 거리와 도움을 우선하세요.",
      replies:[
        {label:"명확한 경계",text:"실시간 위치를 계속 공유하는 건 원하지 않아. 이건 내 개인정보 경계야.",reason:"사랑의 증명과 개인정보 제공을 분리합니다."},
        {label:"반복 요구 중단",text:"이미 원하지 않는다고 말했어. 위치공유 요구는 더 이상 하지 말아줘.",reason:"사용자의 기존 거절을 분명하게 반복합니다."},
        {label:"압박 시 거리두기",text:"이 요구가 계속되면 이 대화는 여기서 멈출게.",reason:"대면 만남을 강요하지 않고 반복 압박에 행동 경계를 둡니다."}
      ]
    };
  }

  const phonePasswordPressure='''
assert anchor in s
s=s.replace(anchor,insert,1)

# 4) Quick counterpart-date branch: if counterpart day is explicitly impossible and user gives a different real alternative, propose the actual alternative.
needle='''    const userAvailability=alt?.[2]?hasExplicitUserAvailability(compact,alt[2]):false;
    if(!userAvailability){
      return {'''
replacement='''    const userAvailability=alt?.[2]?hasExplicitUserAvailability(compact,alt[2]):false;
    const counterpartDay=alt?.[2]||"";
    const userAlternative=counterpartDay?getExplicitUserAlternative(compact,counterpartDay):null;
    if(!userAvailability && counterpartDay && hasExplicitUserUnavailability(compact,counterpartDay) && userAlternative){
      const altWhen=userAlternative.when;
      return {
        meaning:`상대는 ${when}을(를) 제안했지만 사용자는 ${counterpartDay}은 어렵고 ${altWhen}은 가능하다고 명시했습니다.`,
        emotion:"일정 불일치는 감정 거절로 해석하지 않고 실제 가능한 시간만 조율합니다.",
        caution:`사용자가 불가능하다고 한 ${counterpartDay}을(를) 수락하거나 약속을 확정하지 마세요.`,
        advice:`사용자가 실제로 가능한 ${altWhen}을(를) 한 번 대안으로 제시하세요.`,
        nextAction:`${altWhen} 가능 여부를 상대에게 확인하고, 어렵다면 실제 가능한 다른 시간만 조율하세요.`,
        replies:[
          {label:"가장 자연스럽게",text:`${counterpartDay}은 어려운데 ${altWhen}은 괜찮아요. ${altWhen}은 어떠세요?`,reason:"사용자가 제공한 실제 일정만 사용합니다."},
          {label:"정중하게",text:`말씀하신 ${counterpartDay}은 어렵고 저는 ${altWhen}이 가능해요. 괜찮으실까요?`,reason:"상대 제안을 존중하면서 실제 대안을 제시합니다."},
          {label:"간결하게",text:`${counterpartDay}은 어렵습니다. ${altWhen}은 가능해요.`,reason:"없는 일정이나 감정을 추가하지 않습니다."}
        ]
      };
    }
    if(!userAvailability){
      return {'''
# There can be two occurrences; replace both so fallback and counterpart-specific blocks both stay safe.
count=s.count(needle)
assert count>=1, count
s=s.replace(needle,replacement)

assert '2026-08-23-potentia-v43-day-binding-location-safety' in s
assert 'liveLocationPressure' in s and 'hasExplicitUserUnavailability' in s and 'getExplicitUserAlternative' in s
p.write_text(s,encoding='utf-8')
print('Potentia v43 day binding/location safety patch applied')
