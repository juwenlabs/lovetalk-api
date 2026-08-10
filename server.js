require("dotenv").config();
const express = require("express");
const cors = require("cors");
const Anthropic = require("@anthropic-ai/sdk");

const app = express();
const PORT = process.env.PORT || 3000;
const SERVER_VERSION = "2026-08-11-situation-action-v4";

app.use(cors());
app.use(express.json({ limit: "35mb" }));

const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

app.get("/", (req, res) => res.json({ ok:true, message:"썸톡 AI 서버가 작동 중입니다.", version:SERVER_VERSION }));
app.get("/api/version", (req, res) => res.json({ ok:true, version:SERVER_VERSION }));

function parseClaudeJson(ai){
  const text=ai.content.filter(x=>x.type==="text").map(x=>x.text).join("\n").trim();
  try{return JSON.parse(text);}catch{ return JSON.parse(text.replace(/^```json\s*/i,"").replace(/```$/i,"").trim()); }
}

app.post("/api/starter", async (req,res)=>{
  try{
    const {relation,nickname,message,tone,starterGoal,profile,recentMemory}=req.body||{};
    const context=typeof message==="string"?message.trim():"";
    const prompt=`사용자가 지금 상대에게 먼저 보낼 카카오톡/DM 첫 메시지 3개를 만들어주세요. 이 작업은 절대로 답장 추천이 아닙니다.\n상대: ${nickname||"새로운/임의 상대"}\n관계: ${relation||"애매한 관계"}\n목표: ${starterGoal||"부담 없이 먼저 연락하기"}\n말투: ${tone||"자연스럽게"}\n최근 상황(과거 배경정보): ${context||"입력 없음"}\n프로필: ${profile?JSON.stringify(profile):"없음"}\n최근 기억: ${recentMemory||"없음"}\n규칙: 사용자가 지금 먼저 보내는 말만 작성. 최근 상황은 상대가 방금 보낸 말이 아님. 어제/지난주/아까/지난번은 끝난 과거 사건. '응','웅','나도','그래'처럼 답장형으로 시작 금지. 최근 상황이 없어도 질문하지 말고 바로 작성. 실제 카톡처럼 짧고 자연스럽게.\nJSON만 출력: {"replies":[{"label":"자연스럽게","text":"먼저 보낼 메시지"},{"label":"다정하게","text":"먼저 보낼 메시지"},{"label":"센스 있게","text":"먼저 보낼 메시지"}]}`;
    const ai=await anthropic.messages.create({model:"claude-haiku-4-5",max_tokens:180,messages:[{role:"user",content:prompt}]});
    const parsed=parseClaudeJson(ai);
    if(!Array.isArray(parsed.replies)||parsed.replies.length<3) throw new Error("AI가 추천 문장 3개를 반환하지 않았습니다.");
    res.json({...parsed,serverVersion:SERVER_VERSION});
  }catch(error){ console.error("선톡 API 오류:",error); res.status(500).json({error:"선톡 추천을 생성하지 못했습니다.",detail:error?.message||"알 수 없는 오류",serverVersion:SERVER_VERSION}); }
});

