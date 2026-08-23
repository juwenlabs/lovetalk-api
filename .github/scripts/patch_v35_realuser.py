from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')
assert '2026-08-23-potentia-v34-balance-timing-guards' in s, 'expected v34 server not found'
s=s.replace('const SERVER_VERSION = "2026-08-23-potentia-v34-balance-timing-guards";', 'const SERVER_VERSION = "2026-08-23-potentia-v35-realuser-consistency";', 1)

old='''function getStarterGuard({message="",starterGoal="",selectedSituation=""}){
  const t=`${message} ${starterGoal} ${selectedSituation}`.toLowerCase().replace(/\\s+/g," ");'''
new='''function getStarterGuard({message="",starterGoal="",selectedSituation="",relation=""}){
  const t=`${relation} ${message} ${starterGoal} ${selectedSituation}`.toLowerCase().replace(/\\s+/g," ");'''
assert old in s, 'starter guard signature missing'
s=s.replace(old,new,1)

old='''  if(/(?:상사|직장\\s*상급자|교수|지도교수|권력관계).{0,50}(?:강요|압박|불이익|협박)/.test(t)) return stop("권력관계에서의 강압 가능성이 있는 상황이에요.","관계 기술보다 경계와 안전이 우선이에요. 불이익을 피하기 위한 사적·성적 요구에 응하도록 돕는 문장은 만들지 않습니다.");'''
new='''  if(/(?:상사|팀장|직장\\s*상급자|교수|지도교수|권력관계).{0,100}(?:강요|압박|불이익|협박)/.test(t) || /(?:상사|팀장|직장\\s*상급자|교수|지도교수|권력관계).{0,100}(?:진급|승진|평가|기회).{0,100}(?:단둘|둘이|술|사적|데이트|만나)/.test(t) || /(?:진급|승진|평가|기회).{0,80}(?:단둘|둘이|술|사적|데이트|만나).{0,80}(?:상사|팀장|교수)/.test(t)) return stop("권력관계에서 사적 만남과 인사상 이익이 연결된 압박 가능성이 있어요.","연애 기술로 부드럽게 맞추기보다 업무와 사적 관계의 경계를 지키는 것이 우선이에요. 대화 내용을 보존하고, 불이익 우려가 있으면 신뢰할 수 있는 내부 담당자나 외부 지원 경로를 검토하세요.");'''
assert old in s, 'power guard anchor missing'
s=s.replace(old,new,1)

old='''  const guard=getStarterGuard({message:context,starterGoal,selectedSituation});'''
new='''  const guard=getStarterGuard({message:context,starterGoal,selectedSituation,relation});'''
assert old in s, 'starter guard call anchor missing'
s=s.replace(old,new,1)

