from pathlib import Path
import re

p=Path('server.js')
s=p.read_text(encoding='utf-8')

assert '2026-08-23-potentia-v28-truthful-messages' in s, 'expected v28 server not found'
s=s.replace('const SERVER_VERSION = "2026-08-23-potentia-v28-truthful-messages";', 'const SERVER_VERSION = "2026-08-23-potentia-v29-coach-safety";', 1)

# 1) Deterministic starter safety guards for manual 20.2/20.3 risk cases.
anchor='''  if(/빌려달|송금|대출|보증|급전|금전/.test(t)) return stop("금전 요구가 포함된 상황이에요.","관계를 유지하기 위한 선톡보다 금전 거래를 거절하고 개인정보·송금을 추가로 제공하지 않는 것이 우선이에요. 필요하면 ‘금전 거래는 어렵습니다.’처럼 짧게 경계를 세우세요.");'''
insert='''  if(/(?:협박|폭력|스토킹|해코지|죽여|때리|찾아가서)/.test(t)) return stop("협박·폭력·스토킹 가능성이 있는 안전 위험 상황이에요.","일반적인 선톡이나 관계 기술보다 안전한 거리두기와 증거 보존이 우선이에요. 상대를 자극하는 도발 문장을 만들지 말고, 필요하면 신뢰할 수 있는 사람이나 관련 기관의 도움을 받으세요.");
  if(/(?:자해\\s*협박|자살|죽겠|죽을\\s*거|극단적\\s*선택)/.test(t)) return stop("자해 위협이 포함된 고위험 상황이에요.","연애 기술로 달래거나 책임을 떠안는 문장을 만들기보다 즉각적인 안전을 우선하세요. 급박한 위험이면 주변의 신뢰할 수 있는 사람이나 지역 응급·전문 도움을 연결하는 것이 우선입니다.");
  if(/(?:사진|영상|사적\\s*사진).{0,30}(?:유포|퍼뜨|공개|협박)|(?:유포|퍼뜨).{0,30}(?:사진|영상)/.test(t)) return stop("사적 사진·영상 유포 위협이 포함된 안전 위험 상황이에요.","일반 연애 답장보다 증거 보존과 안전한 거리두기를 우선하세요. 추가 사진·개인정보를 보내지 말고 상대를 자극하는 문장을 피하세요.");
  if(/(?:주민등록번호|계좌\\s*비밀번호|집\\s*비밀번호|실시간\\s*위치|신분증|사적인\\s*사진).{0,30}(?:요구|보내|알려|달라)|(?:요구|보내|알려|달라).{0,30}(?:주민등록번호|계좌\\s*비밀번호|집\\s*비밀번호|실시간\\s*위치|신분증|사적인\\s*사진)/.test(t)) return stop("과도한 개인정보 요구가 포함된 상황이에요.","선톡을 만들기보다 개인정보 제공을 거절하는 것이 우선이에요. 주민등록번호·비밀번호·실시간 위치·사적 사진은 보내지 마세요.");
  if(/(?:미성년|중학생|고등학생|만\\s*1[0-7]세).{0,60}(?:성적|성관계|야한|노출|호텔|사진\\s*보내)|(?:성적|성관계|야한|노출).{0,60}(?:미성년|중학생|고등학생|만\\s*1[0-7]세)/.test(t)) return stop("미성년자와 관련된 성적 상황이에요.","성적 만남·사진·압박 문장을 만들지 않습니다. 일반적이고 존중하는 대화와 안전한 경계만 유지하세요.");
  if(/(?:상사|직장\\s*상급자|교수|지도교수|권력관계).{0,50}(?:강요|압박|불이익|협박)/.test(t)) return stop("권력관계에서의 강압 가능성이 있는 상황이에요.","관계 기술보다 경계와 안전이 우선이에요. 불이익을 피하기 위한 사적·성적 요구에 응하도록 돕는 문장은 만들지 않습니다.");
''' + anchor
assert anchor in s, 'starter money guard anchor missing'
s=s.replace(anchor,insert,1)

