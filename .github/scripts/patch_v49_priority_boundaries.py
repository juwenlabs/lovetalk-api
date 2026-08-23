from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')
old='2026-08-23-potentia-v48-pro-participation-balance'
new='2026-08-23-potentia-v49-priority-boundaries'
assert old in s, 'v48 base version missing'
s=s.replace(f'const SERVER_VERSION = "{old}";', f'const SERVER_VERSION = "{new}";', 1)

anchor='''  const compact=msg.replace(/\\s+/g," ");

  // v47: deterministic grounding for first-meetup neutrality, explicit friend-only'''
insert='''  const compact=msg.replace(/\\s+/g," ");

  // v49: higher-priority structure guards. These must run before generic
  // silence/model logic so repeated user investment and repeated boundaries
  // are not converted into another follow-up or an in-person solution.
  const threeUserOpenings=/(?:나는|내가|저는|사용자)[^.\\n]{0,80}먼저[^.\\n]{0,35}(?:세\\s*번|3\\s*번)[^.\\n]{0,30}(?:연락|메시지)/.test(compact) || /(?:세\\s*번|3\\s*번)[^.\\n]{0,60}(?:나는|내가|저는|사용자)[^.\\n]{0,40}먼저[^.\\n]{0,30}(?:연락|메시지)/.test(compact);
  const counterpartNeverOpened=/(?:상대가|상대는|상대)[^.\\n]{0,70}먼저\\s*연락[^.\\n]{0,35}(?:없|안)/.test(compact);
  const lastStillSilent=/(?:마지막|최근)[^.\\n]{0,80}(?:이틀|2\\s*일|48\\s*시간)[^.\\n]{0,50}(?:답[^.\\n]{0,15}(?:없|안)|무응답|읽씹)/.test(compact) || /(?:마지막|최근)[^.\\n]{0,80}(?:답[^.\\n]{0,15}(?:없|안)|무응답|읽씹)[^.\\n]{0,50}(?:이틀|2\\s*일|48\\s*시간)/.test(compact);
  if(threeUserOpenings && counterpartNeverOpened && lastStillSilent){
    return {
      meaning:"최근 대화 시작을 사용자가 세 번 맡았고 상대가 먼저 연락한 적은 없으며 마지막 연락에도 답이 없는 상태입니다. 단순 48시간 무응답보다 반복된 사용자 선연락 패턴을 먼저 봐야 합니다.",
      emotion:"상대의 속마음이나 무응답 이유는 알 수 없지만, 현재 확인되는 실제 참여는 사용자 쪽에 과도하게 치우쳐 있습니다.",
      caution:"여기서 3일 기준을 다시 세어 확인 메시지를 하나 더 만들거나, 새 화제로 네 번째 선연락을 하지 마세요.",
      advice:"이미 사용자가 세 번 연속 대화를 시작했다면 추가 연락을 중지하고 상대의 자발적 참여가 생기는지 확인하는 편이 맞습니다.",
      nextAction:"새 메시지를 보내지 마세요. 상대가 먼저 연락하거나 구체적인 질문·약속 제안 등 참여를 보일 때만 그 흐름에 답하세요. 상대 참여가 없으면 사용자의 연락 횟수를 더 늘리지 마세요.",
      replies:[]
    };
  }

  const vagueSomedayInvite=/(?:언제\\s*한\\s*번|언젠가)[^.\\n]{0,70}(?:밥|식사|커피|보자|만나)/.test(compact) && !/(?:월요일|화요일|수요일|목요일|금요일|토요일|일요일|이번\\s*주|다음\\s*주|오전|오후|저녁|\\d{1,2}\\s*시)/.test(compact);
  if(vagueSomedayInvite){
    return {
      meaning:"상대가 언젠가 함께 식사하거나 만나자는 가능성을 말했지만 구체적인 날짜·시간은 전혀 정해지지 않았습니다. 아직 확정된 약속은 아닙니다.",
      emotion:"이 한 문장만으로 연애 호감이나 실제 만남 의지의 크기를 단정할 수 없습니다. 말보다 이후에 상대가 일정을 구체화하는지가 더 중요합니다.",
      caution:"사용자가 가능하다고 말하지 않은 '이번 주·주말·평일 저녁'을 만들어 제안하거나, 'ㅎㅎ' 같은 한 신호로 호감을 확정하지 마세요.",
      advice:"지금은 상대의 제안을 가볍게 받아주고 구체적인 일정은 상대가 실제로 참여해 정하는지 보는 편이 안전합니다.",
      nextAction:"아래 문장 중 하나로 가능성만 받아주고 기다리세요. 상대가 구체적인 날짜나 시간을 제시하면 그때 사용자의 실제 가능 여부를 확인해 조율하세요.",
      replies:[
        {label:"가장 자연스럽게",text:"좋아요. 일정 정해지면 말씀해주세요.",reason:"사용자의 미확인 가능 시간을 만들지 않고 상대가 구체화하도록 둡니다."},
        {label:"조금 더 정중하게",text:"네, 구체적으로 정해지면 알려주세요.",reason:"확정되지 않은 제안을 약속처럼 바꾸지 않습니다."},
        {label:"가장 간결하게",text:"좋습니다. 정해지면 편하게 말씀해주세요.",reason:"특정 요일·시간이나 감정을 새로 만들지 않습니다."}
      ]
    };
  }

  const moneyPressure=/(?:\\d+\\s*만원|돈|금전)[^.\\n]{0,80}(?:빌려|빌려달|송금|보내달)/.test(compact) && /(?:사랑하면|좋아하면|도와줘야|이 정도는)/.test(compact);
  const userMoneyBoundary=/(?:나는|내가|저는|사용자)[^.\\n]{0,100}(?:돈[^.\\n]{0,25}(?:싫|안)|빌려주[^.\\n]{0,25}(?:싫|않|안)|송금[^.\\n]{0,20}(?:싫|안))/.test(compact);
  if(moneyPressure && userMoneyBoundary){
    return {
      meaning:"상대가 돈을 빌려달라고 요청하면서 사랑이나 관계를 이유로 압박하고 있고, 사용자는 돈을 빌려주고 싶지 않다고 명확히 밝혔습니다.",
      emotion:"상대가 실제로 얼마나 급한지나 요청의 진짜 의도는 단정하지 않습니다. 확인되는 것은 금전 요구와 감정적 압박, 사용자의 거절 의사입니다.",
      caution:"미안함을 사용자가 느낀 것처럼 만들거나, 상대가 급하다고 추정하거나, 압박을 줄이기 위해 일부라도 송금하지 마세요.",
      advice:"금전 거래를 하지 않겠다는 경계를 짧고 분명하게 전달하세요. 같은 요구와 압박이 반복되면 설명을 늘리지 말고 대화와 관계의 거리를 재검토하세요.",
      nextAction:"아래 문장 중 하나로 돈을 빌려주지 않겠다는 입장을 한 번 전달하세요. 이후에도 사랑을 이유로 압박하면 같은 논쟁을 반복하지 말고 연락을 줄이세요.",
      replies:[
        {label:"명확한 거절",text:"돈은 빌려주지 않을게. 이 문제로 압박하지 말아줘.",reason:"사용자의 실제 거절 의사만 전달합니다."},
        {label:"원칙 전달",text:"나는 금전 거래는 하지 않겠어. 돈을 보내지는 않을게.",reason:"미안함이나 상대 사정을 새로 만들지 않습니다."},
        {label:"대화 경계",text:"내 결정은 바뀌지 않아. 돈 얘기는 여기까지 할게.",reason:"추가 설득에 대한 행동 경계를 분명히 합니다."}
      ]
    };
  }

  const repeatedUnannouncedVisit=/(?:회사\\s*앞|직장\\s*앞|집\\s*앞)[^.\\n]{0,100}(?:예고\\s*없이|자꾸|계속|반복)/.test(compact) && /(?:오지\\s*말|오지마|찾아오지\\s*말)/.test(compact) && /(?:또\\s*왔|다시\\s*왔|계속\\s*와|반복)/.test(compact);
  if(repeatedUnannouncedVisit){
    return {
      meaning:"상대가 예고 없이 사용자의 회사나 생활 공간에 반복해서 찾아오고, 사용자가 오지 말라고 이미 말했는데도 그 경계가 지켜지지 않고 있습니다.",
      emotion:"상대가 왜 찾아오는지는 단정하지 않습니다. 현재 중요한 사실은 사용자의 명확한 방문 거절이 반복해서 무시되고 있다는 점입니다.",
      caution:"사용자가 느낀다고 말하지 않은 스트레스·두려움을 답장에 만들거나, 문제 해결을 위해 직접 만나거나 단둘이 대화하라고 권하지 마세요.",
      advice:"대면 만남보다 서면으로 방문 중단 경계를 분명히 남기고 거리를 우선하세요. 반복되면 관련 연락과 방문 기록을 보존하고 신뢰할 수 있는 동료·직장 지원 경로 등 안전한 도움을 고려하세요.",
      nextAction:"이미 방문 중단을 분명히 말했다면 새로 만나서 설명할 필요가 없습니다. 필요하면 아래 문장 중 하나를 한 번 서면으로 남기고, 이후에도 반복되면 답장을 늘리지 말고 기록·차단·주변 지원을 우선하세요.",
      replies:[
        {label:"명확한 방문 경계",text:"회사 앞에 오지 말아달라고 이미 말했어. 앞으로는 오지 말아줘.",reason:"사용자가 실제로 전달한 경계를 그대로 반복합니다."},
        {label:"반복 중단 요청",text:"예고 없이 회사로 찾아오는 건 원하지 않아. 다시 오지 말아줘.",reason:"대면 해결을 열어두지 않고 방문 자체를 중단시킵니다."},
        {label:"연락 경계",text:"이 요청을 계속 무시하면 연락을 중단할게.",reason:"반복 경계 침해에 대한 행동 결과를 분명히 합니다."}
      ]
    };
  }

  // v47: deterministic grounding for first-meetup neutrality, explicit friend-only'''
assert anchor in s, 'v49 quick priority anchor missing'
s=s.replace(anchor,insert,1)

p.write_text(s,encoding='utf-8')
print('patched',new)
