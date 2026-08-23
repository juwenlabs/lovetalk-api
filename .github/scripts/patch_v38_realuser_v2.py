from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')
assert '2026-08-23-potentia-v37-grounded-followups' in s, 'expected v37 server not found'
s=s.replace('const SERVER_VERSION = "2026-08-23-potentia-v37-grounded-followups";', 'const SERVER_VERSION = "2026-08-23-potentia-v38-critical-followups";', 1)

old='''if(/(?:자해\\s*협박|자살|죽겠|죽을\\s*거|극단적\\s*선택)/.test(t)) return stop("자해 위협이 포함된 고위험 상황이에요.","연애 기술로 달래거나 책임을 떠안는 문장을 만들기보다 즉각적인 안전을 우선하세요. 급박한 위험이면 주변의 신뢰할 수 있는 사람이나 지역 응급·전문 도움을 연결하는 것이 우선입니다.");'''
new='''if(/(?:자해\\s*협박|자살|죽겠|죽어\\s*버리|죽어버리|죽을\\s*거|죽는다|극단적\\s*선택)/.test(t)) return stop("자해 위협이 포함된 고위험 상황이에요.","연애 기술로 달래거나 관계를 유지하는 조건으로 책임을 떠안지 마세요. 급박한 위험이면 주변의 신뢰할 수 있는 사람이나 지역 응급·전문 도움을 연결하고, 사용자의 안전과 경계를 함께 지키는 것이 우선입니다.");'''
assert old in s, 'self-harm starter guard anchor missing'
s=s.replace(old,new,1)

anchor='''  const firstDateNextDay='''
insert='''  const clubFirstMessage=/(?:동호회|모임)/.test(relation+" "+compact) && /(?:첫\\s*선톡|처음\\s*연락|번호\\s*교환|연락처\\s*교환)/.test(relation+" "+compact);
  if(clubFirstMessage){
    out.replies=[
      {label:"자연스럽게",text:"지난 모임에서 잠깐 이야기 나눴는데, 잘 지내셨어요?",reason:"입력에 있는 모임과 대화 맥락만 사용하고 날씨나 사용자의 감정을 새로 만들지 않습니다."},
      {label:"부담 없이",text:"지난 모임 이후로 처음 연락드리네요. 잘 지내셨어요?",reason:"첫 연락이라는 사실만 사용해 낮은 압력으로 대화를 엽니다."},
      {label:"조금 더 간결하게",text:"지난 모임에서 뵀었죠. 잘 지내셨어요?",reason:"입력에 없는 일정·날씨·호감 표현 없이 확인 가능한 공통 맥락만 씁니다."}
    ];
    return out;
  }

  const firstDateNextDay='''
assert anchor in s, 'starter policy insertion anchor missing'
s=s.replace(anchor,insert,1)

anchor='''  const compact=msg.replace(/\\s+/g," ");

  const initialMovieOneExchange='''
