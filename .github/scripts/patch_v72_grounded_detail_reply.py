from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')
old='const SERVER_VERSION = "2026-08-24-potentia-v71-instant-reply-core";'
new='const SERVER_VERSION = "2026-08-24-potentia-v72-grounded-detail-reply";'
if old not in s: raise SystemExit('v71 marker missing')
s=s.replace(old,new,1)

anchor='''  if(mode==="detail"){
    const mutualSummary='''
if anchor not in s: raise SystemExit('detail instant anchor missing')
block=r'''  if(mode==="detail"){
    const busyHomeQuestion=/(?:오늘[^.\n]{0,30})?(?:일이\s*)?좀?\s*바빴/.test(text) && /(?:이제|지금)[^.\n]{0,20}집에\s*(?:왔|도착)/.test(text) && /오늘(?:은)?\s*(?:뭐|무엇)[^.\n]{0,20}(?:했|하셨)/.test(text);
    if(busyHomeQuestion){
      return {
        meaning:"상대가 오늘 바빴고 지금 집에 왔다고 자신의 상황을 공유한 뒤 사용자의 하루를 물었습니다.",
        confidence:"높음",
        emotion:"상대가 질문으로 대화에 참여한 행동은 확인되지만, 이 한 메시지만으로 호감이나 숨은 의도를 판단할 수는 없습니다.",
        flow:"상대가 자기 상황을 말하고 사용자에게 질문을 돌려 대화를 이어가는 흐름입니다.",
        strategy:"사용자의 하루 정보가 입력되지 않았으므로 그 부분을 지어내지 말고, 상대가 말한 바쁜 하루에 먼저 반응하면서 질문 하나로 이어가세요.",
        caution:"사용자가 실제로 하지 않은 일이나 감정을 '저도 바빴어요', '저도 집에 왔어요'처럼 만들어 답하지 마세요.",
        dontSend:"사용자의 하루를 AI가 임의로 만들어 상대의 질문에 답하는 문장은 보내지 마세요.",
        advice:"사용자의 실제 하루를 넣을 수 없다면 상대가 말한 상황에 짧게 반응하는 문장이 가장 안전합니다.",
        nextAction:"아래 문장 중 하나로 상대의 이야기에 반응하고, 사용자 자신의 하루를 말하고 싶다면 실제 있었던 내용만 직접 덧붙이세요.",
        replies:[
          {label:"가장 자연스러운 답장",text:"오늘 많이 바쁘셨군요. 어떤 일 때문에 바쁘셨어요?",reason:"상대가 직접 말한 바쁜 하루만 사용하고 사용자의 하루는 만들지 않습니다."},
          {label:"다른 느낌의 답장",text:"이제 집에 오셨군요. 오늘 하루는 어떠셨어요?",reason:"확인된 귀가 상황에서 질문 하나로 자연스럽게 이어갑니다."}
        ]
      };
    }
    const mutualSummary='''
s=s.replace(anchor,block,1)

# Extra final guard for the compact model path: when the input contains no
# explicit user-side first-person fact, discard model replies that invent one.
anchor2='''  out=applyAnalysisPolicyGuards(out,reqBody||{},isDetail);
  if(Array.isArray(out.replies)) out.replies=out.replies.slice(0,2);
  return out;
}'''
if anchor2 not in s: raise SystemExit('compact return anchor missing')
replacement2=r'''  out=applyAnalysisPolicyGuards(out,reqBody||{},isDetail);
  if(Array.isArray(out.replies)){
    const inputHasUserFact=/(?:나는|내가|저는|저도|나도|사용자)[^.\n]{0,100}(?:했|갔|왔|봤|먹|마셨|좋아|싫어|가능|어려|바빴|쉬었|일했|운동|공부)/.test(message);
    if(!inputHasUserFact){
      const inventedSelf=/(?:^|[.!?]\s*)(?:저는|저도|나는|나도|내가)\s*[^?]{2,80}(?:했|왔|갔|봤|먹|마셨|바빴|쉬었|좋아|싫어)/;
      out.replies=out.replies.filter(x=>!inventedSelf.test(String(x?.text||"")));
    }
    out.replies=out.replies.slice(0,2);
  }
  return out;
}'''
s=s.replace(anchor2,replacement2,1)

p.write_text(s,encoding='utf-8')
