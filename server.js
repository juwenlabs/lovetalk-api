require("dotenv").config();
const express = require("express");
const cors = require("cors");
const Anthropic = require("@anthropic-ai/sdk");
const fs = require("fs");
const path = require("path");
let Pool = null;
try { ({ Pool } = require("pg")); } catch (_) {}

const app = express();
const PORT = process.env.PORT || 3000;
const SERVER_VERSION = "2026-08-19-sse-v13-advanced-starter";
const NOTICE_ADMIN_PASSWORD = process.env.NOTICE_ADMIN_PASSWORD || "";
const NOTICE_FILE = path.join(process.cwd(), "notices-data.json");

app.use(cors());
app.use(express.json({ limit: "35mb" }));

const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

let noticePool = null;
if (process.env.DATABASE_URL && Pool) {
  noticePool = new Pool({ connectionString: process.env.DATABASE_URL, ssl: { rejectUnauthorized: false } });
}

async function initNoticeStore() {
  if (!noticePool) return;
  try {
    await noticePool.query(`
      CREATE TABLE IF NOT EXISTS notices (
        id BIGSERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        type TEXT NOT NULL DEFAULT 'notice',
        important BOOLEAN NOT NULL DEFAULT FALSE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      )
    `);
  } catch (e) {
    console.error("공지 DB 초기화 실패, 파일 저장소로 대체:", e.message);
    noticePool = null;
  }
}
initNoticeStore();

function formatNotice(row) {
  const created = row.created_at ? new Date(row.created_at) : new Date();
  return {
    id: String(row.id),
    title: row.title || "",
    content: row.content || "",
    type: row.type || "notice",
    important: !!row.important,
    date: created.toLocaleDateString("ko-KR", { timeZone: "Asia/Seoul" }).replace(/\. /g, ".").replace(/\.$/, ""),
    createdAt: created.toISOString(),
  };
}

function readNoticeFile() {
  try {
    if (!fs.existsSync(NOTICE_FILE)) return [];
    const parsed = JSON.parse(fs.readFileSync(NOTICE_FILE, "utf8"));
    return Array.isArray(parsed) ? parsed : [];
  } catch (_) { return []; }
}
function writeNoticeFile(items) {
  fs.writeFileSync(NOTICE_FILE, JSON.stringify(items, null, 2), "utf8");
}
async function listNotices() {
  if (noticePool) {
    const { rows } = await noticePool.query("SELECT * FROM notices ORDER BY important DESC, created_at DESC, id DESC");
    return rows.map(formatNotice);
  }
  return readNoticeFile().sort((a,b)=>(Number(b.important)-Number(a.important)) || String(b.createdAt||"").localeCompare(String(a.createdAt||"")));
}
async function createNotice({ title, content, type, important }) {
  if (noticePool) {
    const { rows } = await noticePool.query(
      "INSERT INTO notices(title,content,type,important) VALUES($1,$2,$3,$4) RETURNING *",
      [title, content, type, !!important]
    );
    return formatNotice(rows[0]);
  }
  const items = readNoticeFile();
  const now = new Date();
  const item = { id: String(Date.now()), title, content, type, important: !!important, createdAt: now.toISOString(), date: now.toLocaleDateString("ko-KR",{timeZone:"Asia/Seoul"}).replace(/\. /g,".").replace(/\.$/,"") };
  items.unshift(item); writeNoticeFile(items); return item;
}
async function deleteNotice(id) {
  if (noticePool) {
    const r = await noticePool.query("DELETE FROM notices WHERE id=$1", [id]);
    return r.rowCount > 0;
  }
  const items = readNoticeFile();
  const next = items.filter(x=>String(x.id)!==String(id));
  writeNoticeFile(next); return next.length !== items.length;
}
function requireNoticeAdmin(req,res,next) {
  if (!NOTICE_ADMIN_PASSWORD) return res.status(503).json({ error: "관리자 비밀번호가 서버에 설정되지 않았습니다." });
  const supplied = String(req.body?.password || req.headers["x-admin-password"] || "");
  if (supplied !== NOTICE_ADMIN_PASSWORD) return res.status(401).json({ error: "관리자 비밀번호가 올바르지 않습니다." });
  next();
}

