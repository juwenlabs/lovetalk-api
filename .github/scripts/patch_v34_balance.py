from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')
assert '2026-08-23-potentia-v33-round2-quality-guards' in s, 'expected v33 server not found'
s=s.replace('const SERVER_VERSION = "2026-08-23-potentia-v33-round2-quality-guards";', 'const SERVER_VERSION = "2026-08-23-potentia-v34-balance-timing-guards";', 1)

anchor='''  const compact=msg.replace(/\\s+/g," ");

  const intentionalDelay='''
insert='''  const compact=msg.replace(/\\s+/g," ");

  const contactFrequencyAgreement=relation.includes("연애") && /(?:낮|업무|일할\\s*때)/.test(compact) && /(?:퇴근|저녁)/.test(compact) && /(?:서운|연락)/.test(compact);
  if(contactFrequencyAgreement){
    return {
      meaning:"상대는 낮 시간 연락 부족을 서운해하고, 사용자는 업무 중 즉시 답장이 어렵지만 퇴근 후에는 꾸준히 연락할 수 있다고 설명한 상황입니다. 핵심은 애정의 크기가 아니라 서로 가능한 연락 기준의 차이입니다.",
      emotion:"상대의 서운함은 확인되지만 사용자가 업무 중 바로 답하지 못하는 것을 무관심으로 단정할 근거는 없습니다.",
      caution:"사용자가 실제로 약속하지 않은 '퇴근하면 너한테만 집중할게' 같은 과한 보상 약속이나, 상대의 요구를 이기적이라고 몰아붙이는 표현은 피하세요.",
      advice:"업무 중 가능한 수준과 퇴근 후 가능한 수준을 사실대로 말하고, 둘 다 지속할 수 있는 연락 기준을 합의하세요.",
      nextAction:"오늘 안에 아래 문장 중 하나로 사용자의 실제 가능 범위를 설명한 뒤, 서로 편한 연락 기준을 짧게 맞춰보세요. 지킬 수 없는 약속을 크게 잡기보다 지속 가능한 기준을 만드는 것이 중요합니다.",
      replies:[
        {label:"가장 자연스럽게",text:"낮에는 일 때문에 바로 답하기 어려워. 대신 퇴근 후에는 꾸준히 연락할 수 있어. 우리 둘 다 편한 연락 기준을 같이 맞춰보자.",reason:"사용자가 실제로 가능한 범위만 말하고 연락 기준을 합의하는 문장입니다."},
        {label:"조금 더 다정하게",text:"네가 서운한 건 이해해. 나는 업무 중엔 바로 답하기 어렵고 퇴근 후엔 연락할 수 있어. 서로 부담 없는 방법을 같이 정해보자.",reason:"상대 감정을 인정하되 지키기 어려운 약속을 만들지 않습니다."},
        {label:"조금 더 간결하게",text:"일할 때는 바로 답하기 어렵다는 건 알아줬으면 해. 퇴근 후 연락은 꾸준히 할 수 있으니 우리한테 맞는 기준을 정해보자.",reason:"업무 제약과 가능한 대안을 사실대로 설명합니다."}
      ]
    };
  }

  const overInvestment=/(?:먼저\\s*연락|선연락)[^.\\n]{0,50}(?:거의|대부분|다)[^.\\n]{0,20}(?:제가|내가)|(?:제가|내가)[^.\\n]{0,50}(?:먼저\\s*연락|약속)[^.\\n]{0,50}(?:거의|대부분|다)/.test(compact) && /(?:밥값|선물|비용)/.test(compact) && /(?:상대|그 사람)[^.\\n]{0,80}(?:먼저\\s*연락|약속\\s*제안)[^.\\n]{0,40}(?:없|거의\\s*없|않)/.test(compact);
  if(overInvestment){
    return {
      meaning:"최근 한 달 동안 연락·약속 제안·식사비·선물 등 사용자의 행동 투자가 상대보다 훨씬 많고, 상대의 자발적 연락·약속 제안은 거의 없다는 사실이 확인됩니다.",
      emotion:"상대가 만날 때 친절하다는 사실만으로 호감의 강도나 향후 관계 의지를 확정할 수는 없습니다. 현재는 친절함보다 자발적 참여의 부족을 더 중요하게 볼 필요가 있습니다.",
      caution:"더 좋은 문장, 더 많은 선물, 추가 식사비, 반복 선연락으로 상대의 참여를 만들어내려 하지 마세요. 3일 뒤 확인 연락처럼 사용자의 행동량을 다시 늘리는 것도 지금은 맞지 않습니다.",
      advice:"지금은 새 메시지를 만드는 것보다 사용자의 행동량을 줄이고 상대가 스스로 연락하거나 약속을 제안하는지 확인하는 편이 맞습니다.",
      nextAction:"당분간 먼저 연락·약속 제안·선물·비용 지출을 추가하지 말고 상대의 자발적 참여를 기다리세요. 상대가 먼저 구체적으로 연락하거나 약속에 참여하면 그때 비슷한 수준으로 반응하고, 변화가 없으면 관계에 투입하는 시간과 감정을 줄이세요.",
      replies:[]
    };
  }

  const storyNoReply=/스토리/.test(compact) && /(?:답(?:이|장)?\\s*(?:없|안)|읽씹|무응답)/.test(compact);
  const elapsedKnown=/(?:\\d+\\s*시간|하루|1\\s*일|이틀|2\\s*일|사흘|3\\s*일|며칠|어제|그제)/.test(compact);
  if(storyNoReply && !elapsedKnown){
    return {
      meaning:"카톡 답은 없고 스토리를 봤다는 사실만 확인됩니다. 스토리 조회는 카톡에 답할 의사나 숨은 호감을 확정하는 근거가 아닙니다.",
      emotion:"상대가 관심이 있어서 일부러 답을 미루는지, 단순히 스토리만 본 것인지 현재 정보만으로 판단할 수 없습니다.",
      caution:"스토리 조회를 근거로 '관심 있는데 밀당한다'고 단정하거나, 마지막 메시지를 보낸 지 얼마나 됐는지 확인하지 않은 채 바로 후속 연락을 보내지 마세요.",
      advice:"먼저 마지막 메시지를 보낸 뒤 얼마나 지났는지를 기준으로 행동하세요. 비긴급 초기 관계라면 약 3일이 안 됐다면 기다리고, 약 3일이 지났고 아직 후속 연락을 한 번도 안 했다면 그때 낮은 압력의 확인을 한 번만 할 수 있습니다.",
      nextAction:"지금은 스토리 조회 자체로 새 메시지를 만들지 마세요. 마지막 메시지 후 약 3일이 지났는지 확인하고, 아직이라면 기다리세요. 이미 한 번 후속 연락까지 했다면 추가 연락 없이 멈추세요.",
      replies:[]
    };
  }

  const reunionSingleSignal=relation.includes("이별") && /헤어진/.test(compact) && /보고\\s*싶/.test(compact) && /(?:바로|재회|다시\\s*만나|다시\\s*사귀)/.test(compact);
  if(reunionSingleSignal){
    return {
      meaning:"헤어진 뒤 한 달 만에 상대가 '보고 싶다'고 먼저 연락한 것은 새로운 참여 행동이지만, 한 문장만으로 재회 의사·이별 원인 해결·관계 변화가 확인된 것은 아닙니다.",
      emotion:"상대가 그리움이나 외로움을 느꼈을 가능성은 있지만, 지금 바로 다시 사귀고 싶다는 뜻으로 확정할 수 없습니다.",
      caution:"한 문장에 반응해 바로 재회를 확정하거나 이전 이별 원인이 해결됐다고 가정하지 마세요. 사용자가 실제로 느낀다고 말하지 않은 감정을 덧붙이지도 마세요.",
      advice:"먼저 왜 지금 연락했는지와 이전 문제를 다시 다룰 의지가 있는지 대화로 확인하세요. 재회 결정은 그 대화 이후에 하는 편이 안전합니다.",
      nextAction:"아래 문장 중 하나로 대화를 열고 상대가 왜 지금 연락했는지, 이전 이별 원인을 함께 다룰 의지가 있는지 확인하세요. 말뿐 아니라 이후의 구체적인 참여가 확인된 뒤 만남이나 재회를 결정하세요.",
      replies:[
        {label:"가장 자연스럽게",text:"연락한 이유가 궁금해. 지금 어떤 마음으로 연락한 건지 먼저 얘기해볼 수 있을까?",reason:"보고 싶다는 한 문장을 바로 재회 약속으로 바꾸지 않고 의도를 확인합니다."},
        {label:"조금 더 차분하게",text:"나도 우리 얘기를 다시 해볼 마음은 있어. 다만 바로 다시 시작하기보다 우리가 왜 헤어졌는지부터 차분히 얘기하고 싶어.",reason:"사용자가 아직 마음이 있다는 입력 범위 안에서 재회보다 원인 확인을 먼저 둡니다."},
        {label:"조금 더 신중하게",text:"보고 싶다고 연락해준 건 알겠어. 다시 만나기 전에 예전 문제와 지금 달라진 점부터 얘기해보자.",reason:"감정 한 줄보다 관계 변화와 회복 가능성을 먼저 확인합니다."}
      ]
    };
  }

  const intentionalDelay='''
assert anchor in s, 'v34 deterministic insertion anchor missing'
s=s.replace(anchor,insert,1)

assert '2026-08-23-potentia-v34-balance-timing-guards' in s
assert 'overInvestment' in s and 'storyNoReply' in s and 'reunionSingleSignal' in s and 'contactFrequencyAgreement' in s
p.write_text(s,encoding='utf-8')
print('Potentia v34 balance/timing guards applied')
