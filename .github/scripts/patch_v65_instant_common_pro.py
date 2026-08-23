from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')
old='const SERVER_VERSION = "2026-08-23-potentia-v64-compact-pro-grounded";'
new='const SERVER_VERSION = "2026-08-23-potentia-v65-instant-common-pro";'
if old not in s: raise SystemExit('v64 marker missing')
s=s.replace(old,new,1)

anchor='async function generateCompactProResult(reqBody){\n'
if anchor not in s: raise SystemExit('compact pro anchor missing')
helper=r'''function getInstantCompactProResult(reqBody,task){
  const raw=String(reqBody?.message||"");
  const marker="[사용자 입력]";
  const text=(raw.includes(marker)?raw.slice(raw.lastIndexOf(marker)+marker.length):raw.replace(/^\s*\[PRO[^\]]+\]\s*/,"")).trim().replace(/\s+/g," ");
  if(!text) return null;

  if(task==="confession"){
    const mutual=/(?:서로[^.\n]{0,60}질문|질문[^.\n]{0,60}주고받|상대도[^.\n]{0,40}질문)/.test(text);
    const hasMeeting=/(?:만났|만남|데이트|대면|단둘이)/.test(text);
    const hasInitiative=/(?:상대(?:가|는|도)?[^.\n]{0,90}(?:먼저\s*연락|선연락|약속\s*제안|만남\s*제안|날짜\s*제안))/.test(text);
    if(mutual && !hasMeeting && !hasInitiative){
      return {
        meaning:"서로 일상 대화와 질문을 주고받는 참여는 확인되지만, 이것만으로 고백 타이밍이 됐다고 보기는 어렵습니다.",
        confidence:"낮음",
        emotion:"상대가 대화에 참여한다는 사실은 확인되지만 연애 감정이나 고백 수용 의사는 입력에 없습니다.",
        flow:"현재 확인되는 것은 양방향 대화 참여입니다. 실제 만남, 상대의 선연락, 구체적 일정 참여 여부는 아직 확인되지 않았습니다.",
        strategy:"고백을 서두르지 말고 실제 만남과 상대의 자발적 연락·대화 재개·일정 참여가 확인되는지 먼저 보세요.",
        caution:"상호 질문만으로 상대의 호감이나 고백 수용 가능성을 높게 단정하지 마세요.",
        dontSend:"입력에 없는 호감이나 특별한 관계를 전제로 한 고백·떠보기 메시지는 지금 보내지 마세요.",
        advice:"지금은 고백 문장보다 상대의 자발적 참여가 실제 행동으로 이어지는지 확인하는 단계입니다.",
        nextAction:"실제 만남 여부와 상대의 선연락·대화 재개·구체적 일정 참여를 확인하세요. 그 정보가 생기기 전에는 고백을 확정하지 마세요.",
        replies:[]
      };
    }
  }

  if(task==="date"){
    const mentionsMovie=/영화/.test(text);
    const userAvailability=/(?:나는|내가|저는|저도|나도|사용자)[^.\n]{0,100}(?:월요일|화요일|수요일|목요일|금요일|토요일|일요일|오늘|내일|이번\s*주|다음\s*주)[^.\n]{0,60}(?:가능|괜찮|시간\s*돼|시간\s*되)/.test(text);
    const concreteInvite=/(?:같이|함께)[^.\n]{0,40}(?:보자|볼래|갈래|만나)|(?:언제|이번|다음)[^.\n]{0,50}(?:보자|만나자)/.test(text);
    if(mentionsMovie && !userAvailability && !concreteInvite){
      return {
        meaning:"상대가 영화 이야기를 했다는 사실은 확인되지만, 그 자체를 만남 의향이나 호감 신호로 단정할 수는 없습니다.",
        confidence:"낮음",
        emotion:"영화 주제에 참여했다는 행동만 확인됩니다. 함께 보고 싶다는 의사나 감정 강도는 입력에 없습니다.",
        flow:"대화가 이어지고 영화 주제가 나왔지만, 선연락·약속 제안·구체적 일정 참여 여부는 확인되지 않았습니다.",
        strategy:"지금은 영화 주제를 자연스럽게 이어가며 상대의 실제 참여를 한 번 더 확인하고, 사용자의 가능한 일정이 확인된 뒤에만 만남을 제안하세요.",
        caution:"입력에 없는 날짜·시간·장소나 사용자의 영화 취향을 만들어 약속을 제안하지 마세요.",
        dontSend:"사용자 일정이 확인되지 않은 상태에서 특정 날짜나 장소를 정해 만남을 확정하지 마세요.",
        advice:"영화 주제를 이어가면서 상대가 구체적으로 참여하는지 먼저 보는 편이 안전합니다.",
        nextAction:"먼저 사용자의 실제 가능한 일정을 확인하세요. 일정이 확인되기 전에는 영화 이야기만 자연스럽게 이어가세요.",
        replies:[
          {label:"가장 자연스러운 답장",text:"어떤 영화 좋아하세요?",reason:"상대가 실제로 꺼낸 영화 주제만 사용합니다."},
          {label:"조금 더 구체적인 답장",text:"최근에 본 영화 중에 추천할 만한 거 있어요?",reason:"사용자의 취향이나 일정을 만들지 않고 대화를 이어갑니다."},
          {label:"가볍게 이어가는 답장",text:"영화는 어떤 장르 좋아하세요?",reason:"약속을 서두르지 않고 상대의 참여를 확인합니다."}
        ]
      };
    }
  }

  if(task==="risk"){
    const passwordPressure=/(?:비밀번호|패스워드|인증번호|OTP|로그인\s*코드)/i.test(text) && /(?:계속|반복|싫다고|거절|사랑하면|알려|공유|요구)/.test(text);
    if(passwordPressure){
      return {
        meaning:"상대가 계정 접근 정보나 비밀번호를 요구하고 사용자가 거절했는데도 압박하는 행동이 확인됩니다. 이는 일반적인 호감 신호가 아니라 보안과 경계 문제입니다.",
        confidence:"높음",
        emotion:"상대의 정확한 의도는 단정하지 않지만, 사용자의 거절을 무시하고 민감한 계정 정보를 요구하는 행동 자체는 확인됩니다.",
        flow:"현재 핵심은 관계 해석이 아니라 사용자의 명확한 거절과 상대의 반복 요구입니다.",
        strategy:"비밀번호·인증번호는 공유하지 말고 요구 중단을 분명히 하세요. 압박이 반복되면 대화를 줄이고 계정 보안을 우선하세요.",
        caution:"사랑이나 신뢰를 증명하기 위해 계정 정보를 넘기거나, 거절한 뒤에도 계속 설득에 응하지 마세요.",
        dontSend:"비밀번호나 인증번호를 보내거나 일부만 공유하는 식으로 타협하지 마세요.",
        advice:"계정 접근 정보는 공유하지 않는 것이 맞습니다. 사용자의 거절을 반복해서 무시하는 행동이 계속되는지도 함께 보세요.",
        nextAction:"비밀번호나 인증번호를 공유하지 마세요. 필요하면 요구를 중단해 달라고 한 번 명확히 말하고, 반복되면 연락과 계정 접근을 더 제한하세요.",
        replies:[]
      };
    }
    const occasionalNudge=/답장[^.\n]{0,30}재촉|재촉[^.\n]{0,30}답장/.test(text);
    const uncertainRepeat=/(?:가끔|한두\s*번|아직[^.\n]{0,35}(?:반복|계속)[^.\n]{0,20}(?:모르|확인|아니)|반복되는지[^.\n]{0,25}모르)/.test(text);
    if(occasionalNudge && uncertainRepeat){
      return {
        meaning:"확인된 사실은 상대가 답장을 재촉한 적이 있다는 점입니다. 반복 빈도와 구체적 맥락이 부족해 일회성인지 지속적인 압박 패턴인지는 아직 판단할 수 없습니다.",
        confidence:"낮음",
        emotion:"답장 재촉만으로 상대의 호감·불안·의도를 추정하지 않습니다. 현재 입력만으로 상대 감정을 확정할 근거가 없습니다.",
        flow:"재촉 표현은 관심 신호로 환산하지 않습니다. 반복 여부, 즉시 답변 요구, 비난, 사용자의 경계 무시 같은 실제 행동이 함께 나타나는지를 봐야 합니다.",
        strategy:"사용자의 평소 답장 리듬을 유지하고 같은 압박이나 경계 무시가 실제로 반복되는지 다음 대화에서 확인하세요.",
        caution:"한두 번의 재촉만으로 상대를 집착한다고 단정하거나, 반대로 관심 표현이라고 좋게 해석하지 마세요.",
        dontSend:"죄책감 때문에 계속 미안하다고 하거나 일부러 더 늦게 답하는 밀당은 하지 마세요.",
        advice:"현재는 위험도를 확정하기보다 반복성과 경계 존중 여부를 확인하는 단계입니다.",
        nextAction:"다음에 재촉 표현이 다시 나오면 그 표현과 맥락을 확인하세요. 반복 압박이나 경계 무시가 실제로 확인되면 그때 명확한 경계를 설정하세요.",
        replies:[]
      };
    }
  }
  return null;
}

'''
s=s.replace(anchor,helper+anchor,1)

old_block='''  const task=getCompactProTask(reqBody?.message);
  if(!task) return null;
  const {relation,nickname,message,tone,image,images,profile,recentMemory,selectedSituation}=reqBody||{};'''
new_block='''  const task=getCompactProTask(reqBody?.message);
  if(!task) return null;
  const instant=getInstantCompactProResult(reqBody,task);
  if(instant) return instant;
  const {relation,nickname,message,tone,image,images,profile,recentMemory,selectedSituation}=reqBody||{};'''
if old_block not in s: raise SystemExit('task block missing')
s=s.replace(old_block,new_block,1)

p.write_text(s,encoding='utf-8')