app.get("/", (req, res) => res.json({ ok: true, message: "썸톡 AI 서버가 작동 중입니다.", version: SERVER_VERSION }));
app.get("/api/version", (req,res)=>res.json({ok:true,version:SERVER_VERSION}));
app.get("/api/notices", async (req,res)=>{
  try { res.json({ notices: await listNotices(), serverVersion: SERVER_VERSION }); }
  catch(e){ console.error("공지 조회 오류:",e); res.status(500).json({error:"공지사항을 불러오지 못했습니다."}); }
});
app.post("/api/admin/notices", requireNoticeAdmin, async (req,res)=>{
  try {
    const title=String(req.body?.title||"").trim(); const content=String(req.body?.content||"").trim();
    const type=["notice","update","important"].includes(req.body?.type)?req.body.type:"notice";
    const important=!!req.body?.important || type==="important";
    if(!title||!content) return res.status(400).json({error:"제목과 내용을 입력해주세요."});
    res.json({ok:true,notice:await createNotice({title,content,type,important})});
  } catch(e){console.error("공지 등록 오류:",e);res.status(500).json({error:"공지를 등록하지 못했습니다."});}
});
app.delete("/api/admin/notices/:id", requireNoticeAdmin, async (req,res)=>{
  try { const ok=await deleteNotice(req.params.id); if(!ok)return res.status(404).json({error:"공지를 찾지 못했습니다."}); res.json({ok:true}); }
  catch(e){console.error("공지 삭제 오류:",e);res.status(500).json({error:"공지를 삭제하지 못했습니다."});}
});

