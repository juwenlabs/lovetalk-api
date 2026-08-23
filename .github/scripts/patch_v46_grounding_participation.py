from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')
old='2026-08-23-potentia-v45-detail-role-binding'
new='2026-08-23-potentia-v46-grounding-participation-guards'
assert old in s, 'v45 base version missing'
s=s.replace(f'const SERVER_VERSION = "{old}";', f'const SERVER_VERSION = "{new}";', 1)

old_rejection='''  const explicitRomanticRejection=/(?:이성적으로[^.\\n]{0,20}(?:아니|아닌)|마음이\\s*없|더\\s*만나[^.\\n]{0,20}(?:않|안)|만나고\\s*싶지)/.test(compact);'''
new_rejection='''  const userOwnRomanticBoundary=/(?:나는|내가|저는|사용자)[^.\\n]{0,80}(?:이성적으로[^.\\n]{0,20}(?:아니|아닌)|마음이\\s*없|더\\s*만나[^.\\n]{0,20}(?:않|안)|만나고\\s*싶지|사적으로\\s*만나고\\s*싶지)/.test(compact);
  const explicitRomanticRejection=!userOwnRomanticBoundary && /(?:이성적으로[^.\\n]{0,20}(?:아니|아닌)|마음이\\s*없|더\\s*만나[^.\\n]{0,20}(?:않|안)|만나고\\s*싶지)/.test(compact);'''
assert old_rejection in s, 'romantic rejection anchor missing'
s=s.replace(old_rejection,new_rejection,1)

quick_anchor='''  const compact=msg.replace(/\\s+/g," ");

  const selfHarmCoercion='''