# 2) Detail/coach output follows manual structure more explicitly: confidence + do-not-send.
old='''[[meaning]]
핵심 의미와 맥락 2문장 이내, 약 220자 이내
[[emotion]]'''
new='''[[meaning]]
핵심 의미와 맥락 2문장 이내, 약 220자 이내
[[confidence]]
높음 / 중간 / 낮음 중 하나만 출력. 범위 표현이나 퍼센트 금지
[[emotion]]'''
assert old in s, 'detail meaning/emotion protocol anchor missing'
s=s.replace(old,new,1)

old='''[[caution]]
피하면 좋은 행동 2문장 이내, 약 140자 이내
[[reply1]]'''
new='''[[caution]]
피하면 좋은 행동 2문장 이내, 약 140자 이내
[[dontSend]]
지금 보내지 말아야 할 문장이나 행동을 1문장으로 구체적으로 제시. 입력에 없는 사실을 예시로 만들지 말 것
[[reply1]]'''
assert old in s, 'detail caution/reply protocol anchor missing'
s=s.replace(old,new,1)

# Parse and SSE the new sections, but keep them non-fatal to avoid extra paid retries.
old='''const order=isDetail?["meaning","emotion","flow","strategy","caution","reply1","reply2","reply3","advice","nextAction"]:["meaning","emotion","caution","reply1","reply2","reply3","advice","nextAction"];'''
new='''const order=isDetail?["meaning","confidence","emotion","flow","strategy","caution","dontSend","reply1","reply2","reply3","advice","nextAction"]:["meaning","emotion","caution","reply1","reply2","reply3","advice","nextAction"];'''
assert old in s, 'parse order anchor missing'
s=s.replace(old,new,1)

old='''    const order=isDetail?["meaning","emotion","flow","strategy","caution","reply1","reply2","reply3","advice","nextAction"]:["meaning","emotion","caution","reply1","reply2","reply3","advice","nextAction"];'''
new='''    const order=isDetail?["meaning","confidence","emotion","flow","strategy","caution","dontSend","reply1","reply2","reply3","advice","nextAction"]:["meaning","emotion","caution","reply1","reply2","reply3","advice","nextAction"];'''
assert old in s, 'SSE order anchor missing'
s=s.replace(old,new,1)

# Fill conservative coach fallbacks without triggering another model call solely for these display fields.
old='''  parsed=applyAnalysisPolicyGuards(parsed,reqBody||{},isDetail);
  return {parsed,isDetail};'''
new='''  parsed=applyAnalysisPolicyGuards(parsed,reqBody||{},isDetail);
  if(isDetail){
    if(!/^(높음|중간|낮음)$/.test(String(parsed.confidence||"").trim())) parsed.confidence="낮음";
    if(!String(parsed.dontSend||"").trim()) parsed.dontSend=String(parsed.caution||"추가 압박이나 입력에 없는 사실을 만들어 보내지 마세요.");
  }
  return {parsed,isDetail};'''
assert old in s, 'analysis policy return anchor missing'
s=s.replace(old,new,1)

# Make deterministic rejection populate the new coach field too.
old='''    out.caution="거절을 설득으로 뒤집으려 하거나 좋은 인연으로 남자고 제안하거나 미래 재회를 암시하지 마세요.";
    out.advice='''
new='''    out.caution="거절을 설득으로 뒤집으려 하거나 좋은 인연으로 남자고 제안하거나 미래 재회를 암시하지 마세요.";
    out.dontSend="아직 저를 잘 모르셔서 그래요, 한 번만 더 만나봐요처럼 거절을 번복시키려는 문장은 보내지 마세요.";
    out.confidence="높음";
    out.advice='''
assert old in s, 'rejection caution anchor missing'
s=s.replace(old,new,1)

assert '2026-08-23-potentia-v29-coach-safety' in s
assert '[[confidence]]' in s and '[[dontSend]]' in s
assert '미성년자와 관련된 성적 상황' in s
p.write_text(s,encoding='utf-8')
print('Potentia v29 coach+safety patch applied')
