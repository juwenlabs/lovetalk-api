from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')
old='const SERVER_VERSION = "2026-08-23-potentia-v65-instant-common-pro";'
new='const SERVER_VERSION = "2026-08-23-potentia-v66-grounded-fast-pro";'
if old not in s: raise SystemExit('v65 marker missing')
s=s.replace(old,new,1)

# Add an instant, fully grounded board-game invitation when both facts are explicit.
anchor='''  if(task==="date"){
    const mentionsMovie=/영화/.test(text);'''
replacement='''  if(task==="date"){
    const boardGame=/상대(?:가|는)?[^.\\n]{0,50}보드게임(?:을|를)?[^.\\n]{0,25}좋아한다고[^.\\n]{0,25}(?:직접\\s*)?말/.test(text);
    const whenMatch=text.match(/(?:나는|내가|저는|저도|나도|사용자)[^.\\n]{0,80}((?:이번|다음)?\\s*(?:월요일|화요일|수요일|목요일|금요일|토요일|일요일)(?:\\s*(?:오전|오후|저녁))?)[^.\\n]{0,40}(?:가능|괜찮|시간\\s*돼|시간\\s*되)/);
    if(boardGame && whenMatch){
      const when=whenMatch[1].replace(/\\s+/g," ").trim();
      return {
        meaning:`상대가 보드게임을 좋아한다고 직접 말했고 사용자는 ${when}이 가능하다고 밝혔습니다. 이 두 사실만으로 가볍게 만남을 제안할 근거는 충분합니다.`,
        confidence:"중간",
        emotion:"상대의 보드게임 선호는 확인된 취향이지만, 사용자를 만나고 싶다는 감정이나 의사까지 확인된 것은 아닙니다.",
        flow:`확인된 사실은 상대의 보드게임 선호와 사용자의 ${when} 가능 일정입니다. 상대의 실제 가능 여부는 아직 확인되지 않았습니다.`,
        strategy:`${when}에 보드게임을 같이 할지 한 번 가볍게 물어보고 상대가 일정을 확인할 여유를 남기세요.`,
        caution:"입력에 없는 보드게임 카페·매장·구체적 시간·인원을 임의로 정하지 마세요.",
        dontSend:"장소나 세부 시간을 이미 정해진 것처럼 넣거나 상대도 당연히 가능할 것처럼 말하지 마세요.",
        advice:"확인된 취향과 실제 가능한 일정만 사용하면 충분합니다.",
        nextAction:`${when} 가능 여부를 한 번 물어보고 상대의 답을 기다리세요.`,
        replies:[
          {label:"가장 자연스러운 답장",text:`보드게임 좋아한다고 하셨죠. ${when} 괜찮으시면 같이 해볼까요?`,reason:"상대가 직접 말한 취향과 사용자의 실제 가능 일정만 사용합니다."},
          {label:"조금 더 가볍게",text:`${when} 시간 괜찮으시면 보드게임 같이 해요.`,reason:"장소나 세부 시간을 새로 만들지 않습니다."},
          {label:"조금 더 여유 있게",text:`${when} 괜찮으세요? 가능하시면 보드게임 같이 해볼까요?`,reason:"상대가 일정을 확인하고 선택할 여유를 남깁니다."}
        ]
      };
    }
    const mentionsMovie=/영화/.test(text);'''
if anchor not in s: raise SystemExit('date anchor missing')
s=s.replace(anchor,replacement,1)

# Simple memory input with explicit preference + repeated questions can be grounded instantly.
anchor2='''  if(task==="risk"){
    const passwordPressure='''
insert2='''  if(task==="memory"){
    const coffeeFact=/상대(?:가|는)?[^.\\n]{0,40}커피(?:를|을)?[^.\\n]{0,25}좋아한다고[^.\\n]{0,25}말/.test(text);
    const repeatedQuestions=/(?:최근[^.\\n]{0,30}(?:두\\s*대화|2\\s*번|두\\s*번)[^.\\n]{0,50}질문|질문[^.\\n]{0,50}(?:두\\s*대화|2\\s*번|두\\s*번))/.test(text);
    if(coffeeFact && repeatedQuestions){
      return {
        meaning:"확인된 사실은 상대가 커피를 좋아한다고 직접 말했다는 점과 최근 두 대화에서 상대가 질문을 했다는 점입니다.",
        confidence:"높음",
        emotion:"질문이 반복됐다는 행동은 확인되지만, 그 행동만으로 상대의 호감·감정·성격을 추정하지 않습니다.",
        flow:"최근 두 대화에서 질문이 있었다는 반복 행동은 기억해둘 수 있습니다. 질문 내용이나 전체 대화 빈도가 없으므로 관심 강도나 관계 진전으로 확대하지 않습니다.",
        strategy:"장기 기억에는 직접 확인된 취향과 반복 관찰된 행동만 남기고 감정 추론은 분리하세요.",
        caution:"커피 선호를 실력·공통 취향·만남 의사로 바꾸거나 질문 두 번을 호감 신호로 저장하지 마세요.",
        dontSend:"이 기능은 기억 정리용이므로 별도의 메시지를 만들 필요가 없습니다.",
        advice:"커피 선호와 최근 두 대화의 질문 행동만 확인 사실/반복 패턴으로 저장하세요.",
        nextAction:"확인된 사실과 반복 행동만 장기 기억에 남기고 호감·감정 가설은 저장하지 마세요.",
        replies:[]
      };
    }
  }

  if(task==="risk"){
    const passwordPressure='''
if anchor2 not in s: raise SystemExit('risk anchor missing')
s=s.replace(anchor2,insert2,1)

# For all memory outputs, neutralize any model attempt to turn question behavior into romantic interest.
anchor3='''  if(task==="risk" && !asksForReply) out.replies=[];

  if(!out.meaning||!out.emotion||!out.strategy||!out.caution){'''
replacement3='''  if(task==="risk" && !asksForReply) out.replies=[];
  if(task==="memory"){
    out.replies=[];
    const memoryGuess=/(?:관심(?:의)?\\s*신호|호감|속마음|대화\\s*지속\\s*의지)/;
    if(memoryGuess.test(String(out.meaning||""))){
      out.meaning=String(out.meaning||"").replace(/이는\\s*관심(?:의)?\\s*신호일\\s*수\\s*있지만[^.。]*[.。]?/g,"이 행동만으로 감정이나 호감을 판단하지 않습니다. ").trim();
    }
    if(memoryGuess.test(String(out.emotion||""))){
      out.emotion="반복해서 질문했다는 행동은 확인할 수 있지만, 질문 내용과 전체 대화 흐름이 없으면 감정이나 호감은 판단하지 않습니다.";
      out.flow=out.emotion;
    }
  }

  if(!out.meaning||!out.emotion||!out.strategy||!out.caution){'''
if anchor3 not in s: raise SystemExit('memory postprocess anchor missing')
s=s.replace(anchor3,replacement3,1)

p.write_text(s,encoding='utf-8')