quick_insert='''  const compact=msg.replace(/\\s+/g," ");

  // Potentia grounding/participation guards: treat tentative plans, one-sided
  // initiation, one-off rejection, apologies, and workplace power pressure as
  // distinct structures before asking the model to invent a social strategy.
  const workplacePowerPressure=/(?:인사평가|성과평가|승진|평가)[^.\\n]{0,80}(?:술|한잔|둘이|단둘이|사적)/.test(compact) && /(?:상사|팀장|부장|직장)/.test(relation+" "+compact);
  if(workplacePowerPressure){
    return {
      meaning:"직장 상사가 업무상 평가와 사적인 만남을 연결해 제안하고 있고, 사용자는 사적으로 만나고 싶지 않다고 명확히 밝혔습니다. 일반적인 연애 신호가 아니라 권력관계와 경계의 문제입니다.",
      emotion:"사용자가 불편함이나 부담을 느낄 수 있는 구조이지만 구체적인 감정은 입력 이상으로 단정하지 않습니다.",
      caution:"평가를 잘 받기 위해 사적인 술자리를 받아들이라고 권하거나, 단둘이 만나서 오해를 풀라고 권하지 마세요. 사용자의 거절을 상대의 연애 거절로 뒤집어 해석하지도 마세요.",
      advice:"사적 만남은 짧고 분명하게 거절하고, 평가나 업무 이야기는 공식적인 업무 채널과 근무 맥락으로 돌리는 것이 안전합니다. 압박이 반복되면 관련 메시지를 보존하고 신뢰할 수 있는 내부 지원 경로를 검토하세요.",
      nextAction:"아래 문장 중 하나로 사적 술자리를 거절하고 업무 평가와 사적 만남을 분리해 달라고 전달하세요. 이후 같은 압박이 반복되면 기록을 남기고 혼자 대응 범위를 넓히지 마세요.",
      replies:[
        {label:"명확한 경계",text:"사적인 술자리는 어렵습니다. 평가 관련 내용은 업무 시간에 공식적으로 말씀 부탁드립니다.",reason:"업무 평가와 사적 만남을 분리하면서 사용자의 경계를 분명히 합니다."},
        {label:"조금 더 단정하게",text:"오늘 둘이 따로 만나는 자리는 참석하지 않겠습니다. 업무 관련 이야기는 회사에서 부탁드립니다.",reason:"사적 만남을 거절하되 불필요한 감정 추측을 넣지 않습니다."},
        {label:"기록에 남기기 좋은 답장",text:"인사평가와 사적인 자리는 별개로 진행해 주셨으면 합니다. 오늘 술자리는 어렵습니다.",reason:"상대가 실제로 연결한 두 요소를 분리해 달라는 경계를 문장에 남깁니다."}
      ]
    };
  }

  const tentativePlan=/(?:볼\\s*수도|만날\\s*수도|볼지도|만날지도|아직[^.\\n]{0,50}(?:일정|약속)[^.\\n]{0,30}확정[^.\\n]{0,15}(?:아니|안)|(?:일정|약속)[^.\\n]{0,30}(?:미확정|확정되지|확정\\s*전))/.test(compact);
  if(tentativePlan){
    return {
      meaning:"상대가 만남 가능성을 언급했지만 일정이 아직 확정되지 않았다는 사실만 확인됩니다. 약속이 잡힌 상태로 보기는 어렵습니다.",
      emotion:"이 표현만으로 상대가 꼭 만나고 싶어 한다거나 호감이 높다고 단정할 수 없습니다. 거절이라고 단정할 근거도 없습니다.",
      caution:"사용자가 말하지 않은 가능 시간이나 기대감·설렘을 만들지 말고, 상대의 잠정 표현을 확정 약속처럼 바꾸지 마세요.",
      advice:"일정이 정해지면 알려 달라고 짧게 답하고, 상대가 구체적인 날짜나 시간을 다시 제시할 때까지 약속을 확정하려고 밀어붙이지 않는 편이 좋습니다.",
      nextAction:"아래 문장 중 하나로 미확정 상태만 확인하고 기다리세요. 별도의 며칠짜리 추적 일정은 만들지 말고 상대가 구체화하는지 보세요.",
      replies:[
        {label:"가장 자연스럽게",text:"일정 정해지면 편하게 알려주세요.",reason:"상대의 미확정 상태만 받아들이고 사용자 일정이나 감정을 새로 만들지 않습니다."},
        {label:"조금 더 정중하게",text:"아직 미정이군요. 일정 확정되면 말씀해주세요.",reason:"잠정 제안을 확정 약속으로 바꾸지 않습니다."},
        {label:"가장 간결하게",text:"네, 일정 정해지면 알려주세요.",reason:"추가 제안이나 질문 없이 상대의 구체화를 기다립니다."}
      ]
    };
  }

  const repeatedUserInitiation=/(?:네\\s*번|4\\s*번|세\\s*번|3\\s*번|연속\\s*(?:3|4)\\s*번)[^.\\n]{0,90}(?:내가|사용자|나는|저는)[^.\\n]{0,50}먼저\\s*(?:연락|보냈|메시지)/.test(compact) && /(?:한두\\s*줄|짧게|질문[^.\\n]{0,30}(?:거의\\s*없|없))/ .test(compact);
  if(repeatedUserInitiation){
    return {
      meaning:"최근 여러 차례 사용자가 먼저 연락했고 상대는 답은 하지만 짧은 응답 위주이며 역질문이나 주도적 참여가 거의 없다는 패턴이 확인됩니다.",
      emotion:"이 패턴만으로 상대의 호감이 없다고 확정할 수는 없지만, 현재 대화 투자와 주도권은 사용자 쪽에 더 많이 기울어 있습니다.",
      caution:"오늘 또 새 화제를 만들어 보내거나 날씨·생각났다는 이유를 만들어 연락하지 마세요. 며칠 뒤 반드시 한 번 더 보내는 추적 일정도 만들지 마세요.",
      advice:"지금은 사용자의 선연락을 더 늘리지 않고 상대가 먼저 연락하거나 질문·약속 제안 등 구체적인 참여를 보이는지 확인하는 편이 좋습니다.",
      nextAction:"오늘은 새 메시지를 보내지 마세요. 상대가 먼저 구체적으로 참여하면 그 흐름에 답하고, 참여가 계속 없으면 사용자의 연락 횟수를 더 늘리지 마세요.",
      replies:[]
    };
  }

  const counterpartApology=/(?:상대(?:가|는)?[^.\\n]{0,80}(?:미안|사과)|(?:미안|사과)[^.\\n]{0,50}(?:상대가|상대는))/.test(compact);
  const userNoFault=/(?:나는|내가|저는|사용자)[^.\\n]{0,90}(?:잘못[^.\\n]{0,20}(?:없|안)|화난\\s*적\\s*없|화나지\\s*않)/.test(compact);
  if(counterpartApology && userNoFault){
    return {
      meaning:"상대가 자신의 연락이 늦었던 점을 먼저 사과했고, 사용자는 화난 적도 없고 자신의 잘못도 없다고 밝혔습니다.",
      emotion:"상대가 왜 늦었는지, 얼마나 미안한지, 이 사과가 호감 신호인지까지는 입력만으로 단정할 수 없습니다.",
      caution:"사용자가 잘못하지 않았는데 '나도 미안해'라고 만들거나, 상대가 바빴다고 추정하거나, 두 사람의 관계 속도를 새로 합의한 것처럼 말하지 마세요.",
      advice:"상대의 사과를 짧게 받아주면 충분합니다. 이유나 감정을 추가로 만들어 안심시키려 하지 않아도 됩니다.",
      nextAction:"아래 문장 중 하나로 사과를 받아주고 자연스럽게 다음 대화를 기다리세요.",
      replies:[
        {label:"가장 자연스럽게",text:"괜찮아요. 말씀해줘서 고마워요.",reason:"사과를 수용하는 사실만 전달합니다."},
        {label:"조금 더 정중하게",text:"괜찮습니다. 알려주셔서 감사해요.",reason:"상대가 바빴다는 등 입력에 없는 이유를 붙이지 않습니다."},
        {label:"가장 간결하게",text:"네, 괜찮아요.",reason:"사용자의 잘못이나 추가 감정을 만들지 않습니다."}
      ]
    };
  }

  const oneRejectionNoAlternative=/(?:한\\s*번|1\\s*번|한번)[^.\\n]{0,70}(?:거절|어렵|안\\s*되|못\\s*만나)/.test(compact) && /(?:대안|다른\\s*날짜|날짜\\s*제안)[^.\\n]{0,60}(?:없|안\\s*말|않)/.test(compact) && !/(?:다음\\s*주|다음주)[^.\\n]{0,60}(?:월요일|화요일|수요일|목요일|금요일|토요일|일요일)[^.\\n]{0,30}(?:가능|된|괜찮)/.test(compact);
  if(oneRejectionNoAlternative){
    return {
      meaning:"약속 제안이 한 번 거절됐고 상대가 대안 날짜는 제시하지 않았습니다. 한 번의 거절만으로 호감 여부를 확정할 수는 없습니다.",
      emotion:"실제 일정 문제인지 관심 부족인지 현재 정보만으로는 구분할 수 없습니다.",
      caution:"거절 직후 곧바로 다음 주·다른 날짜를 연달아 제안하거나 이유를 캐묻지 마세요. 반대로 한 번의 거절만으로 관계 종료를 단정하지도 마세요.",
      advice:"이번 거절은 짧게 받아들이고 다음 약속 제안은 상대가 구체적으로 참여하는지 본 뒤 결정하는 편이 균형에 맞습니다.",
      nextAction:"아래 문장 중 하나로 한 번 답하고 새 날짜를 바로 제안하지 마세요. 이후 상대가 먼저 일정이나 만남 이야기를 구체화하는지 보세요.",
      replies:[
        {label:"가장 자연스럽게",text:"알겠어요. 일정 괜찮아지면 편하게 말씀해주세요.",reason:"거절을 수용하고 다음 일정 제안의 공을 상대에게 넘깁니다."},
        {label:"조금 더 정중하게",text:"네, 알겠습니다. 여유 생기면 말씀해주세요.",reason:"추가 날짜를 즉시 제안하지 않습니다."},
        {label:"가장 간결하게",text:"알겠습니다. 편할 때 말씀해주세요.",reason:"압박 질문이나 추가 제안 없이 마무리합니다."}
      ]
    };
  }

  const selfHarmCoercion='''
