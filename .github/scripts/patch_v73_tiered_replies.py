from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')
old='const SERVER_VERSION = "2026-08-24-potentia-v72-grounded-detail-reply";'
new='const SERVER_VERSION = "2026-08-24-potentia-v73-tiered-replies";'
if old not in s: raise SystemExit('v72 marker missing')
s=s.replace(old,new,1)

# Starter AI path: free generates only one message; PRO keeps three.
anchor='''  const prompt=`\n사용자가 지금 그 사람에게 먼저 보낼 카카오톡/DM 첫 메시지 3개를 만들어주세요. 이 작업은 답장 추천이 아닙니다.'''
replacement='''  const desiredStarterReplies=advanced?3:1;\n  const prompt=`\n사용자가 지금 그 사람에게 먼저 보낼 카카오톡/DM 첫 메시지 ${desiredStarterReplies}개를 만들어주세요. 이 작업은 답장 추천이 아닙니다.'''
if anchor not in s: raise SystemExit('starter prompt anchor missing')
s=s.replace(anchor,replacement,1)
s=s.replace('- 정보가 부족해도 질문하지 말고 바로 3개를 작성하세요.','- 정보가 부족해도 추가 질문하지 말고 바로 ${desiredStarterReplies}개를 작성하세요.',1)
old_json='''JSON만 출력하세요.\n{"replies":[{"label":"자연스럽게","text":"먼저 보낼 메시지","reason":"이유 1문장"},{"label":"다정하게","text":"먼저 보낼 메시지","reason":"이유 1문장"},{"label":"센스 있게","text":"먼저 보낼 메시지","reason":"이유 1문장"}]}\n`;'''
new_json='''JSON만 출력하세요.\n${advanced\n  ? '{"replies":[{"label":"자연스럽게","text":"먼저 보낼 메시지","reason":"이유 1문장"},{"label":"다정하게","text":"먼저 보낼 메시지","reason":"이유 1문장"},{"label":"센스 있게","text":"먼저 보낼 메시지","reason":"이유 1문장"}]}'\n  : '{"replies":[{"label":"자연스럽게","text":"가장 자연스러운 먼저 보낼 메시지","reason":"이유 1문장"}]}' }\n`;'''
if old_json not in s: raise SystemExit('starter JSON anchor missing')
s=s.replace(old_json,new_json,1)
old_validate='''  let parsed=await createFastStarterJson({content:prompt,advanced:!!advanced});\n  if(!Array.isArray(parsed.replies)||parsed.replies.length<3) throw new Error("AI가 추천 문장 3개를 반환하지 않았습니다.");\n  parsed.replies=parsed.replies.slice(0,3).map((x,i)=>sanitizeReplyObject(x,selectedSituation,["자연스럽게","다정하게","센스 있게"][i]));'''
new_validate='''  let parsed=await createFastStarterJson({content:prompt,advanced:!!advanced});\n  if(!Array.isArray(parsed.replies)||parsed.replies.length<desiredStarterReplies) throw new Error(`AI가 추천 문장 ${desiredStarterReplies}개를 반환하지 않았습니다.`);\n  parsed.replies=parsed.replies.slice(0,desiredStarterReplies).map((x,i)=>sanitizeReplyObject(x,selectedSituation,["자연스럽게","다정하게","센스 있게"][i]));'''
if old_validate not in s: raise SystemExit('starter validate anchor missing')
s=s.replace(old_validate,new_validate,1)

