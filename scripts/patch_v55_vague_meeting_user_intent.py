from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')
old='const SERVER_VERSION = "2026-08-23-potentia-v54-unavailable-boundary-priority";'
new='const SERVER_VERSION = "2026-08-23-potentia-v55-vague-meeting-user-intent";'
assert old in s, 'v54 base version missing'
s=s.replace(old,new,1)

anchor='''function getDeterministicDetailAnalysis(reqBody){
  if(String(reqBody?.mode||"")!=="detail") return null;
  const msg=String(reqBody?.message||"");
  const compact=msg.replace(/\\s+/g," ");

'''
assert anchor in s, 'detail analysis anchor missing'
insert=r'''  // v55: a counterpart's vague "see you again sometime" is not permission
  // to invent the user's desire to meet again. In relationship-analysis mode,
  // if the user's own wish/feeling is not stated and no concrete schedule
  // exists, analyze the participation but do not manufacture sendable replies.
  const detailSituation=String(reqBody?.selectedSituation||"");
  const vagueFutureMeeting=/(?:다음에|나중에)[^.\n]{0,18}(?:또\s*)?(?:봐요|보자|봬요|뵈어요|만나요|만나자)/.test(compact);
  const concreteFutureSchedule=/(?:월요일|화요일|수요일|목요일|금요일|토요일|일요일|이번\s*주|다음\s*주|\d{1,2}\s*시|오전|오후|저녁)[^.\n]{0,45}(?:보|만나|약속)/.test(compact);
  const explicitUserMeetingDesire=/(?:나는|내가|저는|저도|사용자)[^.\n]{0,100}(?:다시|또|한번|한\s*번)?[^.\n]{0,30}(?:보고\s*싶|만나고\s*싶|뵙고\s*싶|즐거웠|좋았|재밌었|기대)/.test(compact);
  const relationAnalysisIntent=/(?:썸|관계|상세|헷갈)/.test(detailSituation+" "+compact);
  if(vagueFutureMeeting && !concreteFutureSchedule && !explicitUserMeetingDesire && relationAnalysisIntent){
    const counterpartInitiated=/상대(?:가|는)?[^.\n]{0,100}먼저[^.\n]{0,35}연락/.test(compact);
    const mutualQuestions=/(?:서로[^.\n]{0,60}질문|질문[^.\n]{0,60}(?:주고받|서로))/.test(compact);
    const participation=[counterpartInitiated?"상대의 선연락":"",mutualQuestions?"서로의 질문 교환":""].filter(Boolean);
    const observed=participation.length?participation.join("과 "):"대화가 이어진 흐름";
    return {
      meaning:`${observed}은 확인됩니다. 상대가 '다음에 또 보자'는 취지의 말을 했지만 날짜·시간이 정해지지 않아 확정 약속으로 볼 수는 없습니다.`,
      confidence:"중간",
      emotion:"상대의 표현은 긍정적인 가능성을 보여줄 수 있지만 예의 있는 마무리 표현일 수도 있어 호감의 강도는 단정할 수 없습니다. 사용자가 다시 만나고 싶은지에 대해서도 입력에 근거가 없습니다.",
      flow:"대화 참여는 이어졌지만 만남은 아직 구체적인 일정 조율 단계로 넘어가지 않았습니다.",
      strategy:"상대의 실제 참여가 계속되는지 보고, 구체적인 날짜나 시간이 제시될 때 사용자의 실제 가능 여부를 확인합니다. 사용자의 마음이나 일정을 대신 만들어 답장을 생성하지 않습니다.",
      caution:"사용자가 말하지 않았는데 '저도 좋아요', '또 뵈면 좋겠어요', '저도 다시 만나고 싶어요'처럼 재만남 의향을 새로 만들지 마세요. 임의의 날짜·장소도 넣지 마세요.",
      dontSend:"사용자의 재만남 의향이 확인되지 않은 상태에서 '저도 또 뵈면 좋겠어요'처럼 마음을 대신 표현하는 문장은 보내지 마세요.",
      replies:[],
      advice:"지금 요청은 관계 분석이므로 별도의 답장 문장을 만들 필요가 없습니다. 상대의 선연락·질문·구체적 일정 제안 같은 실제 참여를 더 확인하세요.",
      nextAction:"새 메시지를 분석 결과 때문에 만들지 마세요. 이후 실제 대화가 이어지거나 상대가 날짜·시간을 구체화하면 그때 사용자의 실제 의향과 가능 일정을 기준으로 대응하세요."
    };
  }

'''
s=s.replace(anchor,anchor+insert,1)
p.write_text(s,encoding='utf-8')
