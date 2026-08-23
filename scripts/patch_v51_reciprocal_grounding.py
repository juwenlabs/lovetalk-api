from pathlib import Path

p = Path('server.js')
s = p.read_text(encoding='utf-8')
old_ver = 'const SERVER_VERSION = "2026-08-23-potentia-v50-detail-completion-resilience";'
new_ver = 'const SERVER_VERSION = "2026-08-23-potentia-v51-reciprocal-grounding";'
assert old_ver in s, 'v50 base version missing'
s = s.replace(old_ver, new_ver, 1)

marker = '  const vagueNextWeekPlan='
assert marker in s, 'detail-analysis insertion marker missing'
insert = r'''  // v51: reciprocal participation is meaningful participation, but it does not
  // create a user schedule, venue, or meeting proposal out of thin air. When
  // both sides initiate and ask questions but nobody has proposed a meeting,
  // keep the assessment balanced and do not manufacture a new outgoing chat.
  const reciprocalInitiation=
    /상대(?:가|는)?[^.\n]{0,80}먼저\s*연락/.test(compact) &&
    /(?:나는|내가|나도|저는|저도|사용자)[^.\n]{0,80}먼저\s*연락/.test(compact);
  const mutualQuestions=/(?:서로[^.\n]{0,60}질문|질문[^.\n]{0,60}(?:주고받|서로))/.test(compact);
  const explicitNoMeetingProposal=
    /(?:아직|둘\s*다|서로)[^.\n]{0,80}(?:약속|만남)[^.\n]{0,45}(?:제안한\s*적(?:은)?\s*없|제안[^.\n]{0,15}(?:없|안))/.test(compact) ||
    /(?:약속|만남)\s*(?:을|은|이)?[^.\n]{0,30}제안한\s*적(?:은)?\s*없/.test(compact);
  if(reciprocalInitiation && mutualQuestions && explicitNoMeetingProposal){
    return {
      meaning:"서로 먼저 연락한 적이 있고 질문도 주고받아 대화 참여는 한쪽으로 치우치지 않은 편입니다. 다만 아직 누구도 만남이나 약속을 제안하지 않았으므로 관계가 다음 단계로 넘어갔다고 보기는 어렵습니다.",
      confidence:"중간",
      emotion:"양방향 참여는 긍정적인 행동 신호이지만, 이것만으로 서로의 호감 강도나 썸 여부를 확정할 수는 없습니다.",
      flow:"현재 확인되는 것은 서로 연락을 시작하고 질문을 주고받는 대화 참여입니다. 실제 만남 제안이나 일정 조율은 아직 시작되지 않았습니다.",
      strategy:"균형 잡힌 대화 흐름은 유지하되, 분석만을 이유로 새 약속을 만들어 보내지 않습니다. 실제 대화 맥락과 사용자의 가능한 일정이 확인된 뒤에만 만남 제안을 검토합니다.",
      caution:"사용자가 말하지 않은 주말·요일·시간·장소를 정하거나 '커피 한잔', '밥 한번'처럼 맥락 없는 약속을 새로 만들지 마세요. 양방향 연락만으로 호감을 확정하지도 마세요.",
      dontSend:"이번 주말에 커피 한잔 할래요처럼 입력에 없는 일정과 장소를 임의로 만든 문장은 보내지 마세요.",
      replies:[],
      advice:"현재는 별도 메시지를 새로 만들 필요가 없습니다. 실제 대화가 이어질 때 자연스럽게 답하고, 상대의 자발적 참여가 계속되는지 보세요.",
      nextAction:"다음 실제 대화 흐름을 이어가세요. 만남을 제안하고 싶다면 먼저 사용자의 실제 가능 일정과 대화 속 확인된 활동 맥락을 확인한 뒤 한 번만 구체화하세요. 그 정보가 없으면 임의의 날짜나 장소를 만들지 마세요."
    };
  }

'''
s = s.replace(marker, insert + marker, 1)
p.write_text(s, encoding='utf-8')
