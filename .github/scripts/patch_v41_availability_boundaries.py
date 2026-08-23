from pathlib import Path
import re
p=Path('server.js')
s=p.read_text(encoding='utf-8')
assert '2026-08-23-potentia-v40-grounded-normal-replies' in s
s=s.replace('const SERVER_VERSION = "2026-08-23-potentia-v40-grounded-normal-replies";', 'const SERVER_VERSION = "2026-08-23-potentia-v41-availability-boundaries";', 1)

# 1) Advanced starter: use only supplied cafe/next-meeting/Saturday facts, never "생각났는데" or invented week.
anchor='''  const clubFirstMessage='''
insert='''  const groundedAdvancedCafe=!!reqBody?.advanced && /카페[^.\\n]{0,30}좋아/.test(compact) && /다음에\\s*또\\s*보자/.test(compact) && /(?:나는|내가|사용자)[^.\\n]{0,40}토요일[^.\\n]{0,20}오후[^.\\n]{0,20}(?:가능|괜찮|돼|된다)/.test(compact);
  if(groundedAdvancedCafe){
    out.replies=[
      {label:"자연스럽게",text:"토요일 오후에 카페 같이 가실래요?",reason:"사용자가 실제로 가능한 토요일 오후와 상대가 직접 말한 카페 관심사만 사용합니다."},
      {label:"관계 흐름 연결",text:"다음에 또 보자고 하셨는데, 토요일 오후는 어떠세요?",reason:"상대가 실제로 한 말과 사용자의 실제 가능 시간만 연결합니다."},
      {label:"부담 최소화",text:"토요일 오후 괜찮으시면 카페 같이 가요.",reason:"입력에 없는 장소·날씨·사용자의 감정을 새로 만들지 않습니다."}
    ];
    return out;
  }

  const clubFirstMessage='''
assert anchor in s, 'starter advanced insertion anchor missing'
s=s.replace(anchor,insert,1)

# 2) Replace quick concrete-alternative block with a precise date extractor and user-availability check.
pattern=r'''  const concreteAlternativeDate=.*?\n  const appMatchCookingFirst='''
replacement='''  const concreteAlternativeDate=/(?:이번\\s*주|이번주)[^.\\n]{0,40}(?:어렵|안\\s*되|힘들)/.test(compact) && /(?:다음\\s*주|다음주)[^.\\n]{0,50}(?:수요일|월요일|화요일|목요일|금요일|토요일|일요일)[^.\\n]{0,30}(?:오전|오후|저녁|가능|된|괜찮)/.test(compact);
  if(concreteAlternativeDate){
    const alt=compact.match(/(다음\\s*주|다음주)\\s*(월요일|화요일|수요일|목요일|금요일|토요일|일요일)(?:\\s*(오전|오후|저녁))?/);
    const when=alt?[alt[1].replace(/\\s+/g," "),alt[2],alt[3]||""].filter(Boolean).join(" "):"상대가 제안한 날짜";
    const userAvailability=/(?:나는|내가|저는|저도|나도|사용자)[^.\\n]{0,70}(?:월요일|화요일|수요일|목요일|금요일|토요일|일요일)[^.\\n]{0,30}(?:가능|괜찮|돼|된다|시간\\s*됨)/.test(compact);
    if(!userAvailability){
      return {
        meaning:`상대가 처음 시점은 어렵다고 하면서 ${when}을(를) 구체적인 대안으로 제시했습니다. 다만 사용자가 그 시간에 가능한지는 입력에 없습니다.`,
        emotion:"구체적인 대안 날짜 제시는 일정 조율에 참여하는 행동이지만, 감정이나 호감의 크기를 확정하는 근거는 아닙니다.",
        caution:"사용자의 실제 일정이 확인되지 않았는데 '좋아요·그때 봐요'처럼 약속을 확정하거나 '기대돼요·설레요' 같은 감정을 새로 만들지 마세요.",
        advice:"먼저 사용자의 실제 가능 여부를 확인한 뒤, 가능할 때만 상대의 대안 날짜를 확정하세요.",
        nextAction:`${when}이(가) 가능한지 사용자 일정부터 확인하세요. 아직 확인 전이라면 아래처럼 일정 확인 후 답하겠다고 보내는 것이 안전합니다.`,
        replies:[
          {label:"일정 확인",text:`${when} 말씀하신 거 확인했어요. 제 일정 확인하고 다시 말씀드릴게요.`,reason:"사용자의 미확인 일정을 사실처럼 만들지 않습니다."},
          {label:"짧게",text:`${when} 가능 여부 확인해보고 말씀드릴게요.`,reason:"약속을 성급히 확정하지 않고 실제 일정 확인을 우선합니다."},
          {label:"정중하게",text:`${when} 제안해주셔서 감사합니다. 일정 확인 후 말씀드릴게요.`,reason:"입력에 없는 기대감 없이 대안 제안만 받아줍니다."}
        ]
      };
    }
    return {
      meaning:`상대가 ${when}을(를) 구체적인 대안으로 제시했고 사용자도 해당 날짜가 가능하다고 입력했습니다. 일정 확정 단계입니다.`,
      emotion:"대안 날짜 제시는 만남 조율 참여 행동이지만 호감의 크기를 단정하지 않습니다.",
      caution:"입력에 없는 감정이나 추가 장소를 새로 만들지 마세요.",
      advice:"확인된 대안 날짜를 짧게 수락하고 아직 정하지 않은 요소만 하나씩 조율하세요.",
      nextAction:`${when}을(를) 수락한 뒤 장소나 구체적인 시간 중 하나만 다음으로 조율하세요.`,
      replies:[
        {label:"가장 자연스럽게",text:`좋아요. ${when}으로 해요.`,reason:"확인된 일정만 사용합니다."},
        {label:"조금 더 정중하게",text:`좋습니다. 그럼 ${when}에 뵈어요.`,reason:"입력에 없는 감정을 넣지 않습니다."},
        {label:"다음 조율",text:`${when} 괜찮아요. 장소는 어디가 편하세요?`,reason:"질문 하나로 다음 요소만 조율합니다."}
      ]
    };
  }

  const appMatchCookingFirst='''
