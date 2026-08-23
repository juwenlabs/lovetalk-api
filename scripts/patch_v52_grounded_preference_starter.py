from pathlib import Path

p = Path('server.js')
s = p.read_text(encoding='utf-8')
old_ver = 'const SERVER_VERSION = "2026-08-23-potentia-v51-reciprocal-grounding";'
new_ver = 'const SERVER_VERSION = "2026-08-23-potentia-v52-grounded-preference-starter";'
assert old_ver in s, 'v51 base version missing'
s = s.replace(old_ver, new_ver, 1)

marker = '  const normalizedStarterGoal='
assert marker in s, 'starter insertion marker missing'
insert = r'''  // v52: when an advanced meeting starter has both a preference the
  // counterpart explicitly stated and a time the user explicitly said they
  // are available, use those two facts in the actual invitation. Do not
  // invent a venue, shared hobby, weather, or a fake "thought of you" hook.
  const starterGoalText=String(starterGoal||"")+" "+String(selectedSituation||"");
  if(advanced && /(?:만남|만나|약속)/.test(starterGoalText)){
    const prefMatch=context.match(/상대(?:가|는)?\s*([^.\n]{1,30}?)\s*(?:을|를)?\s*좋아한다고\s*(?:직접\s*)?말/);
    const availabilityMatch=context.match(/(?:나는|내가|저는|저도|사용자)[^.\n]{0,35}(이번\s*)?(월요일|화요일|수요일|목요일|금요일|토요일|일요일)(?:\s*(오전|오후|저녁))?[^.\n]{0,20}(?:가능|괜찮|시간\s*(?:돼|됨|된다))/);
    if(prefMatch && availabilityMatch){
      const preference=String(prefMatch[1]||"").trim().replace(/(?:을|를)$/,'').trim();
      const when=[availabilityMatch[1]?"이번":"",availabilityMatch[2],availabilityMatch[3]||""].filter(Boolean).join(" ");
      if(preference && when){
        return {
          guard:null,
          result:{replies:[
            {label:"자연스럽게",text:`${preference} 좋아한다고 하셨죠. ${when} 괜찮으시면 만나서 그 얘기 조금 더 나눌까요?`,reason:"상대가 직접 말한 취향과 사용자가 실제로 가능하다고 밝힌 일정만 사용합니다."},
            {label:"조금 더 가볍게",text:`${when} 시간 괜찮으세요? ${preference} 좋아한다고 하신 얘기도 만나서 이어가볼까요?`,reason:"없는 장소나 공통 취향을 만들지 않고 확인된 취향을 만남 제안의 맥락으로 씁니다."},
            {label:"간결하게",text:`${preference} 좋아한다고 하신 거 기억하고 있어요. ${when} 괜찮으시면 잠깐 만날까요?`,reason:"생각났다는 명분이나 날씨·장소를 새로 만들지 않고 두 확인 사실만 사용합니다."}
          ]},
          advanced:true
        };
      }
    }
  }

'''
s = s.replace(marker, insert + marker, 1)
p.write_text(s, encoding='utf-8')
