from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')

old_version='const SERVER_VERSION = "2026-08-23-potentia-v60-fast-pro-grounding-polish";'
new_version='const SERVER_VERSION = "2026-08-23-potentia-v61-faster-pro-cache-compact";'
if old_version not in s:
    raise SystemExit('v60 version marker missing')
s=s.replace(old_version,new_version,1)

# Cache the long, stable system prompt. The varying user content remains outside the cached prefix.
old_system='system:POTENTIA_SYSTEM_PROMPT'
new_system='system:[{type:"text",text:POTENTIA_SYSTEM_PROMPT,cache_control:{type:"ephemeral"}}]'
count=s.count(old_system)
if count < 2:
    raise SystemExit(f'expected multiple system prompt calls, found {count}')
s=s.replace(old_system,new_system)

old_compact='''  const compactInstruction={type:"text",text:"\\n[출력 길이 제한] 이 작업은 장기 저장/요약용입니다. 모든 필수 섹션과 reply1~3은 유지하되 각 섹션은 핵심 1~2문장만 쓰고 전체를 약 1700자 안에 끝내세요. 반복 설명은 금지하고 nextAction까지 반드시 완결하세요."};'''
new_compact='''  const compactInstruction={type:"text",text:"\\n[빠른 PRO 출력] 모든 필수 섹션과 reply1~3 마커는 유지하세요. 각 섹션은 핵심 한 문장만, reply는 짧은 한 문장과 짧은 이유만 쓰세요. 반복 설명은 금지하고 전체를 약 900자 안에 끝내며 nextAction까지 반드시 완결하세요. 입력에 없는 감정·일정·사실은 만들지 마세요."};'''
if old_compact not in s:
    raise SystemExit('compact instruction anchor missing')
s=s.replace(old_compact,new_compact,1)

old_detail='''  const detailInstruction={type:"text",text:"\\n[상세분석 출력 길이] 모든 필수 섹션과 reply1~3을 유지하되 각 섹션은 핵심 1~2문장, 각 추천문장은 1문장으로 쓰고 전체를 약 1900자 안에 끝내세요. 입력에 없는 감정·일정·사실을 만들지 말고 nextAction까지 반드시 완결하세요."};'''
new_detail='''  const detailInstruction={type:"text",text:"\\n[빠른 상세분석 출력] 모든 필수 섹션과 reply1~3 마커는 유지하세요. 각 섹션은 핵심 한 문장만, 각 추천문장은 한 문장과 짧은 이유만 쓰세요. 전체를 약 1100자 안에 끝내고 nextAction까지 반드시 완결하세요. 입력에 없는 감정·일정·사실은 만들지 마세요."};'''
if old_detail not in s:
    raise SystemExit('detail instruction anchor missing')
s=s.replace(old_detail,new_detail,1)

old_first='''  let ai=await anthropic.messages.create({model,system:[{type:"text",text:POTENTIA_SYSTEM_PROMPT,cache_control:{type:"ephemeral"}}],max_tokens:isDetail?(compactProTask?1800:2100):850,messages:[{role:"user",content:requestContent}]});'''
new_first='''  let ai=await anthropic.messages.create({model,system:[{type:"text",text:POTENTIA_SYSTEM_PROMPT,cache_control:{type:"ephemeral"}}],max_tokens:isDetail?(compactProTask?1100:1350):850,messages:[{role:"user",content:requestContent}]});'''
if old_first not in s:
    raise SystemExit('first analysis token anchor missing')
s=s.replace(old_first,new_first,1)

old_retry_text='''    const retryInstruction={type:"text",text:`중요: 이전 출력이 너무 길거나 불완전했습니다. 위의 모든 [[section]]과 reply1~3을 빠짐없이 유지하되 전체를 ${compactProTask?"1500":"2200"}자 안으로 압축해 처음부터 다시 출력하세요. 각 섹션은 핵심만 쓰고 nextAction은 반드시 완결된 문장으로 끝내세요. 코드블록과 머리말은 금지합니다.`};'''
new_retry_text='''    const retryInstruction={type:"text",text:`중요: 이전 출력이 불완전했습니다. 모든 [[section]]과 reply1~3 마커를 빠짐없이 유지하고 전체를 ${compactProTask?"850":"1050"}자 안으로 압축해 처음부터 다시 출력하세요. 각 섹션은 핵심 한 문장만 쓰고 nextAction은 반드시 완결하세요. 코드블록과 머리말은 금지합니다.`};'''
if old_retry_text not in s:
    raise SystemExit('retry instruction anchor missing')
s=s.replace(old_retry_text,new_retry_text,1)

old_retry_call='''    ai=await anthropic.messages.create({model,system:[{type:"text",text:POTENTIA_SYSTEM_PROMPT,cache_control:{type:"ephemeral"}}],max_tokens:isDetail?(compactProTask?1900:2300):1100,messages:[{role:"user",content:retryContent}]});'''
new_retry_call='''    ai=await anthropic.messages.create({model,system:[{type:"text",text:POTENTIA_SYSTEM_PROMPT,cache_control:{type:"ephemeral"}}],max_tokens:isDetail?(compactProTask?1200:1450):1100,messages:[{role:"user",content:retryContent}]});'''
if old_retry_call not in s:
    raise SystemExit('retry token anchor missing')
s=s.replace(old_retry_call,new_retry_call,1)

p.write_text(s,encoding='utf-8')
print('patched system calls:',count)
