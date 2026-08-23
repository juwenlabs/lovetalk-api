from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')
old='const SERVER_VERSION = "2026-08-24-potentia-v69-fast-compact-core";'
new='const SERVER_VERSION = "2026-08-24-potentia-v70-grounded-starter";'
if old not in s: raise SystemExit('v69 marker missing')
s=s.replace(old,new,1)
anchor='''  const normalizedStarterGoal=/밀당|일부러.{0,10}(늦|기다)|답장 텀/.test(String(starterGoal||"")+" "+context) ? "조작 없이 자연스럽게 연락하기" : starterGoal;'''
if anchor not in s: raise SystemExit('normalizedStarterGoal anchor missing')
block=r'''  // v70: if the counterpart explicitly stated a preference and the goal is
  // simply to open/continue conversation, do not ask the model to invent a
  // previous day, a fake "thought of you" hook, or a user preference.
  const simpleStarterGoal=!/(?:만남|만나|약속|데이트)/.test(String(starterGoal||"")+" "+String(selectedSituation||""));
  const statedPreference=context.match(/상대(?:가|는)?\s*([^.\n]{1,40}?)\s*(?:을|를)?\s*좋아한다고\s*(?:직접\s*)?말/);
  if(simpleStarterGoal && statedPreference){
    const preference=String(statedPreference[1]||"").trim().replace(/(?:을|를)$/,'').trim();
    if(preference){
      const isMovie=/영화/.test(preference);
      const replies=isMovie?[
        {label:"자연스럽게",text:`${preference} 좋아한다고 하셨죠. 최근에 재미있게 본 작품 있으세요?`,reason:"상대가 직접 말한 취향만 사용해 자연스럽게 대화를 엽니다."},
        {label:advanced?"조금 더 관심 있게":"다정하게",text:`요즘 볼 만한 ${preference} 있으면 하나 추천해주세요.`,reason:"없는 과거 대화나 사용자의 취향을 만들지 않고 상대가 말한 주제를 이어갑니다."},
        {label:advanced?"부담 최소화":"가볍게",text:`${preference} 중에서는 어떤 스타일을 제일 좋아하세요?`,reason:"한 번의 질문으로 상대가 자신의 취향을 더 이야기할 여지를 줍니다."}
      ]:[
        {label:"자연스럽게",text:`${preference} 좋아한다고 하셨죠. 요즘은 어떤 게 제일 좋아요?`,reason:"상대가 직접 말한 취향만 사용합니다."},
        {label:advanced?"조금 더 관심 있게":"다정하게",text:`${preference} 얘기해주신 게 기억나요. 요즘도 자주 즐기세요?`,reason:"확인된 취향을 자연스럽게 다시 이어갑니다."},
        {label:advanced?"부담 최소화":"가볍게",text:`${preference} 관련해서 추천해주실 만한 거 있으세요?`,reason:"사용자의 가짜 공통점을 만들지 않고 상대에게 이야기할 여지를 줍니다."}
      ];
      return {guard:null,result:{replies},advanced:!!advanced};
    }
  }

'''
s=s.replace(anchor,block+anchor,1)
p.write_text(s,encoding='utf-8')
