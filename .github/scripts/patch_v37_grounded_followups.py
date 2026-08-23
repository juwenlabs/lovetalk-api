from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')
assert '2026-08-23-potentia-v36-apology-detection' in s, 'expected v36 server not found'
s=s.replace('const SERVER_VERSION = "2026-08-23-potentia-v36-apology-detection";', 'const SERVER_VERSION = "2026-08-23-potentia-v37-grounded-followups";', 1)

anchor='''  const initialNumberExchange=/(?:번호\\s*교환|연락처\\s*교환)/.test(relation+" "+compact);'''
insert='''  const firstDateNextDay=/(?:첫\\s*소개팅\\s*다음날|첫\\s*만남\\s*다음날)/.test(relation) || (/어제[^.\\n]{0,50}(?:처음\\s*만났|소개팅)/.test(compact) && /(?:다음\\s*약속|다음\\s*만남)[^.\\n]{0,50}(?:없|정하지)/.test(compact));
  if(firstDateNextDay){
    out.replies=[
      {label:"자연스럽게",text:"어제 시간 내주셔서 감사했어요. 오늘은 잘 보내고 계세요?",reason:"사용자가 말하지 않은 호감이나 즐거움을 새로 만들지 않고 감사와 안부만 전합니다."},
      {label:"부담 최소화",text:"어제 시간 내주셔서 감사했어요. 오늘도 잘 보내세요.",reason:"다음 약속을 서두르지 않고 첫 만남 다음날 가볍게 인사합니다."},
      {label:"안부 중심",text:"어제는 잘 들어가셨어요?",reason:"입력에 있는 첫 만남과 귀가 인사 맥락만 사용합니다."}
    ];
    return out;
  }

  const initialNumberExchange=/(?:번호\\s*교환|연락처\\s*교환)/.test(relation+" "+compact);'''
assert anchor in s, 'starter grounding anchor missing'
s=s.replace(anchor,insert,1)

anchor2='''  const repeatedShortNoReciprocity='''
insert2='''  const initialMovieOneExchange=/(?:초기\\s*대화|처음\\s*대화)/.test(relation) && /(?:영화\\s*봤|영화\\s*보)/.test(compact) && /(?:한\\s*번\\s*주고받|아직\\s*한\\s*번|한번\\s*주고받)/.test(compact);
  if(initialMovieOneExchange){
    return {
      meaning:"상대가 집에서 영화를 봤다고 한 번 답했다는 사실만 확인됩니다. 이 한 번의 답장으로 호감이나 대화 의욕을 판단할 수는 없습니다.",
      emotion:"상대의 현재 감정이나 피곤함·휴식 상태는 입력에 없으므로 추정하지 않습니다.",
      caution:"'푹 쉬셨네요', '영화로 쉬셨네요'처럼 입력에 없는 상태를 덧붙이지 마세요. 한 번의 답장만으로 호감 수준을 판단하지도 마세요.",
      advice:"상대가 실제로 말한 영화 주제 안에서 질문 하나로 가볍게 이어가고 이후의 참여 패턴을 더 보세요.",
      nextAction:"아래 문장 중 하나를 보내고 상대가 구체적으로 답하거나 역질문하는지 확인하세요. 아직은 관계를 확대하거나 줄일 단계가 아닙니다.",
      replies:[
        {label:"가장 자연스럽게",text:"무슨 영화 보셨어요?",reason:"상대가 실제로 말한 영화 주제만 이어갑니다."},
        {label:"조금 더 편하게",text:"어떤 영화 보셨어요?",reason:"새로운 사실을 만들지 않고 대화 폭을 넓힙니다."},
        {label:"반응 확인",text:"재밌게 보셨어요?",reason:"상대가 이미 본 영화에 대한 경험만 묻습니다."}
      ]
    };
  }

  const repeatedShortNoReciprocity='''
assert anchor2 in s, 'analysis grounding anchor missing'
s=s.replace(anchor2,insert2,1)

assert '2026-08-23-potentia-v37-grounded-followups' in s
assert 'firstDateNextDay' in s and 'initialMovieOneExchange' in s
p.write_text(s,encoding='utf-8')
print('Potentia v37 grounded follow-up fixes applied')
