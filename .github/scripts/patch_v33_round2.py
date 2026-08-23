from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')

assert '2026-08-23-potentia-v32-critical-quick-guards' in s, 'expected v32 server not found'
s=s.replace('const SERVER_VERSION = "2026-08-23-potentia-v32-critical-quick-guards";', 'const SERVER_VERSION = "2026-08-23-potentia-v33-round2-quality-guards";', 1)

old='''function sanitizeReplyObject(obj,situation,label){
  const out=(obj&&typeof obj==="object")?obj:{label,text:String(obj||""),reason:""};
  const text=String(out.text||"").trim();
  const banned=["싸워줘서 고마워","화내줘서 고마워","상처 줘서 고마워","읽씹해줘서 고마워"];
  if(!text || banned.some(x=>text.includes(x))) return safeFallbackReply(situation,out.label||label||"추천");
  return {label:out.label||label||"추천",text,reason:String(out.reason||"").trim()};
}'''
new='''function enforceSingleQuestionText(raw){
  const text=String(raw||"").trim();
  const count=(text.match(/\\?/g)||[]).length;
  if(count<=1)return text;
  const parts=text.split("?").map(x=>x.trim()).filter(Boolean);
  if(!parts.length)return text;
  return parts[parts.length-1]+"?";
}
function sanitizeReplyObject(obj,situation,label){
  const out=(obj&&typeof obj==="object")?obj:{label,text:String(obj||""),reason:""};
  const text=enforceSingleQuestionText(String(out.text||"").trim());
  const banned=["싸워줘서 고마워","화내줘서 고마워","상처 줘서 고마워","읽씹해줘서 고마워"];
  if(!text || banned.some(x=>text.includes(x))) return safeFallbackReply(situation,out.label||label||"추천");
  return {label:out.label||label||"추천",text,reason:String(out.reason||"").trim()};
}'''
assert old in s, 'sanitize anchor missing'
s=s.replace(old,new,1)

anchor='''  const msg=String(reqBody?.message||"");
  const situation=String(reqBody?.selectedSituation||"");
  const compact=msg.replace(/\\s+/g," ");
  const appointmentToday='''
