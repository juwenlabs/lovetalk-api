from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')
old='2026-08-23-potentia-v47-boundaries-followup-grounding'
new='2026-08-23-potentia-v48-pro-participation-balance'
assert old in s, 'v47 base version missing'
s=s.replace(f'const SERVER_VERSION = "{old}";', f'const SERVER_VERSION = "{new}";', 1)

anchor='''function getDeterministicDetailAnalysis(reqBody){
  if(String(reqBody?.mode||"")!=="detail") return null;
  const msg=String(reqBody?.message||"");
  const compact=msg.replace(/\\s+/g," ");
  const vagueNextWeekPlan='''
insert='''function getDeterministicDetailAnalysis(reqBody){
  if(String(reqBody?.mode||"")!=="detail") return null;
  const msg=String(reqBody?.message||"");
  const compact=msg.replace(/\\s+/g," ");

  // v48: mixed participation is not a cue for the user to keep opening chats.
  // Fast replies and occasional questions count as participation, but no
  // counterpart initiation + repeated user initiation remains asymmetric.
  const fastReplies=/(?:세\\s*번|3\\s*번)[^.\\n]{0,70}답장[^.\\n]{0,40}빠르/.test(compact) || /답장[^.\\n]{0,50}빠르[^.\\n]{0,50}(?:세\\s*번|3\\s*번)/.test(compact);
  const noCounterInitiation=/(?:상대가|상대는|상대)[^.\\n]{0,90}먼저\\s*연락[^.\\n]{0,40}(?:없|안)/.test(compact);
  const repeatedUserOpening=/(?:나는|내가|저는|사용자)[^.\\n]{0,90}(?:두\\s*번|2\\s*번|세\\s*번|3\\s*번)[^.\\n]{0,50}먼저\\s*연락/.test(compact);
  const noMeetingProposal=/(?:약속|만남)[^.\\n]{0,30}제안[^.\\n]{0,50}(?:서로\\s*)?(?:없|안)/.test(compact);
  if(fastReplies && noCounterInitiation && repeatedUserOpening && noMeetingProposal){
    return {
      meaning:"상대의 답장은 빠르고 가끔 질문도 있지만, 상대가 먼저 연락한 적은 없고 최근 대화 시작은 사용자가 반복해서 맡았으며 서로 약속 제안도 아직 없습니다. 참여는 일부 있으나 주도성은 비대칭입니다.",
      confidence:"중간",
      emotion:"빠른 답장과 간헐적인 질문은 대화 참여 신호일 수 있지만 연애 호감이나 적극성을 확정하는 근거는 아닙니다. 상대의 자발적 선연락이나 약속 참여는 아직 확인되지 않았습니다.",
      flow:"현재는 사용자가 대화를 열고 상대가 응답하는 흐름이 더 강합니다. 상대가 대화에 전혀 참여하지 않는 것은 아니지만, 관계를 앞으로 움직이는 행동은 아직 사용자 쪽에 더 치우쳐 있습니다.",
      strategy:"상대의 마음을 시험하려고 또 새 대화를 열지 말고, 사용자의 선연락을 잠시 늘리지 않은 상태에서 상대가 먼저 연락하거나 약속을 제안하는지 확인합니다.",
      caution:"'답장 빨리 해줘서 좋네요'처럼 사용자가 말하지 않은 감정을 만들어 보내거나, 빠른 답장만으로 썸을 확정하거나, 며칠 뒤 반드시 다시 연락하는 추적 일정을 만들지 마세요.",
      dontSend:"답장 빨리 해줘서 좋네요, 왜 먼저 연락은 안 해요처럼 감정·압박을 새로 만들거나 상대 반응을 시험하는 문장은 보내지 마세요.",
      replies:[],
      advice:"지금은 사용자가 새 대화를 한 번 더 여는 것보다 상대의 자발적 참여를 보는 편이 균형에 맞습니다. 상대가 먼저 연락하면 자연스럽게 답하되, 선연락이 계속 사용자에게만 몰리면 사용자의 투자량을 더 늘리지 마세요.",
      nextAction:"지금은 새 메시지를 보내지 마세요. 상대가 먼저 연락하거나 질문·약속 제안 등 구체적인 참여를 보이면 그 흐름에 답하고, 그런 참여가 없으면 사용자가 연락 횟수를 추가로 늘리지 마세요."
    };
  }

  const vagueNextWeekPlan='''
assert anchor in s, 'v48 detail insertion anchor missing'
s=s.replace(anchor,insert,1)

p.write_text(s,encoding='utf-8')
print('patched',new)