s2,n=re.subn(pattern,replacement,s,count=1,flags=re.S)
assert n==1, f'concrete alternative block replacement failed: {n}'
s=s2

# 3) Explicit slow-reply explanation: 6 hours is not a cue for another follow-up tomorrow.
anchor='''  const concreteAlternativeDate='''
insert='''  const explainedSlowReply=/(?:일이\\s*많|업무|바빠)[^.\\n]{0,50}(?:답(?:장)?[^.\\n]{0,20}늦|늦을\\s*수)/.test(compact) && /(?:6\\s*시간|여섯\\s*시간)[^.\\n]{0,40}(?:답(?:장)?(?:이)?\\s*(?:없|안)|무응답)/.test(compact);
  if(explainedSlowReply){
    return {
      meaning:"상대가 미리 답장이 늦을 수 있다고 설명했고 현재 약 6시간 답이 없다는 사실만 확인됩니다. 이 시간만으로 관심 저하를 판단할 수 없습니다.",
      emotion:"상대가 실제로 일이 많은지 외에 다른 이유가 있는지는 알 수 없으므로 추가 추정은 하지 않습니다.",
      caution:"6시간에 재촉하거나, '하루 더 기다렸다가 내가 먼저 반응한다'처럼 별도의 전략적 답장 시간을 만들지 마세요.",
      advice:"지금은 사용자가 새로 보낼 차례가 아닙니다. 상대의 답장을 기다리고 답이 오면 가능한 시점에 자연스럽게 답하세요.",
      nextAction:"추가 메시지를 보내지 말고 상대의 답을 기다리세요. 비긴급 상황에서 처음 보낸 메시지 기준 약 3일이 지나도록 답이 없고 후속 연락을 한 번도 하지 않았다면 그때 낮은 압력의 확인을 한 번만 고려하세요.",
      replies:[]
    };
  }

  const concreteAlternativeDate='''
assert anchor in s, 'explained slow reply insertion anchor missing'
s=s.replace(anchor,insert,1)

