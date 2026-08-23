from pathlib import Path
import re

p=Path('server.js')
s=p.read_text(encoding='utf-8')
old='2026-08-23-potentia-v44-deterministic-edges'
new='2026-08-23-potentia-v45-detail-role-binding'
assert old in s, 'v44 base version missing'
s=s.replace(f'const SERVER_VERSION = "{old}";', f'const SERVER_VERSION = "{new}";', 1)

pattern=r'''function getDeterministicDetailAnalysis\(reqBody\)\{.*?\n\}\n\nasync function generateAnalysisResult\(reqBody\)\{'''
replacement=r'''function getRoleBoundUserDayStatus(compact,dayName=""){
  const src=String(compact||"");
  const day=String(dayName||"").trim();
  if(!day) return {available:false,unavailable:false,part:""};
  const markerRe=/(나는|내가|저는|저도|나도|사용자|내\s*일정(?:은|상)?|제\s*일정(?:은|상)?|상대(?:가|는|도|방)?)/g;
  const markers=[]; let m;
  while((m=markerRe.exec(src))){
    markers.push({index:m.index,end:m.index+m[0].length,role:m[0].startsWith("상대")?"counterpart":"user"});
  }
  const weekdayRe=/(월요일|화요일|수요일|목요일|금요일|토요일|일요일)/;
  let available=false,unavailable=false,part="";
  for(let i=0;i<markers.length;i++){
    const mark=markers[i]; if(mark.role!=="user") continue;
    let end=Math.min(src.length,mark.end+180);
    if(markers[i+1]) end=Math.min(end,markers[i+1].index);
    const dot=src.indexOf(".",mark.end); if(dot>=0) end=Math.min(end,dot);
    const nl=src.indexOf("\n",mark.end); if(nl>=0) end=Math.min(end,nl);
    const seg=src.slice(mark.end,end);
    let from=0;
    while(true){
      const idx=seg.indexOf(day,from); if(idx<0) break;
      const after=seg.slice(idx+day.length);
      const nextDay=after.match(weekdayRe);
      const same=nextDay?after.slice(0,nextDay.index):after;
      if(/(?:안\s*되|안\s*돼|안됨|불가능|어렵|힘들|못\s*(?:가|해|돼)|시간\s*안)/.test(same)) unavailable=true;
      else if(/(?:가능|괜찮|돼|된다|시간\s*됨|시간\s*돼)/.test(same)){
        available=true;
        const pm=same.match(/(?:오전|오후|저녁)/); if(pm) part=pm[0];
      }
      from=idx+day.length;
    }
  }
  return {available,unavailable,part};
}
function getRoleBoundUserAlternative(compact,excludeDay=""){
  const days=["월요일","화요일","수요일","목요일","금요일","토요일","일요일"];
  for(const day of days){
    if(day===excludeDay) continue;
    const st=getRoleBoundUserDayStatus(compact,day);
    if(st.available && !st.unavailable) return {day,part:st.part,when:[day,st.part].filter(Boolean).join(" ")};
  }
  return null;
}
function getDeterministicDetailAnalysis(reqBody){
  if(String(reqBody?.mode||"")!=="detail") return null;
  const msg=String(reqBody?.message||"");
  const compact=msg.replace(/\s+/g," ");
  const counterpart=compact.match(/(?:상대(?:가|는)?[^.\n]{0,120})?(다음\s*주|다음주)\s*(월요일|화요일|수요일|목요일|금요일|토요일|일요일)(?:\s*(오전|오후|저녁))?[^.\n]{0,35}(?:가능|된|괜찮)/);
  if(!counterpart) return null;
  const day=counterpart[2];
  const counterWhen=[counterpart[1].replace(/\s+/g," "),day,counterpart[3]||""].filter(Boolean).join(" ");
  const userStatus=getRoleBoundUserDayStatus(compact,day);
  const alt=getRoleBoundUserAlternative(compact,day);

  if(userStatus.unavailable && alt){
    const altWhen=alt.when;
    return {
      meaning:`상대는 ${counterWhen}을(를) 제안했지만 사용자는 ${day}은 어렵고 ${altWhen}은 가능하다고 명시했습니다. 지금은 감정 분석보다 실제 일정 조율이 우선입니다.`,
      confidence:"높음",
      emotion:"상대가 대안 날짜를 말한 것은 일정 조율 참여 행동이지만 호감의 크기를 확정하는 근거는 아닙니다.",
      flow:`상대의 ${counterWhen} 제안과 사용자의 ${day} 불가·${altWhen} 가능 정보가 확인됩니다.`,
      strategy:`사용자가 불가능한 ${day}은 짧게 거절하고 실제 가능한 ${altWhen}을(를) 한 번 대안으로 제시합니다.`,
      caution:`${day}이 안 되는 이유를 입력에 없는 업무·약속·개인 사정으로 만들어 설명하지 마세요.`,
      dontSend:`${day} 좋아요, 그때 봐요처럼 불가능한 날짜를 수락하거나 '일이 있어서'처럼 입력에 없는 이유를 붙인 문장은 보내지 마세요.`,
      replies:[
        {label:"가장 자연스러운 답장",text:`${day}은 어려운데 ${altWhen}은 괜찮아요. ${altWhen}은 어떠세요?`,reason:"입력된 일정 사실만 사용합니다."},
        {label:"조금 더 정중한 답장",text:`말씀하신 ${day}은 어렵고 저는 ${altWhen}이 가능합니다. 괜찮으실까요?`,reason:"없는 이유를 만들지 않고 실제 대안만 제시합니다."},
        {label:"조금 더 여유 있는 답장",text:`${day}은 어렵습니다. ${altWhen}은 가능해요.`,reason:"가장 간결하게 일정 사실만 전달합니다."}
      ],
      advice:`${day}이 어렵다는 사실과 ${altWhen}이 가능하다는 사실만 전달하면 충분합니다.`,
      nextAction:`${altWhen}을(를) 한 번 제안하고 상대의 가능 여부를 기다리세요. 상대도 어렵다면 실제 가능한 다른 시간만 조율하세요.`
    };
  }

  if(!userStatus.available){
    return {
      meaning:`상대가 ${counterWhen}을(를) 구체적인 대안으로 제시했지만 사용자가 그 시간에 가능한지는 아직 확인되지 않았습니다.`,
      confidence:"높음",
      emotion:"구체적인 대안 날짜 제시는 일정 조율에 참여하는 행동이지만, 이것만으로 호감의 크기를 확정할 수는 없습니다.",
      flow:`상대의 ${counterWhen} 제안은 확인되지만 사용자의 가능 여부는 입력에 없습니다. 아직 약속 확정 단계가 아닙니다.`,
      strategy:"먼저 사용자의 실제 일정을 확인하고, 확인 전에는 상대 제안을 수락한 것처럼 말하지 않습니다.",
      caution:"사용자가 가능하다고 확인하지 않았는데 '괜찮을 것 같아요', '좋아요', '그날 봐요'처럼 가능 여부나 약속 수락을 암시하지 마세요.",
      dontSend:`${counterWhen} 좋아요, 그때 봐요처럼 미확인 일정을 확정하거나 가능할 것 같다고 추정하는 문장은 보내지 마세요.`,
      replies:[
        {label:"가장 자연스러운 답장",text:`${counterWhen} 말씀하신 거 확인했어요. 제 일정 확인하고 다시 말씀드릴게요.`,reason:"상대 제안만 확인하고 사용자 가능 여부는 만들지 않습니다."},
        {label:"조금 더 간결한 답장",text:`${counterWhen} 가능 여부 확인해보고 말씀드릴게요.`,reason:"일정 확인 전에는 수락하지 않습니다."},
        {label:"조금 더 정중한 답장",text:`${counterWhen} 제안해주셔서 감사합니다. 일정 확인 후 가능 여부 말씀드릴게요.`,reason:"입력에 없는 기대감이나 수락을 새로 만들지 않습니다."}
      ],
      advice:"지금은 상대의 제안을 확정하는 답장보다 사용자의 실제 일정 확인이 우선입니다.",
      nextAction:`먼저 ${counterWhen}에 실제로 가능한지 확인하세요. 가능하면 그때 약속을 확정하고, 불가능하면 사용자가 실제로 가능한 날짜만 대안으로 제시하세요.`
    };
  }

  return null;
}

async function generateAnalysisResult(reqBody){'''

s2,n=re.subn(pattern,lambda m: replacement,s,count=1,flags=re.S)
assert n==1, f'detail analysis replacement failed: {n}'
s=s2
assert new in s
assert 'getRoleBoundUserDayStatus' in s
p.write_text(s,encoding='utf-8')
print('v45 detail role-binding patch applied')