# Starter JSON + SSE endpoints: hard cap free=1, PRO=3 for every deterministic/model path.
old_endpoint='''    if(guard) return res.json({...guard,advanced,serverVersion:SERVER_VERSION});\n    res.json({...result,advanced,serverVersion:SERVER_VERSION});'''
new_endpoint='''    if(guard) return res.json({...guard,advanced,serverVersion:SERVER_VERSION});\n    const starterLimit=advanced?3:1;\n    const tieredResult={...result,replies:Array.isArray(result?.replies)?result.replies.slice(0,starterLimit):[]};\n    res.json({...tieredResult,advanced,serverVersion:SERVER_VERSION});'''
if old_endpoint not in s: raise SystemExit('starter endpoint anchor missing')
s=s.replace(old_endpoint,new_endpoint,1)
old_stream='''      const replies=Array.isArray(result?.replies)?result.replies:[];\n      replies.slice(0,3).forEach((value,i)=>sendSse(res,"section",{name:`reply${i+1}`,value}));'''
new_stream='''      const replies=Array.isArray(result?.replies)?result.replies:[];\n      const starterLimit=req.body?.advanced?3:1;\n      replies.slice(0,starterLimit).forEach((value,i)=>sendSse(res,"section",{name:`reply${i+1}`,value}));'''
if old_stream not in s: raise SystemExit('starter stream anchor missing')
s=s.replace(old_stream,new_stream,1)

# Compact answer path: free quick=1, paid detail=3.
old_prompt='''  const prompt=isDetail\n    ? `${taskData}\\n\\n상대 반응과 흐름을 사실 중심으로 짧게 분석하고 실제 답장 2개를 추천하세요.'''
new_prompt='''  const desiredReplyCount=isDetail?3:1;\n  const prompt=isDetail\n    ? `${taskData}\\n\\n상대 반응과 흐름을 사실 중심으로 짧게 분석하고 실제 답장 3개를 추천하세요.'''
if old_prompt not in s: raise SystemExit('compact detail prompt anchor missing')
s=s.replace(old_prompt,new_prompt,1)
s=s.replace('''"replies":[{"label":"자연스럽게","text":"짧은 답장","reason":"짧은 이유"},{"label":"다른 느낌","text":"짧은 답장","reason":"짧은 이유"}]}`\n    : `${taskData}\\n\\n지금 답장에 필요한 핵심만 1문장으로 판단하고 실제 답장 2개를 추천하세요.''','''"replies":[{"label":"자연스럽게","text":"짧은 답장","reason":"짧은 이유"},{"label":"다른 느낌","text":"짧은 답장","reason":"짧은 이유"},{"label":"조금 더 여유 있게","text":"짧은 답장","reason":"짧은 이유"}]}`\n    : `${taskData}\\n\\n지금 답장에 필요한 핵심만 1문장으로 판단하고 실제 답장 1개를 추천하세요.''',1)
s=s.replace('''JSON만 출력: {"meaning":"핵심 1문장","action":"한 줄 조언","replies":[{"label":"자연스럽게","text":"짧은 답장","reason":"짧은 이유"},{"label":"다른 느낌","text":"짧은 답장","reason":"짧은 이유"}]}`;''','''JSON만 출력: {"meaning":"핵심 1문장","action":"한 줄 조언","replies":[{"label":"자연스럽게","text":"짧은 답장","reason":"짧은 이유"}]}`;''',1)
s=s.replace('''  try{raw=await run(isDetail?320:260);}catch(_){raw=await run(isDetail?440:370,"JSON을 완전하게 닫아 더 짧게 다시 출력하세요.");}''','''  try{raw=await run(isDetail?430:190);}catch(_){raw=await run(isDetail?560:290,"JSON을 완전하게 닫아 더 짧게 다시 출력하세요.");}''',1)
old_map='''  const list=Array.isArray(raw?.replies)?raw.replies:[];\n  out.replies=list.slice(0,2).map((x,i)=>sanitizeReplyObject(x,selectedSituation,["가장 자연스러운 답장","다른 느낌의 답장"][i]));\n  if(!meaning||!action||out.replies.length<2||(isDetail&&!signal)) throw new Error("빠른 답장 분석 결과가 불완전합니다.");'''
new_map='''  const list=Array.isArray(raw?.replies)?raw.replies:[];\n  const replyLabels=["가장 자연스러운 답장","다른 느낌의 답장","조금 더 여유 있는 답장"];\n  out.replies=list.slice(0,desiredReplyCount).map((x,i)=>sanitizeReplyObject(x,selectedSituation,replyLabels[i]));\n  if(!meaning||!action||out.replies.length<desiredReplyCount||(isDetail&&!signal)) throw new Error("빠른 답장 분석 결과가 불완전합니다.");'''
if old_map not in s: raise SystemExit('compact reply map anchor missing')
s=s.replace(old_map,new_map,1)
s=s.replace('''    out.replies=out.replies.slice(0,2);''','''    out.replies=out.replies.slice(0,desiredReplyCount);''',1)

