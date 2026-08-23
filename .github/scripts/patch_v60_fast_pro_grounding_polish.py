from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')
old_version='const SERVER_VERSION = "2026-08-23-potentia-v59-fast-pro-grounding";'
new_version='const SERVER_VERSION = "2026-08-23-potentia-v60-fast-pro-grounding-polish";'
if old_version not in s:
    raise SystemExit('v59 marker missing')
s=s.replace(old_version,new_version,1)

old='''    if(Array.isArray(out.replies)) out.replies=out.replies.filter(r=>{\n      const text=String(r?.text||"").trim();\n      return text && !placeholderReply.test(text);\n    });\n\n    if(!inputHasExplicitTiming'''
new='''    const metaInstructionReply=/(?:구체적[^.\\n]{0,50}(?:대화|메시지)[^.\\n]{0,50}(?:없|필요)|답장을\\s*추천하기\\s*어렵|답변\\s*\\+|역질문\\s*1개를\\s*함께\\s*보내|형태로[^.\\n]{0,60}(?:이어가|마치)|상대의\\s*다음[^.\\n]{0,50}기다린\\s*후)/;\n    if(Array.isArray(out.replies)) out.replies=out.replies.filter(r=>{\n      const text=String(r?.text||"").trim();\n      return text && !placeholderReply.test(text) && !metaInstructionReply.test(text);\n    });\n    const isNamedProTask=isProConfession||isProDate||isProRisk||isProMonthly||isProMemory;\n    const looksLikeDirectDialogue=/\\n/.test(msg)||/(?:상대|나|저|사용자)\\s*[:：]/.test(msg)||/["“”]/.test(msg);\n    if(!isNamedProTask && !looksLikeDirectDialogue){\n      out.replies=[];\n      out.advice="현재 입력은 관계 상황 요약이므로 특정 답장 문장을 만들기보다 확인된 참여 행동만 기준으로 보는 것이 정확합니다. 실제 답장 추천이 필요하면 최근 대화 문장을 그대로 입력하세요.";\n      out.nextAction="현재 정보만으로 특정 연락 시점이나 답장을 새로 만들지 마세요. 실제 최근 대화 문장이 있을 때 입력된 사실만 사용해 다음 행동을 정하세요.";\n    }\n\n    const generatedArbitraryPeriod=/(?:최근\\s*)?\\d+\\s*~\\s*\\d+\\s*(?:일|주)|\\d+\\s*(?:일|주)\\s*(?:뒤|동안)|며칠\\s*(?:뒤|동안)|한두\\s*번(?:\\s*더|의\\s*흐름|의\\s*사이클)/;\n    if(!inputHasExplicitTiming){\n      if(generatedArbitraryPeriod.test(String(out.strategy||""))) out.strategy="입력에서 확인되는 사실과 상대의 실제 참여 행동만 기준으로 다음 단계를 판단하세요. 임의의 관찰 횟수나 대기 기간을 새로 정하지 않습니다.";\n      if(generatedArbitraryPeriod.test(String(out.advice||""))) out.advice="입력된 사실만 기준으로 판단하세요. 더 정확한 분석이 필요하면 임의의 기간을 정하기보다 실제 최근 대화 내용을 그대로 제공하는 편이 낫습니다.";\n    }\n\n    if(!inputHasExplicitTiming'''
if old not in s:
    raise SystemExit('reply sanitation anchor missing')
s=s.replace(old,new,1)

old_conf='''        out.replies=[];\n        out.confidence="낮음";\n        out.strategy="상호 질문이 있다는 사실만으로 고백 단계라고 판단하지 않습니다. 실제 만남과 상대의 자발적 연락·대화 재개·일정 참여 같은 행동 근거를 먼저 확인하세요.";'''
new_conf='''        out.replies=[];\n        out.meaning="확인된 사실은 최근 일상 대화가 이어지고 서로 질문을 주고받는다는 점입니다. 이 정보만으로 고백 수용 가능성이나 관계 단계의 진전을 확정하지 않습니다.";\n        out.confidence="낮음";\n        out.emotion="상대가 질문에 참여한다는 행동은 확인되지만, 연애 감정이나 고백을 원하는지는 입력에 없습니다.";\n        out.flow="상호 질문과 일상 대화가 이어진다는 참여 행동은 확인되지만, 실제 만남·통화·상대의 선연락·구체적 일정 조율 여부는 입력에 없습니다.";\n        out.strategy="상호 질문이 있다는 사실만으로 고백 단계라고 판단하지 않습니다. 실제 만남과 상대의 자발적 연락·대화 재개·일정 참여 같은 행동 근거를 먼저 확인하세요.";'''
if old_conf not in s:
    raise SystemExit('confession anchor missing')
s=s.replace(old_conf,new_conf,1)

old_date='''      if(/영화/.test(compact) && !userMoviePreference){\n        out.replies=['''
new_date='''      if(/영화/.test(compact) && !userMoviePreference){\n        out.meaning="확인된 사실은 대화가 이어지고 상대가 영화 이야기를 했다는 점입니다. 영화 주제 하나만으로 만남 제안을 원한다거나 호감이 높다고 판단하지 않습니다.";\n        out.confidence="낮음";\n        out.emotion="상대가 영화 주제에 참여한 것은 대화 행동으로 볼 수 있지만, 만남 의향이나 감정 강도는 입력에 없습니다.";\n        out.flow="사용자는 대화가 자연스럽게 이어진다고 설명했고 상대가 영화 이야기를 했습니다. 그 외에 선연락·약속 제안·구체적 일정 참여 여부는 확인되지 않았습니다.";\n        out.replies=['''
if old_date not in s:
    raise SystemExit('date anchor missing')
s=s.replace(old_date,new_date,1)

p.write_text(s,encoding='utf-8')