insert='''  const msg=String(reqBody?.message||"");
  const situation=String(reqBody?.selectedSituation||"");
  const relation=String(reqBody?.relation||"");
  const compact=msg.replace(/\\s+/g," ");

  const intentionalDelay=/(?:똑같이|일부러|맞춰서)[^.\\n]{0,50}(?:시간|늦게|기다|텀)|(?:답장)[^.\\n]{0,40}(?:몇\\s*시간|\\d+\\s*시간)[^.\\n]{0,30}(?:기다|늦게)/.test(compact) && /답장|답/.test(compact);
  if(intentionalDelay){
    return {
      meaning:"상대가 늦게 답했다는 사실과 사용자가 지금 답장할 수 있다는 사실만 확인됩니다. 상대가 일부러 늦춘 것인지는 알 수 없습니다.",
      emotion:"답장 속도 한 번만으로 상대의 호감이나 힘겨루기를 판단하지 않습니다.",
      caution:"상대와 같은 시간만큼 일부러 기다리거나 답장 텀을 계산해 맞추지 마세요.",
      advice:"지금 답할 수 있다면 자연스럽게 답하세요. 답장 시각보다 대화 내용, 역질문, 자기 이야기, 약속 참여 같은 행동을 더 중요하게 보세요.",
      nextAction:"일부러 시간을 재지 말고 지금 가능한 시점에 자연스럽게 답하세요. 실제로 보낼 문장이 필요하면 상대가 보낸 메시지 내용을 기준으로 답장을 만드세요.",
      replies:[]
    };
  }

  const jealousyPhoneCheck=/휴대폰|핸드폰/.test(compact) && /(?:보여|확인|검사|비밀번호)/.test(compact) && /(?:질투|불안|동료|점심)/.test(compact);
  if(jealousyPhoneCheck){
    return {
      meaning:"애인이 회사 동료와 점심을 먹었다는 사실 때문에 사용자가 질투와 불안을 느끼고, 휴대폰 확인으로 안심하려는 상황입니다. 상대의 부정행위는 입력에서 확인되지 않습니다.",
      emotion:"사용자의 질투와 불안은 실제 감정이지만, 그 감정만으로 상대의 잘못을 사실처럼 확정할 근거는 없습니다.",
      caution:"휴대폰 열람, 비밀번호 요구, 대화 내용 전부 확인 같은 검사는 신뢰 문제를 해결하기보다 통제를 키울 수 있으므로 권하지 않습니다.",
      advice:"검사 대신 사용자가 느낀 불안을 자신의 감정으로 설명하고, 두 사람이 편안하게 느낄 경계를 대화로 맞추는 편이 좋습니다.",
      nextAction:"휴대폰을 보여달라고 요구하기 전에 아래 문장 중 하나로 자신의 불안을 차분히 말하세요. 상대의 설명을 들은 뒤에도 같은 불안이 반복되면 두 사람이 허용할 관계 경계를 구체적으로 합의하세요.",
      replies:[
        {label:"가장 자연스럽게",text:"동료랑 점심 먹었다는 얘기를 듣고 내가 좀 질투가 났어. 휴대폰을 확인하기보다 내가 왜 불편했는지 차분히 얘기해보고 싶어.",reason:"상대를 범인처럼 취급하지 않고 사용자의 감정을 사용자가 책임지는 표현입니다."},
        {label:"조금 더 부드럽게",text:"내가 조금 불안해진 건 맞아. 네 휴대폰을 확인하고 싶다기보다 우리 둘이 편하게 얘기해서 풀고 싶어.",reason:"검사 요구를 줄이고 대화로 전환합니다."},
        {label:"경계까지 함께 정하기",text:"내가 질투가 나서 예민해진 것 같아. 서로 어떤 부분까지 편하게 공유할지 같이 얘기해보면 좋겠어.",reason:"감정을 인정하면서도 일방적인 휴대폰 검사를 요구하지 않습니다."}
      ]
    };
  }

  const firstMeetNextDay=relation.includes("첫 만남") && /어제/.test(compact) && /(?:소개팅|만났|만나)/.test(compact) && /즐거웠어요/.test(compact) && /오늘/.test(compact);
  if(firstMeetNextDay){
    return {
      meaning:"첫 만남 뒤 상대가 '즐거웠어요'라고 인사했고 사용자도 답한 뒤, 다음 날 아직 새 연락이 없는 상태입니다. 이 한 번의 인사와 하루 흐름만으로 호감의 크기는 확정할 수 없습니다.",
      emotion:"상대의 인사는 긍정적일 수 있지만 예의 있는 마무리 인사일 가능성도 있어, 실제 참여는 이후 대화와 만남 제안에서 더 확인해야 합니다.",
      caution:"입력에 없는 날씨, 사용자가 느꼈다고 말하지 않은 '정말 좋았어요·생각났어요' 같은 감정, 이미 잡히지 않은 다음 만남을 사실처럼 넣지 마세요.",
      advice:"오늘 자연스럽게 가벼운 대화를 한 번 열어도 됩니다. 이후 상대가 질문하거나 대화를 이어가는지 보고 다음 만남 제안을 판단하세요.",
      nextAction:"아래 문장 중 하나로 오늘 한 번 가볍게 대화를 여세요. 상대가 대화를 함께 이어가면 다음 흐름에서 구체적인 두 번째 만남을 제안하고, 참여가 약하면 메시지 양을 늘리지 마세요.",
      replies:[
        {label:"가장 자연스럽게",text:"오늘은 어떻게 지내세요?",reason:"입력에 없는 사실이나 감정을 만들지 않고 현재 대화를 가볍게 엽니다."},
        {label:"조금 더 다정하게",text:"오늘 하루는 어떻게 보내고 계세요?",reason:"상대의 상태를 미리 단정하지 않는 한 가지 질문입니다."},
        {label:"조금 더 가볍게",text:"오늘은 뭐 하면서 보내고 계세요?",reason:"첫 만남에 대한 과한 의미 부여 없이 일상 대화를 다시 시작합니다."}
      ]
    };
  }

  const appointmentToday='''
assert anchor in s, 'deterministic quick anchor missing'
s=s.replace(anchor,insert,1)

old='''  if(isDetail && /\\[PRO\\s*고백\\s*타이밍\\]/.test(msg)){
    const facts=[];'''
new='''  if(isDetail && /\\[PRO\\s*고백\\s*타이밍\\]/.test(msg)){
    const earlyConfession=/(?:한\\s*번|1\\s*번)[^.\\n]{0,40}(?:만났|만남)/.test(compact) && /(?:제가|내가|사용자)[^.\\n]{0,60}먼저[^.\\n]{0,40}(?:연락|시작)/.test(compact) && /(?:상대[^.\\n]{0,50}먼저[^.\\n]{0,40}(?:약속|제안)[^.\\n]{0,30}(?:없|않)|먼저\\s*약속[^.\\n]{0,30}(?:없|않))/.test(compact);
    if(earlyConfession){
      out.replies=[];
      out.confidence="중간";
      out.dontSend="지금 바로 좋아한다고 고백하거나 관계를 확정해 달라는 메시지는 보내지 마세요.";
      out.advice="현재는 사용자의 연락 주도가 더 크고 상대의 자발적 약속 참여가 충분히 확인되지 않아 고백보다 상대 참여를 조금 더 보는 편이 안전합니다.";
      out.nextAction="당분간 고백 문장을 만들기보다 자연스러운 대화와 한두 번의 실제 만남에서 상대가 먼저 연락·질문·약속 제안에 참여하는지 확인하세요. 참여가 늘지 않으면 사용자의 연락과 제안을 더 늘리지 마세요.";
    }
    const facts=[];'''
assert old in s, 'PRO confession anchor missing'
s=s.replace(old,new,1)

assert '2026-08-23-potentia-v33-round2-quality-guards' in s
assert 'intentionalDelay' in s and 'jealousyPhoneCheck' in s and 'firstMeetNextDay' in s and 'enforceSingleQuestionText' in s
p.write_text(s,encoding='utf-8')
print('Potentia v33 round2 quality guards applied')
