from pathlib import Path
p=Path('server.js')
s=p.read_text(encoding='utf-8')
assert '2026-08-23-potentia-v39-korean-selfharm-guard' in s
s=s.replace('const SERVER_VERSION = "2026-08-23-potentia-v39-korean-selfharm-guard";', 'const SERVER_VERSION = "2026-08-23-potentia-v40-grounded-normal-replies";', 1)

# Strengthen factual grounding: liking an activity is not proof of skill, and user preferences must not be invented.
anchor='''- 사용자가 말하지 않은 자신의 현재 행동·경험·감정도 지어내지 않는다.'''
insert='''- 상대가 어떤 활동을 “좋아한다”고 말한 것을 “잘한다·능숙하다”로 바꾸지 않는다. 좋아함과 실력은 다른 사실이다.\n- 사용자가 직접 말하지 않은 취향·관심사·경험을 “저도 좋아해요·저도 자주 해요”처럼 공통점으로 만들어내지 않는다.\n- 사용자가 말하지 않은 자신의 현재 행동·경험·감정도 지어내지 않는다.'''
assert anchor in s
s=s.replace(anchor,insert,1)

# Add deterministic cases before the existing initial-movie guard.
anchor='''  const initialMovieOneExchange='''
insert='''  const concreteAlternativeDate=/(?:이번\\s*주|이번주)[^.\\n]{0,40}(?:어렵|안\\s*되|힘들)/.test(compact) && /(?:다음\\s*주|다음주)[^.\\n]{0,50}(?:수요일|월요일|화요일|목요일|금요일|토요일|일요일)[^.\\n]{0,40}(?:오전|오후|저녁|시간|가능|된|괜찮)/.test(compact);
  if(concreteAlternativeDate){
    const m=compact.match(/(?:다음\\s*주|다음주)[^.\\n]{0,50}(?:수요일|월요일|화요일|목요일|금요일|토요일|일요일)[^.\\n]{0,30}(?:오전|오후|저녁)?/);
    const when=m?m[0].trim():"상대가 제안한 시간";
    return {
      meaning:`상대가 처음 제안된 시점은 어렵다고 했지만 ${when}을(를) 구체적인 대안으로 먼저 제시했습니다. 이것은 거절 후 대안 참여가 확인된 일정 조율 상황입니다.`,
      emotion:"구체적인 대안 날짜 제시는 만남 조율에 참여하는 행동이지만, 그것만으로 감정이나 호감의 크기를 확정하지 않습니다.",
      caution:"사용자가 말하지 않은 '기대돼요·기다려져요·설레요' 같은 감정을 답장에 새로 넣지 마세요. 이미 대안이 있으므로 다시 관계 의도를 확인하려고 압박하지도 마세요.",
      advice:"상대가 먼저 제시한 실제 대안을 그대로 받아 일정 확정으로 넘어가면 됩니다.",
      nextAction:`${when} 가능 여부를 짧게 확인하거나 수락한 뒤, 장소처럼 아직 정하지 않은 요소만 하나씩 조율하세요.`,
      replies:[
        {label:"가장 자연스럽게",text:`좋아요. ${when}으로 해요.`,reason:"상대가 실제로 제안한 시간만 사용해 간단히 확정합니다."},
        {label:"조금 더 정중하게",text:`좋습니다. 그럼 ${when}에 뵈어요.`,reason:"입력에 없는 감정을 보태지 않고 일정만 수락합니다."},
        {label:"다음 조율",text:`${when} 괜찮아요. 장소는 어디가 편하세요?`,reason:"확인된 시간은 유지하고 아직 정하지 않은 장소만 질문 하나로 조율합니다."}
      ]
    };
  }

  const appMatchCookingFirst=/(?:앱\\s*매칭|소개팅\\s*앱|매칭\\s*첫\\s*대화)/.test(relation) && /(?:요리[^.\\n]{0,30}좋아|좋아[^.\\n]{0,30}요리)/.test(compact) && /(?:아직[^.\\n]{0,30}답장|답장[^.\\n]{0,20}안)/.test(compact);
  if(appMatchCookingFirst){
    return {
      meaning:"상대가 첫 메시지에서 요리를 좋아한다고 자기 정보를 하나 공유했고 사용자는 아직 답장하지 않은 초기 대화입니다. 상대의 요리 실력이나 호감 수준은 확인되지 않았습니다.",
      emotion:"구체적인 관심사를 먼저 말한 것은 대화 소재를 제공한 행동으로 볼 수 있지만, 한 메시지만으로 감정이나 참여 수준을 확정하지 않습니다.",
      caution:"'요리 잘하시네요'처럼 좋아함을 실력으로 바꾸거나, 사용자가 말하지 않은 '저도 요리 좋아해요·저도 음식 얘기 좋아해요' 같은 가짜 공통점을 만들지 마세요.",
      advice:"상대가 실제로 말한 요리 관심사 안에서 질문 하나로 자연스럽게 대화를 이어가세요.",
      nextAction:"아래 문장 중 하나를 지금 답장하고, 이후 상대가 구체적으로 답하거나 역질문하는지 확인하세요.",
      replies:[
        {label:"가장 자연스럽게",text:"안녕하세요. 어떤 요리 좋아하세요?",reason:"상대가 실제로 말한 관심사만 사용합니다."},
        {label:"조금 더 구체적으로",text:"안녕하세요. 요리는 주로 어떤 걸 하세요?",reason:"실력을 단정하지 않고 경험을 묻습니다."},
        {label:"가볍게 이어가기",text:"안녕하세요. 최근에는 어떤 요리 해보셨어요?",reason:"사용자 취향을 새로 만들지 않고 상대가 공유한 주제를 확장합니다."}
      ]
    };
  }

  const initialMovieOneExchange='''
assert anchor in s, 'deterministic insertion anchor missing'
s=s.replace(anchor,insert,1)

assert '2026-08-23-potentia-v40-grounded-normal-replies' in s
assert 'concreteAlternativeDate' in s and 'appMatchCookingFirst' in s
p.write_text(s,encoding='utf-8')
print('v40 grounded normal-reply patch applied')