app.post("/api/love-analysis", async (req,res)=>{
  try{
    const {relation,nickname,message,tone,image,images,mode="quick",profile,recentMemory,quickSituation}=req.body||{};
    const hasText=typeof message==="string"&&message.trim();
    const hasSingleImage=!!image?.data;
    const hasImages=Array.isArray(images)&&images.some(img=>img?.data);
    const hasQuickSituation=typeof quickSituation==="string"&&quickSituation.trim();
    if(!hasText&&!hasSingleImage&&!hasImages&&!hasQuickSituation) return res.status(400).json({error:"메시지나 스크린샷을 입력하거나 상황을 선택해주세요.",serverVersion:SERVER_VERSION});
    const isDetail=mode==="detail";
    const commonPrompt=`당신은 연애 상황을 차분하고 현실적으로 분석하는 AI 코치입니다.\n원칙:\n- 상대 속마음을 사실처럼 단정하지 말고 사실과 추정을 구분.\n- 실제 카톡/문자/DM에서 자연스러운 짧은 한국어 답장 작성.\n- 스크린샷이 있으면 대화 순서와 맥락 반영.\n- 답장뿐 아니라 다음 행동과 연락 타이밍을 구체적으로 제안.\n- 상황에 따라 지금 연락하기, 몇 시간/하루 기다리기, 추가 연락 멈추기 등을 현실적으로 판단.\n- 연락 충동을 참는 편이 낫다면 휴대폰 치우기, 메모장에 먼저 쓰기, 알림 끄기, 다른 활동 정하기처럼 실행 가능한 방법 제안.\n\n관계: ${relation||"미입력"}\n별명: ${nickname||"미입력"}\n사용자가 선택한 현재 상황(참고 맥락): ${hasQuickSituation?quickSituation.trim():"선택 없음"}\n중요: 위 상황 선택은 상대가 보낸 메시지가 아니므로 답장에 그대로 인용하지 말고 판단 근거로만 사용.\n상대가 실제로 보낸 대화/설명: ${hasText?message.trim():(hasSingleImage||hasImages?"첨부 스크린샷 분석":"직접 입력 없음")}\n원하는 분위기: ${tone||"자연스럽게"}\n프로필: ${profile?JSON.stringify(profile):"없음"}\n최근 기억: ${recentMemory||"없음"}`;
    const quickPrompt=`${commonPrompt}\nJSON만 출력: {"meaning":"핵심 의미 1~2문장","emotion":"감정/태도 가능성 1~2문장","caution":"피하면 좋은 행동 1문장","replies":[{"label":"가장 자연스러운 답장","text":"짧은 답장","reason":"이유 1문장"},{"label":"조금 더 다정한 답장","text":"짧은 답장","reason":"이유 1문장"},{"label":"조금 더 여유 있는 답장","text":"짧은 답장","reason":"이유 1문장"}],"nextAction":"지금 연락할지 기다릴지, 기다린다면 대략 얼마나 기다릴지와 그동안 할 행동을 2~4문장으로 구체적으로 안내","advice":"한 줄 조언"}`;
    const detailPrompt=`${commonPrompt}\nJSON만 출력: {"meaning":"핵심 의미와 맥락 2~4문장","emotion":"감정·거리감·관심도 가능성 2~4문장","flow":"대화 흐름과 태도 변화 2~4문장","strategy":"답장 목표와 톤 2~4문장","caution":"피하면 좋은 행동 2~3문장","replies":[{"label":"가장 자연스러운 답장","text":"답장","reason":"이유"},{"label":"조금 더 다정한 답장","text":"답장","reason":"이유"},{"label":"조금 더 여유 있는 답장","text":"답장","reason":"이유"}],"nextAction":"지금 연락할지 기다릴지, 연락 타이밍과 그동안의 행동을 3~5문장으로 구체적으로 안내","advice":"한 줄 조언"}`;
    const content=[]; const allowedTypes=["image/jpeg","image/png","image/webp"];
    const imageList=Array.isArray(images)&&images.length?images.slice(0,5):(image?.data?[image]:[]);
    for(const img of imageList){ if(!img?.data) continue; const mediaType=allowedTypes.includes(img.mediaType)?img.mediaType:"image/jpeg"; content.push({type:"image",source:{type:"base64",media_type:mediaType,data:img.data}}); }
    content.push({type:"text",text:isDetail?detailPrompt:quickPrompt});
    const ai=await anthropic.messages.create({model:"claude-sonnet-5",max_tokens:isDetail?1150:620,messages:[{role:"user",content}]});
    const parsed=parseClaudeJson(ai); res.json({...parsed,serverVersion:SERVER_VERSION});
  }catch(error){ console.error("Claude API 오류:",error); res.status(500).json({error:"AI 분석을 생성하지 못했습니다.",detail:error?.message||"알 수 없는 오류",serverVersion:SERVER_VERSION}); }
});

app.listen(PORT,()=>console.log(`썸톡 AI 서버 실행 중: ${PORT} / ${SERVER_VERSION}`));
