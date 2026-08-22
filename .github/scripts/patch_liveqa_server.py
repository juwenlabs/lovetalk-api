from pathlib import Path
import re

p=Path('server.js')
s=p.read_text(encoding='utf-8')

s=re.sub(r'const SERVER_VERSION = "[^"]+";', 'const SERVER_VERSION = "2026-08-23-potentia-v16-quality";', s, count=1)

# Strengthen points that live QA showed were still too loose.
old='''- 기본은 짧고 자연스러운 한국어 한두 문장, 질문은 한 번에 하나. 장문 해명, 질문 폭탄, 무리한 개그, 개인 밈, 과한 이모티콘을 피한다. 공유된 실제 말투는 존중한다.'''
new='''- 기본은 짧고 자연스러운 한국어 한두 문장, 질문은 한 번에 하나. 장문 해명, 질문 폭탄, 무리한 개그, 개인 밈, 과한 이모티콘을 피한다. 공유된 실제 말투는 존중한다.
- 번호 교환 직후·소개팅·앱 매칭·초기 낯선 관계에서 사용자가 이미 반말 관계라고 명시하지 않았다면 존댓말을 기본으로 한다. 상대 이름을 불필요하게 반복하지 않는다.
- 한 번의 짧은 답장만으로 대화 의욕·호감 수준을 정하지 않는다. 첫 짧은 답장에는 낮은 위험의 짧은 반응과 필요하면 개방형 질문 하나로 한 번 더 흐름을 확인한다.
- '언제 한번 봐요', '시간 되면 만나요'처럼 모호한 제안을 구체적 약속이라고 부르지 않는다. 참여가 충분하고 약속을 제안할 단계일 때만 앞 맥락 + 활동/장소 + 실제로 제안 가능한 구체적 시점을 사용한다. 사용자의 일정 정보가 없으면 임의의 날짜를 사실처럼 만들지 않는다.
- 명확한 이성적 거절에는 관계를 다시 열어두는 문장('좋은 인연으로 남아요', '나중에 다시')이나 추가 만남의 여지를 붙이지 않는다. 짧게 수용하고 종료한다.
- 개인정보·금전·협박·스토킹 등 안전 위험에서는 ㅋㅋ, 농담, 장난스러운 말투, 가벼운 이모지를 쓰지 않는다. 차분하고 명확한 경계와 다음 안전 행동을 우선한다.
- 사용자가 설득하고 싶거나 불안하다고 말해도 사용자를 비난하거나 도덕적으로 평가하지 않는다. 왜 그 행동을 멈추는 편이 관계·경계 측면에서 적절한지 행동 중심으로 설명한다.'''
assert old in s, 'system message quality anchor missing'
s=s.replace(old,new,1)

old2='''- 사실, 사용자의 해석, AI 가설을 구분한다. 답장 속도, 메시지 길이, 이모티콘, 스토리 조회, 좋아요, 한 번의 거절/선연락 같은 단일 신호로 호감이나 속마음을 확정하지 않는다.'''
new2='''- 사실, 사용자의 해석, AI 가설을 구분한다. 답장 속도, 메시지 길이, 이모티콘, 스토리 조회, 좋아요, 한 번의 거절/선연락 같은 단일 신호로 호감이나 속마음을 확정하지 않는다.
- 참여도는 행동 강도를 정하는 내부 운영값일 뿐 호감 확률이 아니다. 사용자에게 '호감 중간~높음'처럼 준점수 형태로 포장하지 말고, 확인된 참여 행동과 판단 확신도(높음/중간/낮음)를 분리해 설명한다.'''
assert old2 in s, 'fact anchor missing'
s=s.replace(old2,new2,1)

# Make detailed output compact enough to finish reliably while keeping its useful sections.
repls={
'핵심 의미와 맥락 2~4문장':'핵심 의미와 맥락 2~3문장',
'감정·거리감·관심도의 가능성 2~4문장':'감정·거리감에 대한 가능한 해석 1~2문장. 확인되지 않은 호감 강도를 점수처럼 표현하지 말 것',
'대화 흐름과 태도 변화 2~4문장':'대화 흐름과 태도 변화 1~2문장',
'답장 목표와 톤 2~4문장':'답장 목표와 톤 1~2문장',
'피하면 좋은 행동 2~3문장':'피하면 좋은 행동 1~2문장',
'현재 타이밍 판단 + 다음 연락 시점 + 그때까지 행동 방법 3~5문장':'현재 타이밍 판단 + 다음 연락 시점 + 그때까지 행동 방법 2~3문장'
}
for a,b in repls.items():
    assert a in s, f'detail length anchor missing: {a}'
    s=s.replace(a,b,1)

# Retry if Claude itself says the output hit max_tokens, not only when parsing fails.
old3='''    if(!validAnalysisResult(parsed)){
      const retryContent=Array.isArray(content)?[...content,{type:"text",text:`중요: 위에서 지정한 [[meaning]], [[emotion]], reply 표식을 정확히 지켜 완전한 결과를 다시 출력하세요. 코드블록과 머리말은 금지합니다.`}]:content;
      ai=await anthropic.messages.create({model,system:POTENTIA_SYSTEM_PROMPT,max_tokens:isDetail?1900:900,messages:[{role:"user",content:retryContent}]});'''
new3='''    if(ai.stop_reason==="max_tokens" || !validAnalysisResult(parsed)){
      const retryContent=Array.isArray(content)?[...content,{type:"text",text:`중요: 위에서 지정한 [[meaning]], [[emotion]], reply 표식을 정확히 지켜 완전한 결과를 다시 출력하세요. 각 섹션은 요구된 문장 수 안에서 간결하게 끝내고 코드블록과 머리말은 금지합니다.`}]:content;
      ai=await anthropic.messages.create({model,system:POTENTIA_SYSTEM_PROMPT,max_tokens:isDetail?2200:900,messages:[{role:"user",content:retryContent}]});'''
assert old3 in s, 'retry anchor missing'
s=s.replace(old3,new3,1)

# Give detailed first pass and detailed stream a little more headroom.
s=s.replace('max_tokens:isDetail?1700:750','max_tokens:isDetail?1850:750',1)
s=s.replace('maxTokens:isDetail?1700:750','maxTokens:isDetail?1850:750',1)

# Ensure a second max-token truncation is not silently treated as a complete result.
old4='''      parsed=parseAnalysisSectionsText(getClaudeText(ai),isDetail,selectedSituation);
    }
    if(!validAnalysisResult(parsed)) throw new Error("AI 분석 섹션을 정상적으로 파싱하지 못했습니다.");'''
new4='''      parsed=parseAnalysisSectionsText(getClaudeText(ai),isDetail,selectedSituation);
    }
    if(ai.stop_reason==="max_tokens") throw new Error("AI 상세 분석이 끝까지 생성되지 않아 다시 시도해 주세요.");
    if(!validAnalysisResult(parsed)) throw new Error("AI 분석 섹션을 정상적으로 파싱하지 못했습니다.");'''
assert old4 in s, 'post-retry anchor missing'
s=s.replace(old4,new4,1)

# Static safeguards for accidental regressions.
assert '2026-08-23-potentia-v16-quality' in s
assert '한 번의 짧은 답장만으로 대화 의욕' in s
assert '개인정보·금전·협박·스토킹 등 안전 위험에서는 ㅋㅋ' in s
assert s.count('system:POTENTIA_SYSTEM_PROMPT') >= 4

p.write_text(s,encoding='utf-8')
print('Potentia v16 quality patch applied')
