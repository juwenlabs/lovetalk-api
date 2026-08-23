from pathlib import Path

p = Path("server.js")
s = p.read_text(encoding="utf-8")
old = 'const SERVER_VERSION = "2026-08-23-potentia-v58-fast-pro-analysis";'
new = 'const SERVER_VERSION = "2026-08-23-potentia-v59-fast-pro-grounding";'
if old not in s:
    raise SystemExit("v58 marker missing")
s = s.replace(old, new, 1)
marker = "  // v57: when a detailed analysis concludes that the user should not send a\n"
if marker not in s:
    raise SystemExit("v57 insertion marker missing")
block = r'''  // v59: keep fast PRO analysis grounded. Analytical PRO tools should not
  // emit meta-instructions/placeholders as sendable reply cards, and the model
  // must not invent observation periods, user availability, or romantic intent.
  if(isDetail && reqBody?.advanced){
    const isProConfession=/\[PRO\s*고백\s*타이밍\]/.test(msg);
    const isProDate=/\[PRO\s*데이트\s*타이밍\]/.test(msg);
    const isProRisk=/\[PRO\s*위험\s*신호\s*감지\]/.test(msg);
    const isProMonthly=/\[PRO\s*월간\s*관계\s*리포트\]/.test(msg);
    const isProMemory=/\[PRO\s*상대별\s*AI\s*기억\s*강화\]/i.test(msg);
    const inputHasExplicitTiming=/(?:\d+\s*(?:일|주|주일|시간|분)|하루|이틀|사흘|며칠|일주일|한\s*달|이번\s*주|다음\s*주)[^.\n]{0,50}(?:기다|연락|관찰|확인|보내|만나|가능)/.test(compact);
    const placeholderReply=/(?:\[[^\]]{1,120}\]|\((?:상대|구체적|답변|메시지|상황)[^)]{0,120}\)|상대\s*메시지\s*필요|구체적\s*답장\s*필요|상황에\s*따라\s*다릅니다)/;
    if(Array.isArray(out.replies)) out.replies=out.replies.filter(r=>{
      const text=String(r?.text||"").trim();
      return text && !placeholderReply.test(text);
    });

    if(!inputHasExplicitTiming && /(?:\d+\s*~\s*\d+\s*(?:일|주)|\d+\s*(?:일|주)\s*(?:뒤|동안)|며칠\s*(?:뒤|동안)|한두\s*번의\s*사이클)/.test(String(out.nextAction||""))){
      out.nextAction="상대의 실제 참여 행동을 다음 대화 흐름에서 확인하세요. 입력에 없는 대기 기간을 새로 정하지 말고, 사용자의 실제 일정이 확인되지 않았다면 날짜·시간을 임의로 확정하지 마세요.";
    }

    if(isProRisk){
      out.replies=[];
      out.meaning="확인된 사실은 상대가 답장을 재촉하는 표현을 가끔 했다는 점뿐입니다. 반복 빈도와 구체적 맥락이 부족하므로 일회성 표현인지 지속적인 압박 패턴인지는 아직 판단할 수 없습니다.";
      out.confidence="낮음";
      out.emotion="답장 재촉만으로 상대의 호감·불안·의도를 추정하지 않습니다. 현재 입력만으로 상대 감정을 확정할 근거가 없습니다.";
      out.flow="재촉 표현은 관심 신호로 환산하지 않습니다. 반복 여부, 즉시 답변 요구, 불만·비난, 사용자의 경계 무시처럼 확인 가능한 행동이 함께 나타나는지를 봐야 합니다.";
      out.strategy="사용자의 평소 답장 리듬을 유지하고, 재촉이 반복되거나 압박으로 커지는지 사실만 관찰하세요. 반복 압박이 확인되면 짧고 명확하게 연락 가능 범위를 알리는 것이 우선입니다.";
      out.caution="재촉을 호감으로 해석해 더 빨리 답하거나, 반대로 한 번의 표현만으로 상대를 위험하다고 단정하지 마세요.";
      out.dontSend="죄책감 때문에 계속 미안하다고 하거나, 아직 반복 여부가 불분명한데 상대의 성격·의도를 단정하는 메시지는 보내지 마세요.";
      out.advice="현재는 위험도를 확정하기보다 반복성과 경계 존중 여부를 확인하는 단계입니다. 사용자의 답장 속도를 상대 재촉에 맞춰 억지로 바꿀 필요는 없습니다.";
      out.nextAction="다음에 재촉 표현이 나오면 표현 내용과 맥락을 확인하세요. 즉시 답변 강요·비난·반복 압박처럼 경계를 침범하는 행동이 실제로 반복되면 그때 명확한 경계를 설정하세요.";
    }

    if(isProMonthly){
      out.replies=[];
      out.meaning="제공된 기록에서 확인되는 사실은 서로 안부 질문이 있었고, 사용자가 먼저 연락한 날과 상대가 주제를 이어간 날이 있었다는 점입니다. 횟수와 비율이 없으므로 어느 쪽이 더 많이 주도했는지는 단정하지 않습니다.";
      out.confidence="낮음";
      out.emotion="이 기록만으로 상대의 호감이나 감정 강도는 판단하지 않습니다. 월간 리포트에서는 감정보다 실제 참여 행동의 변화를 보는 것이 안전합니다.";
      out.flow="양쪽의 참여 행동이 일부 확인되지만, 선연락·역질문·대화 재개·일정 제안의 빈도가 제시되지 않아 관계 균형이나 진전 정도를 확정할 수 없습니다.";
      out.strategy="다음 기록에서도 선연락, 질문, 끊긴 대화 재개, 구체적 일정 조율처럼 확인 가능한 행동을 같은 기준으로 비교하세요.";
      out.caution="일부 상호작용만으로 관계가 균형 잡혔다거나 호감이 높아졌다고 단정하지 마세요. 입력에 없는 만남 계획이나 연락 주기도 새로 만들지 않습니다.";
      out.dontSend="월간 리포트의 추정만을 근거로 상대에게 관계 확인을 요구하거나, 입력에 없는 공통 관심사·약속을 만들어 메시지로 보내지 마세요.";
      out.advice="이번 기록은 상호 참여가 일부 있었다는 사실까지만 보여줍니다. 다음 달에는 행동 횟수와 누가 먼저 시작·재개했는지를 함께 기록하면 변화 판단이 더 정확해집니다.";
      out.nextAction="다음 달에도 같은 행동 지표를 기록해 변화만 비교하세요. 현재 기록만으로 새로운 대기 기간이나 연락 횟수 규칙을 정하지 마세요.";
    }

    if(isProMemory){
      out.replies=[];
      out.strategy="장기 기억에는 사용자가 직접 확인한 사실과 반복해서 관찰된 행동만 남기고, 호감·감정·성격 같은 AI 추론은 사실과 분리합니다.";
      out.caution="한두 번의 질문이나 반응을 호감·성격으로 변환해 저장하지 마세요. 좋아한다고 말한 취향도 잘한다거나 함께 하고 싶어 한다는 사실로 확장하지 않습니다.";
      out.dontSend="이 기능의 결과는 기억 정리용이므로 별도의 메시지를 만들 필요가 없습니다.";
      out.advice="직접 말한 취향·일정·경계와 반복 확인된 참여 행동만 저장하고, 불확실한 해석은 장기 기억에서 제외하세요.";
      out.nextAction="확인된 사실과 반복 관찰된 행동만 장기 기억에 저장하세요. 감정 가설·호감 추정·조언·임의의 연락 시점은 저장하지 마세요.";
    }

    if(isProConfession){
      const hasMeetingEvidence=/(?:만났|만남|대면|데이트)/.test(compact);
      const hasConcreteInitiative=/(?:상대(?:가|는|도)?[^.\n]{0,80}(?:먼저\s*연락|선연락|약속\s*제안|날짜\s*제안|만남\s*제안))/.test(compact);
      if(!hasMeetingEvidence && !hasConcreteInitiative){
        out.replies=[];
        out.confidence="낮음";
        out.strategy="상호 질문이 있다는 사실만으로 고백 단계라고 판단하지 않습니다. 실제 만남과 상대의 자발적 연락·대화 재개·일정 참여 같은 행동 근거를 먼저 확인하세요.";
        out.caution="일상 대화가 이어진다는 이유만으로 상대의 연애 감정이나 고백 수용 가능성을 높게 잡지 마세요.";
        out.dontSend="입력에 없는 호감이나 특별한 관계를 전제로 한 고백·떠보기 메시지는 지금 만들지 마세요.";
        out.advice="현재 정보만으로는 고백 타이밍을 정하기 어렵습니다. 상호 질문은 참여 신호일 수 있지만 고백 수용 의사를 뜻하지는 않습니다.";
        out.nextAction="고백 시점을 정하기 전에 실제 만남 여부와 상대의 선연락·대화 재개·구체적 일정 참여처럼 확인 가능한 행동을 더 확인하세요. 입력에 없는 만남이나 일정은 만들지 마세요.";
      }
    }

    if(isProDate){
      const userMoviePreference=/(?:나는|내가|저는|저도|나도)[^.\n]{0,80}(?:영화[^.\n]{0,30}(?:좋아|자주|보고\s*싶)|(?:좋아|자주|보고\s*싶)[^.\n]{0,30}영화)/.test(compact);
      if(/영화/.test(compact) && !userMoviePreference){
        out.replies=[
          {label:"가장 자연스러운 답장",text:"어떤 영화 좋아하세요?",reason:"상대가 실제로 꺼낸 영화 주제만 사용해 취향을 한 번 더 확인합니다."},
          {label:"조금 더 구체적인 답장",text:"최근에 본 영화 중에 추천할 만한 거 있어요?",reason:"사용자의 취향을 지어내지 않고 상대가 말한 주제를 자연스럽게 확장합니다."},
          {label:"가볍게 이어가는 답장",text:"영화는 어떤 장르 좋아하세요?",reason:"만남을 서두르지 않고 실제 대화 참여를 확인할 수 있는 질문입니다."}
        ];
      }
      const userHasAnyAvailability=/(?:나는|내가|저는|저도|나도|사용자)[^.\n]{0,100}(?:월요일|화요일|수요일|목요일|금요일|토요일|일요일|오늘|내일|이번\s*주|다음\s*주)[^.\n]{0,50}(?:가능|괜찮|시간\s*돼|시간\s*되)/.test(compact);
      if(!userHasAnyAvailability){
        out.nextAction="상대가 영화 주제에 계속 참여하더라도 먼저 사용자의 실제 가능한 일정을 확인하세요. 가능한 시간이 확인된 뒤에만 구체적인 만남을 제안하고, 확인 전에는 임의의 날짜·시간·장소를 넣지 마세요.";
      }
    }
  }

'''
s = s.replace(marker, block + marker, 1)
p.write_text(s, encoding="utf-8")