anchor='''  const contactFrequencyAgreement=relation.includes("연애")'''
insert='''  const repeatedShortNoReciprocity=/(?:질문을\\s*(?:한\\s*번도|한번도)\\s*안|역질문[^.\\n]{0,20}(?:없|안))/.test(compact) && /(?:그냥요|네|아니요|몰라요)/.test(compact) && /(?:최근|네\\s*번|4\\s*번|반복)/.test(compact);
  if(repeatedShortNoReciprocity){
    return {
      meaning:"최근 여러 차례 사용자가 질문을 이어갔지만 상대는 짧게만 답했고 역질문이 한 번도 없었다는 반복 행동이 확인됩니다. 이것은 호감 확률이 아니라 현재 대화 참여가 낮다는 행동 신호입니다.",
      emotion:"상대가 왜 짧게 답하는지는 알 수 없으므로 바쁘다·피곤하다·마음이 없다 같은 이유를 지어내지 않습니다.",
      caution:"없는 사정을 대신 만들어 배려 문장을 보내거나, 질문을 더 추가해 대화를 사용자가 혼자 끌고 가지 마세요. 참여가 낮은 상황에서 바로 만남 제안으로 건너뛰지도 마세요.",
      advice:"지금은 새 질문을 만들지 말고 사용자의 메시지 양을 줄여 상대가 스스로 대화를 시작하거나 질문하는지 확인하세요.",
      nextAction:"당분간 먼저 질문하거나 약속을 제안하지 말고 상대의 자발적 참여를 기다리세요. 이후에도 상대가 먼저 대화를 열거나 질문하지 않는 패턴이 반복되면 사용자의 투자를 더 줄이세요.",
      replies:[]
    };
  }

  const reciprocalDateReady=/서로[^.\\n]{0,50}질문|질문[^.\\n]{0,40}많이/.test(compact) && /상대[^.\\n]{0,50}카페/.test(compact) && /둘\\s*다[^.\\n]{0,50}토요일[^.\\n]{0,30}오후/.test(compact);
  if(reciprocalDateReady){
    return {
      meaning:"서로 질문이 이어지고 상대가 먼저 카페 이야기를 꺼냈으며, 두 사람 모두 이번 토요일 오후가 가능하다는 구체적 참여와 일정 정보가 확인됩니다.",
      emotion:"이 행동들은 만남 제안을 해볼 근거가 되지만 호감의 강도를 확정하는 점수는 아닙니다.",
      caution:"입력에 없는 카페 이름이나 임의의 시각을 확정해서 말하지 마세요. 한 메시지에는 질문을 하나만 두세요.",
      advice:"지금은 카톡만 더 이어가기보다 상대가 먼저 꺼낸 카페 맥락과 실제로 가능한 토요일 오후를 연결해 약속으로 전환하기 좋은 시점입니다.",
      nextAction:"아래 문장 중 하나로 토요일 오후 카페 약속을 제안하세요. 상대가 수락하면 그다음 메시지에서 구체적인 시간을 하나씩 조율하세요.",
      replies:[
        {label:"가장 자연스럽게",text:"토요일 오후에 그 카페 같이 가볼까요?",reason:"상대가 먼저 꺼낸 카페와 실제 공통 가능 시간을 한 번의 질문으로 연결합니다."},
        {label:"조금 더 편하게",text:"토요일 오후 괜찮으시면 그 카페 같이 가요.",reason:"이미 확인된 토요일 오후만 사용해 부담 낮은 제안을 합니다."},
        {label:"시간 조율까지 이어가기",text:"토요일 오후에 그 카페 가는 거 어떠세요? 편한 시간 알려주세요.",reason:"질문은 하나만 두고 수락 뒤 시간 조율로 자연스럽게 넘어갑니다."}
      ]
    };
  }

  const oneIllnessCancellation=/(?:내일|오늘)[^.\\n]{0,40}(?:만나|약속)/.test(compact) && /(?:몸이\\s*안\\s*좋|아프|컨디션)[^.\\n]{0,50}(?:취소|못\\s*만나|어렵)/.test(compact) && /(?:다른\\s*날짜|대안)[^.\\n]{0,30}(?:아직|없|말하지)/.test(compact);
  if(oneIllnessCancellation){
    return {
      meaning:"상대가 몸이 좋지 않다고 말하며 약속을 한 번 취소했고 아직 대안 날짜는 제시하지 않았다는 사실만 확인됩니다. 한 번의 취소만으로 만나기 싫다는 뜻을 확정할 수 없습니다.",
      emotion:"실제 건강 문제일 수도 있고 다른 이유가 있을 수도 있으므로 현재는 마음을 추정하기보다 이후의 자발적 재조율 행동을 보는 편이 정확합니다.",
      caution:"취소 직후 바로 새로운 날짜를 요구하거나 '저를 만나기 싫은 거죠?'처럼 확인을 압박하지 마세요. 침묵이나 냉정한 태도로 상대를 시험하지도 마세요.",
      advice:"지금은 취소를 짧게 받아주고 회복할 시간을 주세요. 다음 약속은 상대가 회복 후 연락하거나 일정에 참여하는지 본 뒤 조율하세요.",
      nextAction:"아래 문장 중 하나를 보내고 당장은 새 날짜를 묻지 마세요. 며칠 뒤에도 아무 소식이 없고 건강 상태가 걱정된다면 안부를 한 번만 확인할 수 있지만, 그때도 약속을 재촉하지 마세요.",
      replies:[
        {label:"가장 자연스럽게",text:"괜찮아요. 푹 쉬세요.",reason:"취소를 받아들이고 새 일정 압박을 만들지 않습니다."},
        {label:"조금 더 다정하게",text:"괜찮아요. 몸부터 잘 챙기세요. 나아지면 편할 때 연락 주세요.",reason:"상대에게 회복과 다음 연락의 선택권을 남깁니다."},
        {label:"조금 더 담백하게",text:"알겠어요. 무리하지 말고 푹 쉬세요.",reason:"한 번의 취소에 의미를 과하게 붙이지 않고 현재 상황만 반응합니다."}
      ]
    };
  }

  const receivedApology=relation.includes("연애") && /(?:상대|애인)[^.\\n]{0,80}(?:미안|사과)/.test(compact) && /(?:감정[^.\\n]{0,30}(?:가라앉|정리)|이제[^.\\n]{0,30}가라앉)/.test(compact);
  if(receivedApology){
    return {
      meaning:"상대가 먼저 자신의 말이 심했다고 사과했고 사용자의 감정도 많이 가라앉았다는 사실이 확인됩니다. 사용자가 잘못했다고 인정했다는 정보는 없습니다.",
      emotion:"상대의 사과는 회복 대화를 시작하려는 참여 행동으로 볼 수 있지만, 갈등 원인이 해결됐는지는 아직 별도입니다.",
      caution:"사용자가 잘못했다고 말하지 않았는데 '나도 미안해·나도 말이 심했어'처럼 책임을 새로 만들어내지 마세요. 사과를 받자마자 모든 문제가 끝났다고 덮지도 마세요.",
      advice:"상대의 사과를 받아들이고, 사용자가 실제로 감정이 가라앉았다는 범위 안에서 차분한 회복 대화로 이어가세요.",
      nextAction:"아래 문장 중 하나로 사과를 받아준 뒤 필요하면 갈등 원인을 차분하게 이야기할 시간을 잡으세요. 사용자의 책임이 따로 확인될 때만 그 부분을 구체적으로 사과하세요.",
      replies:[
        {label:"가장 자연스럽게",text:"먼저 말해줘서 고마워. 나도 이제 많이 가라앉았어. 우리 차분하게 얘기해보자.",reason:"사용자가 실제로 말한 감정 상태만 사용하고 없는 잘못을 인정하지 않습니다."},
        {label:"조금 더 다정하게",text:"사과해줘서 고마워. 나도 이제는 차분히 얘기할 수 있을 것 같아.",reason:"상대의 사과를 받아주면서 회복 대화 가능성을 엽니다."},
        {label:"조금 더 담백하게",text:"알겠어. 먼저 말해줘서 고마워. 이 일은 우리 차분하게 풀어보자.",reason:"쌍방 과실을 새로 만들지 않고 관계 회복에 초점을 둡니다."}
      ]
    };
  }

  const contactFrequencyAgreement=relation.includes("연애")'''
assert anchor in s, 'v35 deterministic insertion anchor missing'
s=s.replace(anchor,insert,1)

assert '2026-08-23-potentia-v35-realuser-consistency' in s
assert 'repeatedShortNoReciprocity' in s and 'reciprocalDateReady' in s and 'oneIllnessCancellation' in s and 'receivedApology' in s
assert 'relation=""' in s
p.write_text(s,encoding='utf-8')
print('Potentia v35 real-user consistency patch applied')
