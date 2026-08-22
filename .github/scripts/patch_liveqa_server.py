from pathlib import Path
import re
p=Path('server.js')
s=p.read_text(encoding='utf-8')
s=re.sub(r'const SERVER_VERSION = "[^"]+";', 'const SERVER_VERSION = "2026-08-23-liveqa-v14-parser-guards";', s, count=1)

guard='''
function getAdvancedStarterGuard({message="",starterGoal="",selectedSituation=""}){
  const t=`${message} ${starterGoal} ${selectedSituation}`.toLowerCase().replace(/\\s+/g," ");
  const stop=(reason,advice)=>({doNotSend:true,reason,advice,replies:[]});
  if(/연락하지|연락 중단|더 이상 연락|차단|blocked|다른 계정으로 연락|친구 계정/.test(t)) return stop("상대의 명확한 경계가 확인됐어요.","지금은 새 메시지를 만들지 않는 것이 맞아요. 연락 중단이나 차단은 다른 계정·SNS·지인을 통해 우회하지 마세요.");
  if(/이성적으로.{0,12}아니|마음이 없|만나고 싶지|싫다|좋은 분.{0,20}이성적/.test(t)) return stop("명확한 이성적 거절이 확인됐어요.","추가 설득이나 마지막 기회 요청보다 거절을 존중하고 멈추는 편이 맞아요.");
  if(/(두 번|2번|두번).{0,50}(거절|어렵).{0,80}(대안|다른 날짜).{0,20}(없|않)/.test(t) || /(약속.{0,20}(두 번|2번|두번).{0,50}(거절|어렵))/.test(t)) return stop("약속 제안이 반복해서 거절됐고 대안 참여가 확인되지 않아요.","추가 약속 제안은 멈추고 상대가 먼저 구체적으로 참여할 때까지 기다리는 편이 맞아요.");
  if(/(후속|확인 메시지).{0,60}(무응답|답이 없|답 없음)|다시.{0,20}(이틀|2일).{0,20}(무응답|답이 없)/.test(t)) return stop("이미 한 번 확인한 뒤에도 무응답이 이어지고 있어요.","더 보내지 말고 여기서 멈추는 것이 좋아요.");
  if(/(한|1|두|2)\\s*시간.{0,40}(답이 없|답 없음|무응답|읽었|읽씹)/.test(t)) return stop("아직 추가 연락을 판단하기에는 너무 이른 시간이에요.","불안을 줄이기 위한 재촉 메시지는 보내지 말고 상대가 답할 시간을 주세요.");
  if(/스토리.{0,40}(답이 없|답 없음|무응답|읽씹)|답.{0,20}(없|안).{0,40}스토리/.test(t)) return stop("SNS 활동은 관계 의사를 확정하는 근거가 아니에요.","스토리 조회를 이유로 다시 연락하지 말고, 이미 보낸 메시지에 답할 시간을 주세요.");
  if(/빌려달|송금|대출|보증|급전|금전/.test(t)) return stop("금전 요구가 포함된 상황이에요.","관계를 유지하기 위한 선톡보다 금전 거래를 거절하고 개인정보·송금을 추가로 제공하지 않는 것이 우선이에요. 필요하면 ‘금전 거래는 어렵습니다.’처럼 짧게 경계를 세우세요.");
  return null;
}
'''
if 'function getAdvancedStarterGuard' not in s:
    marker='app.post("/api/starter", async (req,res)=>{'
    assert marker in s
    s=s.replace(marker,guard+'\n'+marker,1)