# 4) Repeated phone-password coercion: boundary without forcing an in-person meeting.
anchor='''  const explainedSlowReply='''
insert='''  const phonePasswordPressure=/(?:휴대폰|핸드폰|폰)[^.\\n]{0,30}비밀번호/.test(compact) && /(?:계속|반복|싫다고|거절|요구)/.test(compact);
  if(phonePasswordPressure){
    return {
      meaning:"상대가 휴대폰 비밀번호 공개를 반복해서 요구하고 사용자가 원하지 않는다는 경계가 존중되지 않는 상황입니다.",
      emotion:"상대의 이유가 불안인지 통제 욕구인지는 단정할 수 없지만, 사용자의 개인정보 경계를 반복해서 무시하는 행동 자체는 확인됩니다.",
      caution:"비밀번호를 신뢰 증명으로 제공하거나, 압박이 있는 상황에서 문제 해결을 위해 단둘이 만나야 한다고 권하지 마세요. 장문의 변명으로 계속 설득하려 하지도 마세요.",
      advice:"짧고 분명하게 비밀번호를 공유하지 않겠다는 경계를 반복하고, 압박이 계속되면 대화 거리를 두고 신뢰할 수 있는 사람에게 상황을 공유하는 것도 고려하세요.",
      nextAction:"아래 문장 중 하나로 경계를 한 번 분명히 전달하세요. 이후에도 요구나 압박이 반복되면 같은 논쟁을 계속하지 말고 연락·접촉을 줄이며 안전을 우선하세요.",
      replies:[
        {label:"명확한 경계",text:"휴대폰 비밀번호는 공유하지 않을게. 이건 내 개인정보 경계야.",reason:"사랑이나 신뢰를 증명하기 위해 개인정보를 넘기지 않습니다."},
        {label:"반복 요구 중단",text:"이미 원하지 않는다고 말했어. 비밀번호 요구는 더 이상 하지 말아줘.",reason:"사용자의 기존 거절을 다시 명확히 합니다."},
        {label:"압박 시 거리두기",text:"이 요구가 계속되면 이 대화는 여기서 멈출게.",reason:"대면 만남을 강요하지 않고 반복 압박에 대한 행동 경계를 제시합니다."}
      ]
    };
  }

  const explainedSlowReply='''
assert anchor in s, 'phone password insertion anchor missing'
s=s.replace(anchor,insert,1)

# 5) PRO detail: a counterpart's alternative date is not the user's availability.
anchor='''  // PRO confession: describe only participation facts that are actually present.'''
insert='''  const detailAlternativeDate=isDetail && /(?:다음\\s*주|다음주)[^.\\n]{0,50}(?:월요일|화요일|수요일|목요일|금요일|토요일|일요일)[^.\\n]{0,30}(?:가능|된|괜찮)/.test(compact);
  const detailUserAvailability=/(?:나는|내가|저는|저도|나도|사용자)[^.\\n]{0,70}(?:월요일|화요일|수요일|목요일|금요일|토요일|일요일)[^.\\n]{0,30}(?:가능|괜찮|돼|된다|시간\\s*됨)/.test(compact);
  if(detailAlternativeDate && !detailUserAvailability){
    const alt=compact.match(/(다음\\s*주|다음주)\\s*(월요일|화요일|수요일|목요일|금요일|토요일|일요일)(?:\\s*(오전|오후|저녁))?/);
    const when=alt?[alt[1].replace(/\\s+/g," "),alt[2],alt[3]||""].filter(Boolean).join(" "):"상대가 제안한 날짜";
    out.replies=[
      {label:"일정 확인",text:`${when} 말씀하신 거 확인했어요. 제 일정 확인하고 다시 말씀드릴게요.`,reason:"상대의 대안 제안은 존중하되 사용자 일정이 확인되지 않아 확정하지 않습니다."},
      {label:"짧게",text:`${when} 가능 여부 확인해보고 말씀드릴게요.`,reason:"사용자의 미확인 가능 여부를 사실로 만들지 않습니다."},
      {label:"정중하게",text:`${when} 제안해주셔서 감사합니다. 일정 확인 후 말씀드릴게요.`,reason:"입력에 없는 기대감이나 수락을 새로 만들지 않습니다."}
    ];
    out.caution=`상대가 ${when}을(를) 제안했다는 사실과 사용자가 실제로 그 시간에 가능하다는 사실을 구분하세요. 사용자 가능 여부가 없으면 약속을 확정하지 마세요.`;
    out.dontSend=`사용자 일정이 확인되지 않았는데 '${when} 좋아요, 그때 봐요'처럼 확정하는 문장은 보내지 마세요.`;
    out.advice="상대가 대안 날짜를 제시한 것은 참여 행동으로 볼 수 있지만, 먼저 사용자의 실제 가능 여부를 확인해야 합니다.";
    out.nextAction=`사용자 일정에서 ${when} 가능 여부를 먼저 확인하세요. 가능하면 그때 약속을 확정하고, 불가능하면 사용자가 실제로 가능한 대안을 제시하세요.`;
  }

  // PRO confession: describe only participation facts that are actually present.'''
assert anchor in s, 'detail alternative insertion anchor missing'
s=s.replace(anchor,insert,1)

assert '2026-08-23-potentia-v41-availability-boundaries' in s
assert all(x in s for x in ['groundedAdvancedCafe','phonePasswordPressure','explainedSlowReply','detailAlternativeDate'])
p.write_text(s,encoding='utf-8')
print('v41 availability and boundary patch applied')
