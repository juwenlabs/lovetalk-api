from pathlib import Path
import re

p=Path('server.js')
s=p.read_text(encoding='utf-8')

assert '2026-08-23-potentia-v27-unified-guards' in s, 'expected v27 server not found'
s=s.replace('const SERVER_VERSION = "2026-08-23-potentia-v27-unified-guards";', 'const SERVER_VERSION = "2026-08-23-potentia-v28-truthful-messages";', 1)

# Explicit rejection: never invent the user's positive feelings merely to make a polite close.
anchor='''  const nonUrgent=/(?:비긴급|급하지\\s*않|일반적인)/.test(compact) || situation.includes("읽씹");'''
insert='''  const nonUrgent=/(?:비긴급|급하지\\s*않|일반적인)/.test(compact) || situation.includes("읽씹");
  const explicitRomanticRejection=/(?:이성적으로[^.\\n]{0,20}(?:아니|아닌)|마음이\\s*없|더\\s*만나[^.\\n]{0,20}(?:않|안)|만나고\\s*싶지)/.test(compact);
  if(explicitRomanticRejection){
    out.replies=[
      {label:"깔끔하게 수용",text:"알겠습니다. 솔직하게 말씀해주셔서 감사합니다.",reason:"상대의 명확한 거절을 존중하면서 사용자가 말하지 않은 감정을 새로 만들지 않는 종료 문장입니다."},
      {label:"짧고 정중하게",text:"그렇군요. 말씀해주셔서 감사해요.",reason:"추가 설득이나 관계를 다시 열어두는 표현 없이 정중하게 마무리합니다."},
      {label:"가장 간결하게",text:"알겠습니다. 고마워요.",reason:"거절을 그대로 받아들이고 대화를 늘리지 않는 가장 짧은 형태입니다."}
    ];
    out.caution="거절을 설득으로 뒤집으려 하거나 좋은 인연으로 남자고 제안하거나 미래 재회를 암시하지 마세요.";
    out.advice="명확한 이성적 거절은 짧게 수용하고 추가 설득이나 재접근 없이 마무리하는 것이 맞습니다.";
    out.nextAction="위 문장 중 하나를 한 번 보내고 더 이상 연락하지 마세요. 상대가 명확히 거절한 의사를 그대로 존중합니다.";
  }'''
assert anchor in s, 'analysis guard anchor missing'
s=s.replace(anchor,insert,1)

starter_code=r'''
function applyStarterPolicyGuards(parsed,reqBody){
  const out=(parsed&&typeof parsed==="object")?parsed:{replies:[]};
  const relation=String(reqBody?.relation||"");
  const context=String(reqBody?.message||"");
  const compact=context.replace(/\s+/g," ");
  const initialNumberExchange=/(?:번호\s*교환|연락처\s*교환)/.test(relation+" "+compact);
  const eventArrivalContext=/행사/.test(compact) && /(?:집|도착|들어가)/.test(compact);
  const userActuallyStatedFeeling=/(?:좋았|반가웠|즐거웠|기대된|생각났)/.test(compact);
  if(initialNumberExchange && eventArrivalContext && !userActuallyStatedFeeling){
    out.replies=[
      {label:"자연스럽게",text:"오늘 행사 끝나고 잘 들어가셨나요?",reason:"입력에 있는 행사와 귀가 맥락만 사용해 자연스럽게 안부를 여는 문장입니다."},
      {label:"다정하게",text:"집에는 잘 도착하셨어요?",reason:"상대의 현재 감정이나 상태를 추측하지 않고 확인 가능한 안부만 묻습니다."},
      {label:"부담 최소화",text:"오늘 행사 마무리는 잘하셨어요?",reason:"사용자가 느꼈다고 말하지 않은 호감·기대·감정을 만들어내지 않는 낮은 압력 질문입니다."}
    ];
  }
  return out;
}

async function generateStarterResult(reqBody){
  const {relation,nickname,message,tone,starterGoal,profile,recentMemory,selectedSituation,advanced=false}=reqBody||{};
  const context=typeof message==="string"?message.trim():"";
  const guard=getStarterGuard({message:context,starterGoal,selectedSituation});
  if(guard) return {guard,result:null,advanced:!!advanced};
  const normalizedStarterGoal=/밀당|일부러.{0,10}(늦|기다)|답장 텀/.test(String(starterGoal||"")+" "+context) ? "조작 없이 자연스럽게 연락하기" : starterGoal;
  const prompt=`
사용자가 지금 그 사람에게 먼저 보낼 카카오톡/DM 첫 메시지 3개를 만들어주세요. 이 작업은 답장 추천이 아닙니다.
[그 사람] ${nickname||"새로운/임의 상대"}
[현재 관계] ${relation||"애매한 관계"}
[오늘의 목표] ${normalizedStarterGoal||"부담 없이 먼저 연락하기"}
[원하는 말투] ${tone||"자연스럽게"}
[최근 상황 - 과거 배경정보] ${context||"입력 없음"}
[선택한 상황] ${selectedSituation||"없음"}
[저장된 프로필] ${profile?JSON.stringify(profile):"없음"}
[최근 관계 기억] ${recentMemory||"없음"}
${situationRules(selectedSituation)}
반드시 지킬 규칙:
- 사용자가 지금 먼저 보내는 말만 작성하세요.
- 최근 상황은 상대가 방금 보낸 메시지가 아닙니다.
- '응','웅','나도','그래'처럼 답장처럼 시작하지 마세요.
- 정보가 부족해도 질문하지 말고 바로 3개를 작성하세요.
- 관계 단계보다 앞서는 연락, 재촉, 추가 설득, 우회 연락은 만들지 마세요.
- 존댓말과 반말을 한 문장 안에서 섞지 마세요.
- 사용자가 직접 말하지 않은 자신의 감정(좋았어요·반가웠어요·기대돼요·생각났어요)이나 상대의 현재 상태(쉬고 있다·피곤하다·바쁠 것이다)를 사실처럼 만들어내지 마세요.
- 번호 교환 직후·소개팅·앱 매칭 등 초기 낯선 관계에서 반말 합의가 없다면 존댓말을 기본으로 하세요.
- 실제 카톡에서 바로 보낼 수 있는 짧고 자연스러운 문장만 작성하세요.
${advanced ? `- 이것은 PRO 고급 먼저 보내기 추천입니다.
- 저장된 프로필, 최근 관계 기억, 선택한 상황, 오늘의 목표를 함께 고려해 일반 추천보다 더 정교하게 설계하세요.
- 세 문장은 각각 가장 자연스러운 접근, 관계 진전형, 부담 최소화형처럼 역할이 겹치지 않게 만드세요.
- 각 reason에는 왜 지금 이 문장이 적합한지 1~2문장으로 구체적으로 설명하세요.` : ""}
JSON만 출력하세요.
{"replies":[{"label":"자연스럽게","text":"먼저 보낼 메시지","reason":"이유 1문장"},{"label":"다정하게","text":"먼저 보낼 메시지","reason":"이유 1문장"},{"label":"센스 있게","text":"먼저 보낼 메시지","reason":"이유 1문장"}]}
`;
  let parsed=await createJsonWithRetry({model:"claude-haiku-4-5",maxTokens:advanced?420:300,retryMaxTokens:advanced?520:380,content:prompt});
  if(!Array.isArray(parsed.replies)||parsed.replies.length<3) throw new Error("AI가 추천 문장 3개를 반환하지 않았습니다.");
  parsed.replies=parsed.replies.slice(0,3).map((x,i)=>sanitizeReplyObject(x,selectedSituation,["자연스럽게","다정하게","센스 있게"][i]));
  parsed=applyStarterPolicyGuards(parsed,reqBody||{});
  return {guard:null,result:parsed,advanced:!!advanced};
}
'''
marker='app.post("/api/starter", async (req,res)=>{'
assert marker in s, 'starter endpoint marker missing'
s=s.replace(marker,starter_code+'\n'+marker,1)