old='''    const {relation,nickname,message,tone,starterGoal,profile,recentMemory,selectedSituation,advanced=false}=req.body||{};\n    const context=typeof message==="string"?message.trim():"";'''
new='''    const {relation,nickname,message,tone,starterGoal,profile,recentMemory,selectedSituation,advanced=false}=req.body||{};\n    const context=typeof message==="string"?message.trim():"";\n    if(advanced){ const guard=getAdvancedStarterGuard({message:context,starterGoal,selectedSituation}); if(guard) return res.json({...guard,advanced:true,serverVersion:SERVER_VERSION}); }\n    const normalizedStarterGoal=advanced && /밀당|일부러.{0,10}(늦|기다)|답장 텀/.test(String(starterGoal||"")+" "+context) ? "조작 없이 자연스럽게 연락하기" : starterGoal;'''
if old in s: s=s.replace(old,new,1)
s=s.replace('[오늘의 목표] ${starterGoal||"부담 없이 먼저 연락하기"}','[오늘의 목표] ${normalizedStarterGoal||"부담 없이 먼저 연락하기"}',1)
needle='- 정보가 부족해도 질문하지 말고 바로 3개를 작성하세요.'
if '관계 단계보다 앞서는 연락' not in s:
    s=s.replace(needle,needle+'\n- 관계 단계보다 앞서는 연락, 재촉, 추가 설득, 우회 연락은 만들지 마세요.\n- 존댓말과 반말을 한 문장 안에서 섞지 마세요.\n- 약속 제안이 적절한 상황에서는 막연한 “언제 괜찮아?”보다 맥락과 하나의 구체적 시점을 포함한 제안을 우선하세요.',1)
parser='''
function parseAnalysisSectionsText(text,isDetail,selectedSituation){
  const src=String(text||"");
  const order=isDetail?["meaning","emotion","flow","strategy","caution","reply1","reply2","reply3","advice","nextAction"]:["meaning","emotion","caution","reply1","reply2","reply3","advice","nextAction"];
  const out={replies:[]};
  for(let i=0;i<order.length;i++){
    const name=order[i], marker=`[[${name}]]`, nextMarker=`[[${order[i+1]||"done"}]]`;
    const start=src.indexOf(marker); if(start<0) continue;
    let end=src.indexOf(nextMarker,start+marker.length); if(end<0) end=src.length;
    const raw=src.slice(start+marker.length,end).trim(); if(!raw) continue;
    if(name.startsWith("reply")){
      const n=Number(name.replace("reply",""))||1; const labels=["가장 자연스러운 답장","조금 더 다정한 답장","조금 더 여유 있는 답장"];
      out.replies[n-1]=sanitizeReplyObject(parseReplyObject(raw,labels[n-1]),selectedSituation,labels[n-1]);
    } else out[name]=raw;
  }
  out.replies=out.replies.filter(Boolean); return out;
}
function validAnalysisResult(x){ return !!(x && x.meaning && Array.isArray(x.replies) && x.replies.length>=1); }
'''
if 'function parseAnalysisSectionsText' not in s:
    marker='app.post("/api/love-analysis", async (req,res)=>{'
    assert marker in s
    s=s.replace(marker,parser+'\n'+marker,1)
pattern=r'app\.post\("/api/love-analysis", async \(req,res\)=>\{.*?\n\}\);\n\nfunction setStreamHeaders'
replacement='''app.post("/api/love-analysis", async (req,res)=>{
  try{
    const {content,isDetail,selectedSituation}=buildAnalysisContent(req.body||{});
    const model=isDetail?"claude-sonnet-5":"claude-haiku-4-5";
    let ai=await anthropic.messages.create({model,max_tokens:isDetail?1700:750,messages:[{role:"user",content}]});
    let parsed=parseAnalysisSectionsText(getClaudeText(ai),isDetail,selectedSituation);
    if(!validAnalysisResult(parsed)){
      const retryContent=Array.isArray(content)?[...content,{type:"text",text:`중요: 위에서 지정한 [[meaning]], [[emotion]], reply 표식을 정확히 지켜 완전한 결과를 다시 출력하세요. 코드블록과 머리말은 금지합니다.`}]:content;
      ai=await anthropic.messages.create({model,max_tokens:isDetail?1900:900,messages:[{role:"user",content:retryContent}]});
      parsed=parseAnalysisSectionsText(getClaudeText(ai),isDetail,selectedSituation);
    }
    if(!validAnalysisResult(parsed)) throw new Error("AI 분석 섹션을 정상적으로 파싱하지 못했습니다.");
    res.json({...parsed,serverVersion:SERVER_VERSION});
  }catch(error){console.error("Claude API 오류:",error);res.status(error?.statusCode||500).json({error:"AI 분석을 생성하지 못했습니다.",detail:error?.message||"알 수 없는 오류",serverVersion:SERVER_VERSION});}
});

function setStreamHeaders'''
s2,n=re.subn(pattern,replacement,s,count=1,flags=re.S)
assert n==1, f'analysis endpoint patch count={n}'
p.write_text(s2,encoding='utf-8')