insert='''  const compact=msg.replace(/\\s+/g," ");

  const selfHarmCoercion=/(?:헤어지|이별|떠나|그만)[^.\\n]{0,50}(?:죽어\\s*버리|죽어버리|죽겠|자살|죽을\\s*거)|(?:죽어\\s*버리|죽어버리|죽겠|자살|죽을\\s*거)[^.\\n]{0,70}(?:헤어지|이별|떠나|그만)/.test(compact);
  if(selfHarmCoercion){
    return {
      meaning:"상대가 관계 유지 여부와 자신의 자해·죽음 위협을 연결하고 있다는 고위험 신호가 확인됩니다. 이것은 일반적인 연애 갈등이나 설득 문제로 다루지 않습니다.",
      emotion:"상대의 실제 의도나 위험 정도를 여기서 단정할 수는 없지만, 사용자가 관계를 유지해야 할 책임을 떠안는 방식으로 대응해서는 안 됩니다.",
      caution:"'내가 절대 안 떠날게'처럼 관계 유지 약속으로 위협을 진정시키려 하거나, 혼자서 상대의 안전을 전부 책임지지 마세요.",
      advice:"급박한 위험이 느껴지면 상대 가까이에 있는 신뢰할 수 있는 사람이나 지역의 응급·전문 도움을 연결하고, 사용자의 신변 안전과 경계를 함께 지키세요.",
      nextAction:"위협 내용을 보존하고 혼자 감당하지 마세요. 직접 대응이 필요하다면 안전 확인과 전문 도움 연결에만 초점을 두고, 관계를 유지하겠다는 약속을 조건으로 제시하지 마세요.",
      replies:[
        {label:"경계와 안전",text:"그 말을 가볍게 넘길 수는 없어. 지금 정말 위험하다면 가까운 사람이나 전문 도움을 바로 받아줘. 하지만 관계를 유지하는 조건으로 내가 책임질 수는 없어.",reason:"자해 위협을 심각하게 다루면서도 관계 유지 책임을 사용자에게 떠넘기지 않습니다."}
      ]
    };
  }

  const oneDayNoResponse=/(?:24\\s*시간|하루)[^.\\n]{0,60}(?:답(?:장)?(?:이)?\\s*(?:없|안)|무응답|읽씹)/.test(compact) || /(?:답(?:장)?(?:이)?\\s*(?:없|안)|무응답|읽씹)[^.\\n]{0,60}(?:24\\s*시간|하루)/.test(compact);
  if(oneDayNoResponse && !/(?:약속\\s*당일|오늘[^.\\n]{0,30}약속|응급|긴급)/.test(compact)){
    return {
      meaning:"비긴급 상황에서 마지막 메시지 후 약 24시간 동안 답이 없다는 사실만 확인됩니다. 하루 무응답만으로 관계 의도나 호감 변화를 확정할 수 없습니다.",
      emotion:"상대가 왜 답하지 않는지는 알 수 없으므로 바쁨·피곤함·관심 저하 같은 이유를 지어내지 않습니다.",
      caution:"24시간이 지났다고 지금 재촉 메시지를 보내거나, 여기서 다시 '3일을 추가'해 총 5~6일을 기다리는 식으로 계산하지 마세요.",
      advice:"초기 비긴급 무응답은 처음 메시지를 보낸 시점부터 총 약 3일을 기준으로 봅니다. 이미 하루가 지났다면 약 이틀 정도 더 기다리는 방향입니다.",
      nextAction:"지금은 새 메시지를 보내지 마세요. 처음 메시지를 보낸 시점 기준 약 3일이 됐는데도 답이 없고 아직 후속 연락을 한 번도 보내지 않았다면, 그때 낮은 압력의 확인을 딱 한 번만 고려하세요.",
      replies:[]
    };
  }

  const threeConsecutiveMessages=/(?:연속[^.\\n]{0,30}(?:3|세)\\s*번|(?:3|세)\\s*번[^.\\n]{0,30}(?:연속|먼저|연락|메시지))/.test(compact) && /(?:답(?:장)?(?:이)?\\s*(?:없|안)|무응답|읽씹|상대[^.\\n]{0,30}연락[^.\\n]{0,20}없)/.test(compact);
  if(threeConsecutiveMessages){
    return {
      meaning:"사용자가 이미 연속으로 여러 번 메시지를 보냈고 상대의 응답이나 자발적 참여가 확인되지 않는 상태입니다.",
      emotion:"무응답 이유는 알 수 없지만 현재 추가 메시지를 만드는 것은 사용자의 투자만 더 늘릴 가능성이 큽니다.",
      caution:"'(메시지 없음)' 같은 문구를 실제 추천문장처럼 보여주거나, 네 번째 확인·안부·명분 메시지를 만들지 마세요.",
      advice:"지금 필요한 것은 더 좋은 문장이 아니라 행동량을 줄이는 것입니다. 상대가 먼저 답하거나 구체적으로 참여할 때까지 새 메시지를 보내지 마세요.",
      nextAction:"추가 연락을 멈추고 상대의 자발적 반응을 기다리세요. 응답이 없다면 불안을 줄이기 위한 후속 메시지를 계속 추가하지 마세요.",
      replies:[]
    };
  }

  const oldFriendMeal=/(?:오래된\\s*친구|친구)/.test(relation) && /(?:다음엔|다음에)[^.\\n]{0,50}(?:둘이|단둘)[^.\\n]{0,40}(?:밥|식사)|(?:둘이|단둘)[^.\\n]{0,40}(?:밥|식사)[^.\\n]{0,50}(?:먹자|하자)/.test(compact);
  if(oldFriendMeal){
    return {
      meaning:"오래된 친구가 다음에는 둘이 식사하자는 구체적인 만남 의사를 표현한 사실이 확인됩니다. 다만 실제 가능한 날짜나 이번 주 일정은 입력에 없습니다.",
      emotion:"이 제안은 만남 참여 행동으로 볼 수 있지만 그것만으로 연애 감정을 확정할 수는 없습니다.",
      caution:"사용자의 일정 정보가 없는데 '이번 주 어때?'처럼 특정 기간이 가능하다고 가정하지 마세요. 숨은 마음을 확정하는 표현도 피하세요.",
      advice:"만남 제안 자체는 자연스럽게 받아들이고, 상대에게 가능한 날을 물어 실제 일정 정보를 얻은 뒤 조율하세요.",
      nextAction:"아래 문장 중 하나로 긍정적으로 반응한 뒤 상대의 가능한 날짜를 확인하세요.",
      replies:[
        {label:"가장 자연스럽게",text:"좋아. 언제가 편해?",reason:"사용자의 미확인 일정을 만들지 않고 상대의 실제 가능 시간을 확인합니다."},
        {label:"조금 더 편하게",text:"좋지. 편한 날 있으면 알려줘.",reason:"특정 주나 날짜를 임의로 가정하지 않습니다."},
        {label:"담백하게",text:"좋아, 날짜 한번 맞춰보자.",reason:"만남 제안을 수용하되 일정은 실제 정보가 나온 뒤 조율합니다."}
      ]
    };
  }

  const initialMovieOneExchange='''
assert anchor in s, 'quick deterministic insertion anchor missing'
s=s.replace(anchor,insert,1)

assert '2026-08-23-potentia-v38-critical-followups' in s
assert 'selfHarmCoercion' in s and 'oneDayNoResponse' in s and 'threeConsecutiveMessages' in s and 'oldFriendMeal' in s and 'clubFirstMessage' in s
p.write_text(s,encoding='utf-8')
print('Potentia v38 critical follow-ups patch applied')