# Instant paid detail common case gets the promised third option.
old_two='''          {label:"가장 자연스러운 답장",text:"오늘 많이 바쁘셨군요. 어떤 일 때문에 바쁘셨어요?",reason:"상대가 직접 말한 바쁜 하루만 사용하고 사용자의 하루는 만들지 않습니다."},\n          {label:"다른 느낌의 답장",text:"이제 집에 오셨군요. 오늘 하루는 어떠셨어요?",reason:"확인된 귀가 상황에서 질문 하나로 자연스럽게 이어갑니다."}\n        ]'''
new_three='''          {label:"가장 자연스러운 답장",text:"오늘 많이 바쁘셨군요. 어떤 일 때문에 바쁘셨어요?",reason:"상대가 직접 말한 바쁜 하루만 사용하고 사용자의 하루는 만들지 않습니다."},\n          {label:"다른 느낌의 답장",text:"이제 집에 오셨군요. 오늘 하루는 어떠셨어요?",reason:"확인된 귀가 상황에서 질문 하나로 자연스럽게 이어갑니다."},\n          {label:"조금 더 가볍게",text:"오늘 많이 바쁘셨네요. 이제 좀 여유가 생기셨어요?",reason:"상대가 말한 바쁜 하루와 귀가 사실만 사용합니다."}\n        ]'''
if old_two not in s: raise SystemExit('instant detail two replies anchor missing')
s=s.replace(old_two,new_three,1)

# Final API-level cap protects all existing deterministic cases: free=1, paid/detail=3.
anchor_api='''app.post("/api/love-analysis", async (req,res)=>{\n  try{\n    const {parsed}=await generateAnalysisResult(req.body||{});\n    res.json({...parsed,serverVersion:SERVER_VERSION});'''
replace_api='''function applyTierReplyLimit(parsed,reqBody){\n  if(!parsed||typeof parsed!=="object") return parsed;\n  if(!Array.isArray(parsed.replies)) return parsed;\n  const paid=!!reqBody?.advanced || String(reqBody?.mode||"")==="detail";\n  return {...parsed,replies:parsed.replies.slice(0,paid?3:1)};\n}\n\napp.post("/api/love-analysis", async (req,res)=>{\n  try{\n    const {parsed}=await generateAnalysisResult(req.body||{});\n    const tiered=applyTierReplyLimit(parsed,req.body||{});\n    res.json({...tiered,serverVersion:SERVER_VERSION});'''
if anchor_api not in s: raise SystemExit('analysis API anchor missing')
s=s.replace(anchor_api,replace_api,1)
old_analysis_stream='''    const {parsed,isDetail}=await generateAnalysisResult(req.body||{});\n    const order=isDetail?["meaning","confidence","emotion","flow","strategy","caution","dontSend","reply1","reply2","reply3","advice","nextAction"]:["meaning","emotion","caution","reply1","reply2","reply3","advice","nextAction"];'''
new_analysis_stream='''    const generated=await generateAnalysisResult(req.body||{});\n    const isDetail=generated.isDetail;\n    const parsed=applyTierReplyLimit(generated.parsed,req.body||{});\n    const order=isDetail?["meaning","confidence","emotion","flow","strategy","caution","dontSend","reply1","reply2","reply3","advice","nextAction"]:["meaning","emotion","caution","reply1","advice","nextAction"];'''
if old_analysis_stream not in s: raise SystemExit('analysis stream anchor missing')
s=s.replace(old_analysis_stream,new_analysis_stream,1)

p.write_text(s,encoding='utf-8')