assert quick_anchor in s, 'quick insertion anchor missing'
s=s.replace(quick_anchor,quick_insert,1)

# Fix an accidental space before .test introduced in the readable patch block.
s=s.replace('(?:거의\\s*없|없))/ .test(compact)', '(?:거의\\s*없|없))/.test(compact)', 1)

detail_anchor='''  const compact=msg.replace(/\\s+/g," ");
  const counterpart=compact.match('''
detail_insert='''  const compact=msg.replace(/\\s+/g," ");
  const vagueNextWeekPlan=/(?:다음\\s*주|다음주)[^.\\n]{0,55}(?:보자|만나자|한\\s*번\\s*보|한\\s*번\\s*만나)/.test(compact) && !/(?:월요일|화요일|수요일|목요일|금요일|토요일|일요일)/.test(compact);
  if(vagueNextWeekPlan){
    return {
      meaning:"상대가 다음 주 중 만남을 제안했지만 구체적인 요일과 시간은 정해지지 않았고, 사용자의 가능한 일정도 입력에 없습니다.",
      confidence:"중간",
      emotion:"상대가 만남을 언급한 것은 일정 조율에 참여한 행동이지만, 이것만으로 호감의 크기나 관계 단계를 확정할 수는 없습니다.",
      flow:"만남 의향은 언급됐지만 아직 날짜·시간과 사용자 가능 여부가 비어 있는 조율 전 단계입니다.",
      strategy:"구체적인 요일이나 시간을 임의로 만들지 말고, 상대가 일정을 구체화하면 그때 사용자의 실제 가능 여부를 확인합니다.",
      caution:"'저는 평일 저녁이 편해요'처럼 사용자가 말하지 않은 가능 시간을 만들거나 특정 요일·시간을 정해진 것처럼 제시하지 마세요.",
      dontSend:"입력에 없는 사용자 가능 요일·시간·장소를 사실처럼 넣은 문장은 보내지 마세요.",
      replies:[
        {label:"가장 자연스러운 답장",text:"다음 주 중이라고 하신 거 확인했어요. 요일 정해지면 제 일정도 확인해볼게요.",reason:"상대의 제안만 확인하고 사용자 가능 일정을 만들지 않습니다."},
        {label:"조금 더 간결한 답장",text:"요일 정해지면 말씀해주세요. 확인 후 답드릴게요.",reason:"구체적인 날짜나 시간을 새로 만들지 않습니다."},
        {label:"조금 더 정중한 답장",text:"다음 주 일정 구체화되면 말씀해주세요. 제 일정 확인해서 가능 여부 알려드릴게요.",reason:"약속을 성급히 확정하지 않고 양쪽 일정 확인을 남겨둡니다."}
      ],
      advice:"지금은 감정을 확대 해석하기보다 구체적인 일정이 나오는지 확인하는 것이 우선입니다.",
      nextAction:"상대가 요일이나 시간을 구체적으로 제시하면 그때 사용자의 실제 가능 여부를 확인해 답하세요. 별도의 하루이틀 추적 규칙은 만들지 마세요."
    };
  }
  const counterpart=compact.match('''
assert detail_anchor in s, 'detail insertion anchor missing'
s=s.replace(detail_anchor,detail_insert,1)

assert new in s
assert 'workplacePowerPressure' in s
assert 'tentativePlan' in s
assert 'repeatedUserInitiation' in s
assert 'oneRejectionNoAlternative' in s
assert 'vagueNextWeekPlan' in s
p.write_text(s,encoding='utf-8')
print('v46 grounding and participation guards applied')
