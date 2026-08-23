from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')
old='2026-08-23-potentia-v46-grounding-participation-guards'
new='2026-08-23-potentia-v47-boundaries-followup-grounding'
assert old in s, 'v46 base version missing'
s=s.replace(f'const SERVER_VERSION = "{old}";', f'const SERVER_VERSION = "{new}";', 1)

anchor='''  const compact=msg.replace(/\\s+/g," ");

  // Potentia grounding/participation guards: treat tentative plans, one-sided'''
insert='''  const compact=msg.replace(/\\s+/g," ");

  // v47: deterministic grounding for first-meetup neutrality, explicit friend-only
  // boundaries, promised callbacks, credential pressure, and repeated ex-contact.
  const firstMeetupContext=/(?:첫\\s*소개팅|소개팅\\s*다음날)/.test(relation) || /(?:어제|오늘)[^.\\n]{0,40}처음\\s*만났/.test(compact);
  const userExplicitMeetupFeeling=/(?:나는|내가|저는|사용자)[^.\\n]{0,100}(?:즐거웠어|즐거웠어요|재밌었어|재밌었어요|좋았어|좋았어요|마음에\\s*들었어|마음에\\s*들었어요|별로였어|별로였어요|아쉬웠어|아쉬웠어요)/.test(compact);
  if(firstMeetupContext && !userExplicitMeetupFeeling){
    return {
      meaning:"첫 만남 뒤 상대가 감사와 귀가 안부를 전했다는 사실만 확인됩니다. 사용자는 만남이 좋았는지 별로였는지 자신의 평가를 아직 말하지 않았습니다.",
      emotion:"상대의 한 번의 인사만으로 호감 강도나 다음 만남 의지를 확정할 수 없고, 사용자의 즐거움·호감도 입력에 없으므로 새로 만들지 않습니다.",
      caution:"'저도 재밌었어요·즐거웠어요·만나서 좋았어요'처럼 사용자가 말하지 않은 감정을 넣거나 다음 약속을 새로 만들지 마세요.",
      advice:"상대의 감사와 안부에만 중립적으로 답하면 충분합니다. 사용자의 실제 평가가 확인되기 전에는 긍정 감정을 대신 만들어 보내지 마세요.",
      nextAction:"아래 문장 중 하나로 귀가와 감사에만 답한 뒤 상대의 다음 참여를 자연스럽게 보세요.",
      replies:[
        {label:"가장 자연스럽게",text:"저도 잘 들어갔어요. 오늘 감사합니다.",reason:"확인된 귀가와 감사만 답하고 사용자의 미확인 감정을 만들지 않습니다."},
        {label:"조금 더 부드럽게",text:"네, 저도 잘 들어왔어요. 연락 주셔서 고마워요.",reason:"상대가 실제로 연락한 사실만 받아줍니다."},
        {label:"조금 더 정중하게",text:"저도 무사히 들어왔습니다. 오늘 감사했어요.",reason:"다음 약속이나 즐거웠다는 평가를 추가하지 않습니다."}
      ]
    };
  }

  const explicitFriendOnly=/(?:상대가|상대는|상대)[^.\\n]{0,120}친구로\\s*지내/.test(compact) || /[\"“']?좋은\\s*사람[^.\\n]{0,80}친구로\\s*지내/.test(compact);
  if(explicitFriendOnly){
    return {
      meaning:"상대가 연애 관계가 아니라 친구로 지내고 싶다는 경계를 명확하게 표현했습니다. 이 말은 그대로 존중해야 합니다.",
      emotion:"'좋은 사람'이라는 표현은 긍정적인 예의 표현일 수 있지만, 그 자체를 연애 호감이나 나중에 마음이 바뀔 가능성의 근거로 해석하지 않습니다.",
      caution:"한 번만 더 만나 달라고 설득하거나, 기다리겠다고 하거나, 친구 관계를 이용해 연애 가능성을 다시 열어두지 마세요.",
      advice:"짧게 수용하고 연애 방향의 추가 설득을 멈추는 것이 맞습니다. 이후 친구로 연락을 이어갈지는 두 사람의 자연스러운 상호 참여가 있을 때만 판단하세요.",
      nextAction:"아래 문장 중 하나로 상대의 뜻을 한 번 수용한 뒤 연애 설득이나 재접근을 중지하세요.",
      replies:[
        {label:"깔끔하게 수용",text:"알겠습니다. 솔직하게 말씀해주셔서 감사합니다.",reason:"상대의 명확한 경계를 그대로 받아들입니다."},
        {label:"짧게",text:"네, 뜻 존중할게요.",reason:"추가 설득이나 미래 가능성을 만들지 않습니다."},
        {label:"부드럽게 마무리",text:"알겠어요. 말씀해줘서 고마워요.",reason:"연애 관계를 다시 열어두지 않고 대화를 정리합니다."}
      ]
    };
  }

  const promisedCallback=/(?:상대가|상대는|상대)[^.\\n]{0,180}(?:내가|자기가)?\\s*먼저\\s*연락(?:할게|하겠|드릴게)/.test(compact);
  const aboutOneDay=/(?:하루|1\\s*일)[^.\\n]{0,40}(?:지났|경과|됐)/.test(compact);
  if(promisedCallback && aboutOneDay && !/(?:오늘[^.\\n]{0,30}약속|약속\\s*당일|응급|긴급)/.test(compact)){
    return {
      meaning:"상대가 일정이 확정되면 먼저 연락하겠다고 명시했고 그 뒤 약 하루가 지난 비긴급 상황입니다. 현재는 상대가 약속한 연락을 기다리는 단계입니다.",
      emotion:"하루가 지났다는 사실만으로 관심 저하나 마음 변화를 판단할 수 없습니다.",
      caution:"지금 확인 메시지를 보내거나, 오늘부터 다시 3~4일을 추가로 세는 새 대기 규칙을 만들지 마세요.",
      advice:"지금은 새 메시지를 보내지 말고 상대가 먼저 연락하겠다는 말을 존중하세요. 비긴급 무응답 판단은 별도의 추가 대기일이 아니라 그 말을 들은 시점부터 총 약 3일 기준으로 봅니다.",
      nextAction:"지금은 기다리세요. 상대가 먼저 연락하겠다고 한 시점부터 총 약 3일이 지나도 연락이 없고 후속 확인을 한 적이 없다면 그때 낮은 압력의 확인을 한 번만 고려하세요.",
      replies:[]
    };
  }

  const loginCredentialPressure=(/(?:SNS|인스타|계정|로그인)[^.\\n]{0,50}(?:인증번호|인증\\s*코드|OTP)/i.test(compact) || /(?:인증번호|인증\\s*코드|OTP)[^.\\n]{0,50}(?:SNS|인스타|계정|로그인)/i.test(compact)) && /(?:계속|반복|싫다고|거절|사랑하면|보내야|요구)/.test(compact);
  if(loginCredentialPressure){
    return {
      meaning:"상대가 계정 접근에 사용되는 로그인 인증번호를 반복해서 요구하고 사용자가 거절했는데도 사랑을 조건으로 압박하고 있습니다. 일반적인 연애 신뢰 문제가 아니라 계정 보안과 경계 문제입니다.",
      emotion:"상대의 정확한 동기는 단정할 수 없지만, 사용자의 거절을 무시하고 계정 접근 정보를 요구하는 행동 자체는 확인됩니다.",
      caution:"인증번호를 제공하거나, 신뢰를 증명하기 위해 계정 접근을 허용하거나, 문제 해결을 위해 통화·대면 만남을 해야 한다고 권하지 마세요.",
      advice:"인증번호는 공유하지 말고 짧고 분명하게 요구 중단을 전달하세요. 압박이 계속되면 대화를 줄이고 계정 보안과 사용자의 거리를 우선하세요.",
      nextAction:"아래 문장 중 하나로 경계를 한 번 분명히 전달하세요. 이후에도 인증번호 요구나 압박이 반복되면 같은 논쟁을 이어가지 말고 연락을 줄이세요.",
      replies:[
        {label:"명확한 경계",text:"로그인 인증번호는 공유하지 않을게. 이 요구는 더 이상 하지 말아줘.",reason:"계정 접근 정보를 관계의 신뢰 증명으로 넘기지 않습니다."},
        {label:"압박 중단",text:"인증번호는 줄 수 없어. 이미 거절했으니 계속 요구하지 말아줘.",reason:"사용자의 기존 거절을 분명히 반복합니다."},
        {label:"거리두기",text:"이 요구가 계속되면 이 대화는 여기서 멈출게.",reason:"통화나 대면 만남을 강요하지 않고 반복 압박에 행동 경계를 둡니다."}
      ]
    };
  }

  const repeatedExMeetingPressure=/(?:헤어진|이별한|전\\s*연인|전남친|전여친)/.test(relation+" "+compact) && /(?:나는|내가|저는|사용자)[^.\\n]{0,100}(?:만나고\\s*싶지|만날\\s*생각\\s*없|만나지\\s*않)/.test(compact) && /(?:계속|자꾸|반복|거절해도)[^.\\n]{0,80}(?:만나|보자|만남)/.test(compact);
  if(repeatedExMeetingPressure){
    return {
      meaning:"헤어진 상대가 반복해서 대면 만남을 요구하고 있고 사용자는 만나고 싶지 않다고 분명히 밝혔습니다. 사용자의 경계를 우선해야 하는 상황입니다.",
      emotion:"상대가 왜 계속 만나려는지는 추정하지 않습니다. 확인되는 것은 반복된 만남 요구와 사용자의 거절 의사입니다.",
      caution:"미안함이나 고마움을 사용자가 느낀 것처럼 만들어 완곡하게 여지를 주거나, 마지막으로 한 번 만나서 정리하라고 권하지 마세요.",
      advice:"이미 만남을 여러 번 거절했다면 같은 설명을 계속 반복할 필요가 없습니다. 필요하다면 한 번의 최종 경계만 전달하고 이후 반복 요구에는 답하지 않는 편이 안전합니다.",
      nextAction:"이미 분명하게 거절했다면 새 메시지를 보내지 않아도 됩니다. 아직 연락 중단 경계를 말하지 않았고 한 번 더 정리하고 싶다면 아래 문장 중 하나만 보내고, 이후 반복 요청에는 답하지 말고 필요하면 차단을 검토하세요.",
      replies:[
        {label:"최종 경계",text:"나는 만나지 않겠어. 더 이상 만남을 요청하지 말아줘.",reason:"사용자의 실제 의사만 분명히 전달합니다."},
        {label:"연락 경계",text:"만날 의사가 없어. 이 얘기로 계속 연락하지 말아줘.",reason:"추가 설명이나 감정을 만들지 않고 반복 요구를 중단시킵니다."},
        {label:"이미 충분히 거절했다면",text:"새 메시지를 보내지 마세요.",reason:"이미 경계를 여러 번 전달했다면 추가 응답이 필요하지 않습니다."}
      ]
    };
  }

  // Potentia grounding/participation guards: treat tentative plans, one-sided'''
assert anchor in s, 'quick-analysis v47 insertion anchor missing'
s=s.replace(anchor,insert,1)

p.write_text(s,encoding='utf-8')
print('patched',new)