function getClaudeText(ai) { return ai.content.filter(item=>item.type==="text").map(item=>item.text).join("\n").trim(); }
function parseClaudeJson(ai) {
  const text=getClaudeText(ai); const cleaned=text.replace(/^```json\s*/i,"").replace(/^```\s*/i,"").replace(/```$/i,"").trim();
  const first=cleaned.indexOf("{"); const last=cleaned.lastIndexOf("}");
  return JSON.parse(first>=0&&last>first?cleaned.slice(first,last+1):cleaned);
}
async function createJsonWithRetry({model,maxTokens,content,retryMaxTokens}){
  let ai=await anthropic.messages.create({model,max_tokens:maxTokens,messages:[{role:"user",content}]});
  try{return parseClaudeJson(ai);}catch(firstError){
    const retryContent=Array.isArray(content)?[...content,{type:"text",text:"\n중요: 반드시 완전하고 유효한 JSON 하나만 출력하세요. 코드블록과 설명은 금지합니다."}]:String(content)+"\n\n반드시 완전하고 유효한 JSON 하나만 출력하세요.";
    ai=await anthropic.messages.create({model,max_tokens:retryMaxTokens||maxTokens,messages:[{role:"user",content:retryContent}]});
    return parseClaudeJson(ai);
  }
}

function situationRules(selectedSituation="") {
  const s=String(selectedSituation||"").trim();
  const base=`
[상황별 답장 안전 규칙]
- 실제 사람이 바로 보낼 수 있는 자연스러운 카톡 문장만 작성하세요.
- 지나치게 감성적·드라마틱·오글거리는 표현, 비꼼, 밀당, 죄책감 유도, 상대 시험하기는 금지합니다.
- 사용자가 제공하지 않은 사건·감정·사실을 지어내지 마세요.
`;
  const map={
    "싸웠어":`- 싸움 자체에 감사하는 표현(예: '싸워줘서 고마워', '화내줘서 고마워', '상처 줘서 고마워')은 절대 금지합니다.
- 갈등 직후에는 감정 진정 → 상황 인정 → 필요한 경우 짧은 사과 → 차분하게 다시 대화할 여지 순서로 접근하세요.
- 잘못이 명확하지 않으면 무조건적인 사과나 자기비하를 만들지 마세요.`,
    "사과하고 싶어":`- 사과는 구체적이고 짧게 하되 과도한 자기비하, 매달림, 용서 강요를 금지합니다.
- '미안해' 뒤에 변명부터 붙이지 말고 상대가 답할 여지를 남기세요.`,
    "내가 너무 많이 연락한 것 같아":`- 연속 연락을 더 권하지 마세요.
- 필요하면 짧은 한 문장만 보내고 이후 시간을 두도록 안내하세요.
- '내가 너무 부담스럽지?', '싫어진 거야?' 같은 불안 확인 질문은 금지합니다.`,
    "다시 연락해도 될지 모르겠어":`- 부담 없는 한 번의 연락만 제안하고 답장 압박을 주지 마세요.
- 관계를 바로 정의하거나 감정을 확인받으려는 문장은 피하세요.`,
    "읽씹 당했어":`- 읽씹을 추궁하거나 '왜 읽고 답 안 해?' 같은 공격적 표현은 금지합니다.
- 같은 내용을 반복해서 보내지 말고 상황에 따라 기다리는 선택도 제안하세요.`,
    "답장이 짧아졌어":`- 답장 길이만으로 마음이 식었다고 단정하지 마세요.
- '나한테 마음 없어?' 같은 확인 요구보다 가볍고 짧은 답장을 우선하세요.`,
    "답장이 늦어졌어":`- 답장 속도만으로 관심 하락을 단정하지 마세요.
- 재촉·추궁·연속 메시지를 권하지 마세요.`,
    "갑자기 차가워졌어":`- 원인을 단정하거나 따져 묻지 마세요.
- 낮은 압력의 짧은 메시지 또는 잠시 기다리는 선택을 제안하세요.`,
    "연락을 기다리는 중이야":`- 불안해서 반복 연락하는 행동을 권하지 마세요.
- 마지막 연락 시점에 따라 기다릴 시간을 구체적으로 제안하세요.`,
    "썸인지 헷갈려":`- 상대 마음을 확정하지 마세요.
- 고백을 급하게 권하기보다 작은 약속·가벼운 호감 표현처럼 확인 가능한 다음 행동을 제안하세요.`,
    "약속 잡고 싶어":`- 날짜/시간을 너무 압박하지 말고 구체적인 제안 + 상대가 편하게 조정할 여지를 주세요.`
  };
  return base+(map[s]?"\n"+map[s]:"");
}

function safeFallbackReply(situation,label){
  const s=String(situation||"");
  if(s.includes("싸")) return {label,text:"아까는 우리 둘 다 감정이 올라온 것 같아. 조금 진정하고 차분하게 얘기하고 싶어.",reason:"갈등을 키우지 않고 대화를 다시 열어두는 표현이에요."};
  if(s.includes("사과")) return {label,text:"아까 내가 말한 방식은 미안해. 변명하지 않고 제대로 얘기하고 싶어.",reason:"과하게 매달리지 않으면서 책임질 부분만 짚는 표현이에요."};
  if(s.includes("읽씹")||s.includes("기다")) return {label,text:"바쁠 수도 있으니까 일단 조금 기다려볼게.",reason:"재촉하지 않고 여유를 주는 표현이에요."};
  return {label,text:"부담 주려는 건 아니고, 편할 때 얘기해줘.",reason:"상대에게 답할 여지를 남기는 자연스러운 표현이에요."};
}
function sanitizeReplyObject(obj,situation,label){
  const out=(obj&&typeof obj==="object")?obj:{label,text:String(obj||""),reason:""};
  const text=String(out.text||"").trim();
  const banned=["싸워줘서 고마워","화내줘서 고마워","상처 줘서 고마워","읽씹해줘서 고마워"];
  if(!text || banned.some(x=>text.includes(x))) return safeFallbackReply(situation,out.label||label||"추천");
  return {label:out.label||label||"추천",text,reason:String(out.reason||"").trim()};
}

function buildCommonPrompt({relation,nickname,message,tone,profile,recentMemory,selectedSituation,hasImages,hasSingleImage}){
  const hasText=typeof message==="string"&&message.trim(); const hasSituation=typeof selectedSituation==="string"&&selectedSituation.trim();
  return `
당신은 연애 상황을 차분하고 현실적으로 분석하는 AI 코치입니다.

중요 원칙:
- 그 사람의 속마음을 사실처럼 단정하지 말고 가능성으로 표현하세요.
- 확인되는 사실과 추정/가능성을 구분하세요.
- 실제 카카오톡/문자/DM에서 자연스럽게 쓸 수 있는 짧은 한국어 답장을 작성하세요.
- 스크린샷이 있으면 대화 순서와 앞뒤 맥락을 반영하세요.
- 답장뿐 아니라 지금 연락할지 기다릴지 같은 다음 행동도 현실적으로 안내하세요.
- 상대를 조종하거나 불안을 키우는 밀당을 권하지 마세요.
${situationRules(selectedSituation)}

[현재 관계] ${relation||"미입력"}
[그 사람 이름/별명] ${nickname||"미입력"}
[사용자가 선택한 현재 상황] ${hasSituation?selectedSituation.trim():"선택 없음"}
[그 사람이 실제로 보낸 대화/사용자 설명] ${hasText?message.trim():((hasImages||hasSingleImage)?"첨부된 스크린샷을 분석":"직접 입력 없음 - 선택한 상황을 중심으로 판단")}
[원하는 답장 분위기] ${tone||"자연스럽게"}
[그 사람 프로필] ${profile?JSON.stringify(profile):"없음"}
[최근 기억] ${recentMemory||"없음"}
`;
}

app.post("/api/starter", async (req,res)=>{
  try{
    const {relation,nickname,message,tone,starterGoal,profile,recentMemory,selectedSituation,advanced=false}=req.body||{};
    const context=typeof message==="string"?message.trim():"";
    const prompt=`
사용자가 지금 그 사람에게 먼저 보낼 카카오톡/DM 첫 메시지 3개를 만들어주세요. 이 작업은 답장 추천이 아닙니다.
[그 사람] ${nickname||"새로운/임의 상대"}
[현재 관계] ${relation||"애매한 관계"}
[오늘의 목표] ${starterGoal||"부담 없이 먼저 연락하기"}
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
- 실제 카톡에서 바로 보낼 수 있는 짧고 자연스러운 문장만 작성하세요.
${advanced ? `- 이것은 PRO 고급 먼저 보내기 추천입니다.
- 저장된 프로필, 최근 관계 기억, 선택한 상황, 오늘의 목표를 함께 고려해 일반 추천보다 더 정교하게 설계하세요.
- 세 문장은 각각 '가장 자연스러운 접근', '관계 진전형', '부담 최소화형'처럼 목적이 겹치지 않게 만드세요.
- 각 추천의 reason에는 왜 지금 이 문장이 적합한지 1~2문장으로 구체적으로 설명하세요.` : ""}
JSON만 출력하세요.
{"replies":[{"label":"자연스럽게","text":"먼저 보낼 메시지","reason":"이유 1문장"},{"label":"다정하게","text":"먼저 보낼 메시지","reason":"이유 1문장"},{"label":"센스 있게","text":"먼저 보낼 메시지","reason":"이유 1문장"}]}
`;
    const parsed=await createJsonWithRetry({model:"claude-haiku-4-5",maxTokens:advanced?420:300,retryMaxTokens:advanced?520:380,content:prompt});
    if(!Array.isArray(parsed.replies)||parsed.replies.length<3) throw new Error("AI가 추천 문장 3개를 반환하지 않았습니다.");
    parsed.replies=parsed.replies.slice(0,3).map((x,i)=>sanitizeReplyObject(x,selectedSituation,["자연스럽게","다정하게","센스 있게"][i]));
    res.json({...parsed,advanced:!!advanced,serverVersion:SERVER_VERSION});
  }catch(error){console.error("선톡 API 오류:",error);res.status(500).json({error:"선톡 추천을 생성하지 못했습니다.",detail:error?.message||"알 수 없는 오류",serverVersion:SERVER_VERSION});}
});

function buildAnalysisContent(reqBody){
  const {relation,nickname,message,tone,image,images,mode="quick",profile,recentMemory,selectedSituation}=reqBody||{};
  const hasText=typeof message==="string"&&message.trim(); const hasSingleImage=!!image?.data; const hasImages=Array.isArray(images)&&images.some(img=>img?.data); const hasSituation=typeof selectedSituation==="string"&&selectedSituation.trim(); const isDetail=mode==="detail";
  if(!hasText&&!hasSingleImage&&!hasImages&&!hasSituation){const err=new Error("메시지나 스크린샷을 올리거나 상황을 선택해주세요.");err.statusCode=400;throw err;}
  const commonPrompt=buildCommonPrompt({relation,nickname,message,tone,profile,recentMemory,selectedSituation,hasImages,hasSingleImage});
  const protocol=isDetail?`
${commonPrompt}
아래 표식을 정확히 같은 순서로 출력하세요. 코드블록/설명/머리말 금지. reply는 한 줄 유효 JSON 객체.
[[meaning]]
핵심 의미와 맥락 2~4문장
[[emotion]]
감정·거리감·관심도의 가능성 2~4문장
[[flow]]
대화 흐름과 태도 변화 2~4문장
[[strategy]]
답장 목표와 톤 2~4문장
[[caution]]
피하면 좋은 행동 2~3문장
[[reply1]]
{"label":"가장 자연스러운 답장","text":"답장","reason":"이유"}
[[reply2]]
{"label":"조금 더 다정한 답장","text":"답장","reason":"이유"}
[[reply3]]
{"label":"조금 더 여유 있는 답장","text":"답장","reason":"이유"}
[[advice]]
한 줄 조언
[[nextAction]]
현재 타이밍 판단 + 다음 연락 시점 + 그때까지 행동 방법 3~5문장
[[done]]
`:`
${commonPrompt}
아래 표식을 정확히 같은 순서로 출력하세요. 코드블록/설명/머리말 금지. reply는 한 줄 유효 JSON 객체.
[[meaning]]
핵심 의미 1문장
[[emotion]]
감정/태도 가능성 1문장
[[caution]]
피하면 좋은 행동 1문장
[[reply1]]
{"label":"가장 자연스러운 답장","text":"짧은 답장","reason":"이유 1문장"}
[[reply2]]
{"label":"조금 더 다정한 답장","text":"짧은 답장","reason":"이유 1문장"}
[[reply3]]
{"label":"조금 더 여유 있는 답장","text":"짧은 답장","reason":"이유 1문장"}
[[advice]]
한 줄 조언
[[nextAction]]
지금 연락할지 기다릴지와 바로 할 행동을 1~2문장으로 구체적으로 안내
[[done]]
`;
  const content=[]; const allowed=["image/jpeg","image/png","image/webp"]; const imageList=Array.isArray(images)&&images.length?images.slice(0,15):(image?.data?[image]:[]);
  for(const img of imageList){if(!img?.data)continue;const mediaType=allowed.includes(img.mediaType)?img.mediaType:"image/jpeg";content.push({type:"image",source:{type:"base64",media_type:mediaType,data:img.data}});}
  content.push({type:"text",text:protocol}); return {content,isDetail,selectedSituation};
}

app.post("/api/love-analysis", async (req,res)=>{
  try{
    const {content,isDetail,selectedSituation}=buildAnalysisContent(req.body||{});
    const parsed=await createJsonWithRetry({model:isDetail?"claude-sonnet-5":"claude-haiku-4-5",maxTokens:isDetail?1700:750,retryMaxTokens:isDetail?1900:900,content});
    if(Array.isArray(parsed.replies)) parsed.replies=parsed.replies.slice(0,3).map((x,i)=>sanitizeReplyObject(x,selectedSituation,["가장 자연스러운 답장","조금 더 다정한 답장","조금 더 여유 있는 답장"][i]));
    res.json({...parsed,serverVersion:SERVER_VERSION});
  }catch(error){console.error("Claude API 오류:",error);res.status(error?.statusCode||500).json({error:"AI 분석을 생성하지 못했습니다.",detail:error?.message||"알 수 없는 오류",serverVersion:SERVER_VERSION});}
});

function setStreamHeaders(res){res.status(200);res.setHeader("Content-Type","text/event-stream; charset=utf-8");res.setHeader("Cache-Control","no-cache, no-transform");res.setHeader("Connection","keep-alive");res.setHeader("X-Accel-Buffering","no");if(res.socket&&typeof res.socket.setNoDelay==="function")res.socket.setNoDelay(true);if(typeof res.flushHeaders==="function")res.flushHeaders();res.write(": connected "+" ".repeat(2048)+"\n\n");}
function sendSse(res,event,data){if(res.writableEnded)return;res.write(`event: ${event}\n`);res.write(`data: ${JSON.stringify(data)}\n\n`);res.write(":"+" ".repeat(2048)+"\n\n");if(typeof res.flush==="function")res.flush();}
function parseReplyObject(raw,fallbackLabel){const text=String(raw||"").trim();try{const first=text.indexOf("{");const last=text.lastIndexOf("}");if(first>=0&&last>first)return JSON.parse(text.slice(first,last+1));}catch(_){}const m=text.match(/"text"\s*:\s*"((?:\\.|[^"\\])*)/s);let recovered=m?m[1]:text;recovered=recovered.replace(/\\n/g,"\n").replace(/\\"/g,'"').replace(/\\\\/g,"\\").trim();if(recovered.startsWith("{"))recovered="추천 문장을 생성했지만 마지막 부분이 잘렸어요. 다시 시도해주세요.";return{label:fallbackLabel||"추천",text:recovered,reason:""};}
async function streamClaudeSections({res,model,maxTokens,content,sectionOrder,selectedSituation}){
  let fullText="";const emitted=new Set();let finished=false;
  function tryEmit(){for(let i=0;i<sectionOrder.length;i++){const name=sectionOrder[i];if(emitted.has(name))continue;const marker=`[[${name}]]`;const next=sectionOrder[i+1]||"done";const nextMarker=`[[${next}]]`;const start=fullText.indexOf(marker);let end=fullText.indexOf(nextMarker);if(start<0)continue;if(end<0&&finished&&i===sectionOrder.length-1)end=fullText.length;if(end<0||end<=start)continue;const raw=fullText.slice(start+marker.length,end).trim();if(!raw)continue;let value=raw;if(name.startsWith("reply")){const n=Number(name.replace("reply",""))||1;const labels=["가장 자연스러운 답장","조금 더 다정한 답장","조금 더 여유 있는 답장"];value=sanitizeReplyObject(parseReplyObject(raw,labels[n-1]||"추천"),selectedSituation,labels[n-1]);}sendSse(res,"section",{name,value});emitted.add(name);}}
  const stream=anthropic.messages.stream({model,max_tokens:maxTokens,messages:[{role:"user",content}]});stream.on("text",t=>{fullText+=t;tryEmit();});await stream.finalMessage();finished=true;tryEmit();sendSse(res,"done",{serverVersion:SERVER_VERSION});if(!res.writableEnded)res.end();
}

app.post("/api/love-analysis-stream",async(req,res)=>{try{const {content,isDetail,selectedSituation}=buildAnalysisContent(req.body||{});setStreamHeaders(res);await streamClaudeSections({res,model:isDetail?"claude-sonnet-5":"claude-haiku-4-5",maxTokens:isDetail?1700:750,content,selectedSituation,sectionOrder:isDetail?["meaning","emotion","flow","strategy","caution","reply1","reply2","reply3","advice","nextAction"]:["meaning","emotion","caution","reply1","reply2","reply3","advice","nextAction"]});}catch(error){console.error("스트리밍 분석 API 오류:",error);if(!res.headersSent)return res.status(error?.statusCode||500).json({error:"스트리밍 분석을 생성하지 못했습니다.",detail:error?.message||"알 수 없는 오류",serverVersion:SERVER_VERSION});if(!res.writableEnded){sendSse(res,"error",{message:error?.message||"스트리밍 오류"});res.end();}}});

app.post("/api/starter-stream",async(req,res)=>{try{const {relation,nickname,message,tone,starterGoal,profile,recentMemory,selectedSituation,advanced=false}=req.body||{};const context=typeof message==="string"?message.trim():"";const prompt=`
사용자가 지금 그 사람에게 먼저 보낼 카카오톡/DM 첫 메시지 3개를 만드세요. 답장 추천이 아니라 선톡입니다.
최근 상황은 과거 배경정보이며 그 사람이 방금 보낸 메시지가 아닙니다. '응','웅','나도','그래'처럼 답장처럼 시작하지 마세요. 정보가 부족해도 추가 질문 없이 바로 추천하세요.
[그 사람] ${nickname||"새로운/임의 상대"}
[현재 관계] ${relation||"애매한 관계"}
[오늘의 목표] ${starterGoal||"부담 없이 먼저 연락하기"}
[원하는 말투] ${tone||"자연스럽게"}
[최근 상황] ${context||"입력 없음"}
[선택한 상황] ${selectedSituation||"없음"}
[저장된 프로필] ${profile?JSON.stringify(profile):"없음"}
[최근 관계 기억] ${recentMemory||"없음"}
${situationRules(selectedSituation)}
${advanced ? `이것은 PRO 고급 먼저 보내기 추천입니다.
저장된 프로필, 최근 관계 기억, 선택한 상황, 오늘의 목표를 함께 고려해 일반 추천보다 더 정교하게 설계하세요.
세 문장은 각각 가장 자연스러운 접근, 관계 진전형, 부담 최소화형처럼 목적이 겹치지 않게 만드세요.
각 reason에는 왜 지금 이 문장이 적합한지 구체적으로 설명하세요.` : ""}
아래 표식을 정확히 같은 순서로 출력하세요. 각 reply는 유효한 한 줄 JSON 객체.
[[reply1]]
{"label":"자연스럽게","text":"먼저 보낼 메시지","reason":"이유 1문장"}
[[reply2]]
{"label":"다정하게","text":"먼저 보낼 메시지","reason":"이유 1문장"}
[[reply3]]
{"label":"센스 있게","text":"먼저 보낼 메시지","reason":"이유 1문장"}
[[done]]
`;setStreamHeaders(res);await streamClaudeSections({res,model:"claude-haiku-4-5",maxTokens:advanced?720:560,content:prompt,selectedSituation,sectionOrder:["reply1","reply2","reply3"]});}catch(error){console.error("선톡 스트리밍 API 오류:",error);if(!res.headersSent)return res.status(500).json({error:"선톡 스트리밍 추천을 생성하지 못했습니다.",detail:error?.message||"알 수 없는 오류",serverVersion:SERVER_VERSION});if(!res.writableEnded){sendSse(res,"error",{message:error?.message||"스트리밍 오류"});res.end();}}});

app.listen(PORT,()=>console.log(`썸톡 AI 서버 실행 중: ${PORT} / ${SERVER_VERSION}`));