# Use one shared starter generator for JSON and the actual app SSE path.
pattern=r'app\.post\("/api/starter", async \(req,res\)=>\{.*?\n\}\);\n\nfunction buildAnalysisContent'
replacement='''app.post("/api/starter", async (req,res)=>{
  try{
    const {guard,result,advanced}=await generateStarterResult(req.body||{});
    if(guard) return res.json({...guard,advanced,serverVersion:SERVER_VERSION});
    res.json({...result,advanced,serverVersion:SERVER_VERSION});
  }catch(error){console.error("선톡 API 오류:",error);res.status(500).json({error:"선톡 추천을 생성하지 못했습니다.",detail:error?.message||"알 수 없는 오류",serverVersion:SERVER_VERSION});}
});

function buildAnalysisContent'''
s,n=re.subn(pattern,replacement,s,count=1,flags=re.S)
assert n==1, f'starter JSON endpoint replacement count={n}'

pattern=r'app\.post\("/api/starter-stream",async\(req,res\)=>\{.*?\}\);\n\napp\.listen'
replacement='''app.post("/api/starter-stream",async(req,res)=>{
  try{
    setStreamHeaders(res);
    const {guard,result}=await generateStarterResult(req.body||{});
    if(guard){
      sendSse(res,"guard",guard);
    }else{
      const replies=Array.isArray(result?.replies)?result.replies:[];
      replies.slice(0,3).forEach((value,i)=>sendSse(res,"section",{name:`reply${i+1}`,value}));
    }
    sendSse(res,"done",{serverVersion:SERVER_VERSION});
    if(!res.writableEnded)res.end();
  }catch(error){console.error("선톡 스트리밍 API 오류:",error);if(!res.headersSent)return res.status(500).json({error:"선톡 스트리밍 추천을 생성하지 못했습니다.",detail:error?.message||"알 수 없는 오류",serverVersion:SERVER_VERSION});if(!res.writableEnded){sendSse(res,"error",{message:error?.message||"스트리밍 오류"});res.end();}}
});

app.listen'''
s,n=re.subn(pattern,replacement,s,count=1,flags=re.S)
assert n==1, f'starter SSE endpoint replacement count={n}'

assert '2026-08-23-potentia-v28-truthful-messages' in s
assert 'function applyStarterPolicyGuards' in s
assert 'async function generateStarterResult' in s
assert 'explicitRomanticRejection' in s
p.write_text(s,encoding='utf-8')
print('Potentia v28 truthful messages patch applied')
