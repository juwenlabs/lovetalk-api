from pathlib import Path
import re

p=Path('server.js')
s=p.read_text(encoding='utf-8')
s=re.sub(r'const SERVER_VERSION = "[^"]+";', 'const SERVER_VERSION = "2026-08-23-potentia-v18-grounded-complete";', s, count=1)

# Never invent context merely to make a reply sound natural.
anchor='''- 사실, 사용자의 해석, AI 가설을 구분한다. 답장 속도, 메시지 길이, 이모티콘, 스토리 조회, 좋아요, 한 번의 거절/선연락 같은 단일 신호로 호감이나 속마음을 확정하지 않는다.'''
insert='''- 사실, 사용자의 해석, AI 가설을 구분한다. 답장 속도, 메시지 길이, 이모티콘, 스토리 조회, 좋아요, 한 번의 거절/선연락 같은 단일 신호로 호감이나 속마음을 확정하지 않는다.
- 사용자가 제공하지 않은 현재 날씨, 장소, 일정, 직업 사정, 상대의 피곤함·기분·의도·활동을 사실처럼 만들어 답장에 넣지 않는다. 필요한 정보가 없으면 추측을 문장 재료로 채우지 말고 입력된 사실만 사용하거나 낮은 위험의 질문으로 확인한다.
- 상대가 단 한 번 짧게 답한 경우 '대화할 여유가 있다', '열려 있다', '호감이 낮다/높다'처럼 참여나 감정을 판정하지 않는다. 확인 가능한 사실은 짧게 답했다는 것뿐이라고 두고 한 번 더 자연스럽게 흐름을 확인한다.'''
assert anchor in s, 'fact grounding anchor missing'
s=s.replace(anchor,insert,1)

# Tighten quick analysis wording so single-signal cases explicitly preserve uncertainty.
s=s.replace('''[[meaning]]\n핵심 의미 1문장\n[[emotion]]\n감정/태도 가능성 1문장''','''[[meaning]]\n확인된 사실과 정보 한계를 함께 반영한 핵심 의미 1문장\n[[emotion]]\n감정/태도는 단일 신호로 확정하지 말고, 근거가 부족하면 판단 유보를 명시한 1문장''',1)

# Put hard size ceilings on detail sections. Detailed means structured, not verbose.
replacements={
'''[[meaning]]\n핵심 의미와 맥락 2~3문장''':'''[[meaning]]\n핵심 의미와 맥락 2문장 이내, 약 220자 이내''',
'''[[emotion]]\n감정·거리감에 대한 가능한 해석 1~2문장. 확인되지 않은 호감 강도를 점수처럼 표현하지 말 것''':'''[[emotion]]\n감정·거리감에 대한 가능한 해석 2문장 이내, 약 160자 이내. 확인되지 않은 호감 강도를 점수처럼 표현하지 말 것''',
'''[[flow]]\n대화 흐름과 태도 변화 1~2문장''':'''[[flow]]\n대화 흐름과 태도 변화 2문장 이내, 약 160자 이내''',
'''[[strategy]]\n답장 목표와 톤 1~2문장''':'''[[strategy]]\n답장 목표와 톤 2문장 이내, 약 160자 이내''',
'''[[caution]]\n피하면 좋은 행동 1~2문장''':'''[[caution]]\n피하면 좋은 행동 2문장 이내, 약 140자 이내''',
'''[[advice]]\n한 줄 조언''':'''[[advice]]\n한 줄 조언, 약 100자 이내''',
'''[[nextAction]]\n현재 타이밍 판단 + 다음 연락 시점 + 그때까지 행동 방법 2~3문장''':'''[[nextAction]]\n현재 타이밍 판단 + 다음 연락 시점 + 그때까지 행동 방법 3문장 이내, 약 240자 이내\n[[lengthRule]]\n전체 출력은 모든 표식과 reply JSON을 포함해 약 2600자 안에서 반드시 끝낼 것'''
}
for a,b in replacements.items():
    assert a in s, f'missing detail anchor: {a}'
    s=s.replace(a,b,1)

# Parser should require the product's complete set, not a single reply.
old='''function validAnalysisResult(x){ return !!(x && x.meaning && Array.isArray(x.replies) && x.replies.length>=1); }'''
new='''function validAnalysisResult(x,isDetail){
  const base=!!(x && x.meaning && x.emotion && x.caution && x.advice && x.nextAction && Array.isArray(x.replies) && x.replies.length>=3);
  return isDetail ? !!(base && x.flow && x.strategy) : base;
}
function analysisEndingLooksComplete(x){
  const t=String(x?.nextAction||"").trim();
  return !!t && /[.!?。]$/.test(t);
}'''
assert old in s, 'validAnalysisResult anchor missing'
s=s.replace(old,new,1)

s=s.replace('!validAnalysisResult(parsed)', '!validAnalysisResult(parsed,isDetail)')
s=s.replace('''if(ai.stop_reason==="max_tokens") throw new Error("AI 상세 분석이 끝까지 생성되지 않아 다시 시도해 주세요.");\n    if(!validAnalysisResult(parsed,isDetail)) throw new Error("AI 분석 섹션을 정상적으로 파싱하지 못했습니다.");''','''if(ai.stop_reason==="max_tokens" && !analysisEndingLooksComplete(parsed)) throw new Error("AI 상세 분석이 끝까지 생성되지 않아 다시 시도해 주세요.");
    if(!validAnalysisResult(parsed,isDetail)) throw new Error("AI 분석 섹션을 정상적으로 파싱하지 못했습니다.");''',1)

# Retry specifically requests a compact full answer rather than allowing another long generation.
old_retry='''중요: 위에서 지정한 [[meaning]], [[emotion]], reply 표식을 정확히 지켜 완전한 결과를 다시 출력하세요. 각 섹션은 요구된 문장 수 안에서 간결하게 끝내고 코드블록과 머리말은 금지합니다.'''
new_retry='''중요: 이전 출력이 너무 길거나 불완전했습니다. 위의 모든 [[section]]과 reply1~3을 빠짐없이 유지하되 전체를 약 2200자 안으로 압축해 처음부터 다시 출력하세요. 각 섹션의 글자 제한을 지키고 nextAction은 반드시 완결된 문장으로 끝내세요. 코드블록과 머리말은 금지합니다.'''
assert old_retry in s, 'retry text anchor missing'
s=s.replace(old_retry,new_retry,1)

# Retain enough headroom, but compact prompts should normally finish on first call.
s=s.replace('max_tokens:isDetail?1850:750','max_tokens:isDetail?1900:750',1)
s=s.replace('max_tokens:isDetail?2200:900','max_tokens:isDetail?2100:900',1)
s=s.replace('maxTokens:isDetail?1850:750','maxTokens:isDetail?1900:750',1)

assert '2026-08-23-potentia-v18-grounded-complete' in s
assert '현재 날씨, 장소, 일정' in s
assert '전체 출력은 모든 표식과 reply JSON을 포함해 약 2600자' in s
assert 'analysisEndingLooksComplete' in s
p.write_text(s,encoding='utf-8')
print('Potentia v18 grounded/completeness patch applied')
