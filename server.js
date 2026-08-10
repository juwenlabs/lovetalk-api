require("dotenv").config();
const express = require("express");
const cors = require("cors");
const Anthropic = require("@anthropic-ai/sdk");

const app = express();
const PORT = process.env.PORT || 3000;
const SERVER_VERSION = "2026-08-11-sse-v10";

app.use(cors());
app.use(express.json({ limit: "35mb" }));

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

app.get("/", (req, res) => {
  res.json({
    ok: true,
    message: "썸톡 AI 서버가 작동 중입니다.",
    version: SERVER_VERSION,
  });
});

app.get("/api/version", (req, res) => {
  res.json({ ok: true, version: SERVER_VERSION });
});

function getClaudeText(ai) {
  return ai.content
    .filter(item => item.type === "text")
    .map(item => item.text)
    .join("\n")
    .trim();
}

function parseClaudeJson(ai) {
  const text = getClaudeText(ai);
  const cleaned = text
    .replace(/^```json\s*/i, "")
    .replace(/^```\s*/i, "")
    .replace(/```$/i, "")
    .trim();

  const firstBrace = cleaned.indexOf("{");
  const lastBrace = cleaned.lastIndexOf("}");
  const candidate =
    firstBrace >= 0 && lastBrace > firstBrace
      ? cleaned.slice(firstBrace, lastBrace + 1)
      : cleaned;

  return JSON.parse(candidate);
}

async function createJsonWithRetry({ model, maxTokens, content, retryMaxTokens }) {
  let ai = await anthropic.messages.create({
    model,
    max_tokens: maxTokens,
    messages: [{ role: "user", content }],
  });

  try {
    return parseClaudeJson(ai);
  } catch (firstError) {
    console.warn("JSON 파싱 실패 - 1회 재생성:", firstError.message);

    const retryContent = Array.isArray(content)
      ? [
          ...content,
          {
            type: "text",
            text:
              "\n중요: 방금 응답 형식이 깨졌습니다. 이번에는 반드시 완전하고 유효한 JSON 하나만 출력하세요. " +
              "모든 문자열의 큰따옴표를 닫고, 마지막 중괄호까지 반드시 출력하세요. 코드블록과 설명은 금지합니다.",
          },
        ]
      : String(content) +
        "\n\n중요: 이번에는 반드시 완전하고 유효한 JSON 하나만 출력하세요. " +
        "모든 문자열의 큰따옴표를 닫고 마지막 중괄호까지 반드시 출력하세요. 코드블록과 설명은 금지합니다.";

    ai = await anthropic.messages.create({
      model,
      max_tokens: retryMaxTokens || maxTokens,
      messages: [{ role: "user", content: retryContent }],
    });

    return parseClaudeJson(ai);
  }
}

app.post("/api/starter", async (req, res) => {
  try {
    const { relation, nickname, message, tone, starterGoal, profile, recentMemory } = req.body || {};
    const context = typeof message === "string" ? message.trim() : "";
    const prompt = `
사용자가 지금 상대에게 먼저 보낼 카카오톡/DM 첫 메시지 3개를 만들어주세요.
이 작업은 절대로 '답장 추천'이 아닙니다.
[상대] ${nickname || "새로운/임의 상대"}
[현재 관계] ${relation || "애매한 관계"}
[오늘의 목표] ${starterGoal || "부담 없이 먼저 연락하기"}
[원하는 말투] ${tone || "자연스럽게"}
[최근 상황 - 과거 배경정보] ${context || "입력 없음"}
[저장된 상대 프로필] ${profile ? JSON.stringify(profile) : "없음"}
[최근 관계 기억] ${recentMemory || "없음"}
사용자가 지금 먼저 보내는 말만 작성하고, 답장처럼 시작하지 마세요.
아래 JSON만 출력하세요.
{"replies":[{"label":"자연스럽게","text":"먼저 보낼 메시지"},{"label":"다정하게","text":"먼저 보낼 메시지"},{"label":"센스 있게","text":"먼저 보낼 메시지"}]}
`;
    const parsed = await createJsonWithRetry({ model:"claude-haiku-4-5", maxTokens:240, retryMaxTokens:320, content:prompt });
    res.json({ ...parsed, serverVersion: SERVER_VERSION });
  } catch (error) {
    res.status(500).json({ error:"선톡 추천을 생성하지 못했습니다.", detail:error?.message || "알 수 없는 오류", serverVersion:SERVER_VERSION });
  }
});

function buildAnalysisContent(reqBody) {
  const { relation, nickname, message, tone, image, images, mode="quick", profile, recentMemory, selectedSituation } = reqBody || {};
  const hasText = typeof message === "string" && message.trim();
  const hasSingleImage = !!image?.data;
  const hasImages = Array.isArray(images) && images.some(img => img?.data);
  const hasSituation = typeof selectedSituation === "string" && selectedSituation.trim();
  const isDetail = mode === "detail";

  if (!hasText && !hasSingleImage && !hasImages && !hasSituation) {
    const err = new Error("메시지나 스크린샷을 올리거나 상황을 선택해주세요.");
    err.statusCode = 400;
    throw err;
  }

  const commonPrompt = `
당신은 연애 상황을 차분하고 현실적으로 분석하는 AI 코치입니다.
상대의 속마음을 사실처럼 단정하지 말고 가능성으로 표현하세요.
실제 카카오톡/문자/DM에서 자연스럽게 쓸 수 있는 짧은 한국어 답장을 작성하세요.
스크린샷이 있으면 대화 순서와 앞뒤 맥락을 반영하세요.
답장뿐 아니라 지금 연락할지, 기다릴지 같은 다음 행동도 현실적으로 안내하세요.
[현재 관계] ${relation || "미입력"}
[상대 별명] ${nickname || "미입력"}
[사용자가 선택한 현재 상황] ${hasSituation ? selectedSituation.trim() : "선택 없음"}
[상대가 실제로 보낸 대화/사용자 설명] ${hasText ? message.trim() : (hasImages || hasSingleImage ? "첨부된 스크린샷을 분석" : "직접 입력 없음 - 선택한 상황을 중심으로 판단")}
[원하는 답장 분위기] ${tone || "자연스럽게"}
[상대 프로필] ${profile ? JSON.stringify(profile) : "없음"}
[최근 기억] ${recentMemory || "없음"}
`;

  const quickProtocol = `
${commonPrompt}
아래 표식을 정확히 같은 순서로 출력하세요. 코드블록/설명/머리말 금지.
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

  const detailProtocol = `
${commonPrompt}
아래 표식을 정확히 같은 순서로 출력하세요. 코드블록/설명/머리말 금지.
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
현재 타이밍 판단 + 다음 연락 시점 + 그때까지의 행동 방법을 포함한 구체적인 행동 가이드 3~5문장
[[done]]
`;

  const content = [];
  const allowedTypes = ["image/jpeg","image/png","image/webp"];
  const imageList = Array.isArray(images) && images.length ? images.slice(0,isDetail ? 5 : 3) : (image?.data ? [image] : []);
  for (const img of imageList) {
    if (!img?.data) continue;
    const mediaType = allowedTypes.includes(img.mediaType) ? img.mediaType : "image/jpeg";
    content.push({ type:"image", source:{ type:"base64", media_type:mediaType, data:img.data } });
  }
  content.push({ type:"text", text:isDetail ? detailProtocol : quickProtocol });
  return { content, isDetail };
}

app.post("/api/love-analysis", async (req,res) => {
  try {
    const { content, isDetail } = buildAnalysisContent(req.body || {});
    const promptText = content[content.length - 1].text + `\nJSON 형식으로 다시 정리해서 출력하세요.`;
    const parsed = await createJsonWithRetry({
      model:isDetail ? "claude-sonnet-5" : "claude-haiku-4-5",
      maxTokens:isDetail ? 1700 : 700,
      retryMaxTokens:isDetail ? 1900 : 850,
      content:[...content.slice(0,-1),{type:"text",text:promptText}],
    });
    res.json({ ...parsed, serverVersion:SERVER_VERSION });
  } catch (error) {
    res.status(error?.statusCode || 500).json({ error:"AI 분석을 생성하지 못했습니다.", detail:error?.message || "알 수 없는 오류", serverVersion:SERVER_VERSION });
  }
});

function setStreamHeaders(res) {
  res.status(200);
  res.setHeader("Content-Type","text/event-stream; charset=utf-8");
  res.setHeader("Cache-Control","no-cache, no-transform");
  res.setHeader("Connection","keep-alive");
  res.setHeader("X-Accel-Buffering","no");
  if (res.socket && typeof res.socket.setNoDelay === "function") res.socket.setNoDelay(true);
  if (typeof res.flushHeaders === "function") res.flushHeaders();
  res.write(": connected " + " ".repeat(2048) + "\n\n");
}

function sendSse(res,event,data) {
  if (res.writableEnded) return;
  res.write(`event: ${event}\n`);
  res.write(`data: ${JSON.stringify(data)}\n\n`);
  res.write(":" + " ".repeat(2048) + "\n\n");
  if (typeof res.flush === "function") res.flush();
}

function parseReplyObject(raw,fallbackLabel) {
  const text = String(raw || "").trim();
  try {
    const first = text.indexOf("{");
    const last = text.lastIndexOf("}");
    if (first >= 0 && last > first) return JSON.parse(text.slice(first,last+1));
  } catch (_) {}
  return { label:fallbackLabel || "추천", text, reason:"" };
}

async function streamClaudeSections({ res, model, maxTokens, content, sectionOrder }) {
  let fullText = "";
  const emitted = new Set();
  let streamFinished = false;

  function tryEmit() {
    for (let i=0; i<sectionOrder.length; i++) {
      const name = sectionOrder[i];
      if (emitted.has(name)) continue;
      const marker = `[[${name}]]`;
      const nextName = sectionOrder[i+1] || "done";
      const nextMarker = `[[${nextName}]]`;
      const start = fullText.indexOf(marker);
      let end = fullText.indexOf(nextMarker);
      if (start < 0) continue;
      if (end < 0 && streamFinished && i === sectionOrder.length - 1) end = fullText.length;
      if (end < 0 || end <= start) continue;
      const raw = fullText.slice(start + marker.length,end).trim();
      if (!raw) continue;
      let value = raw;
      if (name.startsWith("reply")) {
        const n = Number(name.replace("reply","")) || 1;
        const labels = ["가장 자연스러운 답장","조금 더 다정한 답장","조금 더 여유 있는 답장"];
        value = parseReplyObject(raw,labels[n-1] || "추천");
      }
      sendSse(res,"section",{ name,value });
      emitted.add(name);
    }
  }

  const stream = anthropic.messages.stream({ model,max_tokens:maxTokens,messages:[{role:"user",content}] });
  stream.on("text",text => { fullText += text; tryEmit(); });
  await stream.finalMessage();
  streamFinished = true;
  tryEmit();
  sendSse(res,"done",{ serverVersion:SERVER_VERSION });
  if (!res.writableEnded) res.end();
}

app.post("/api/love-analysis-stream", async (req,res) => {
  try {
    const { content,isDetail } = buildAnalysisContent(req.body || {});
    setStreamHeaders(res);
    await streamClaudeSections({
      res,
      model:isDetail ? "claude-sonnet-5" : "claude-haiku-4-5",
      maxTokens:isDetail ? 1700 : 700,
      content,
      sectionOrder:isDetail
        ? ["meaning","emotion","flow","strategy","caution","reply1","reply2","reply3","advice","nextAction"]
        : ["meaning","emotion","caution","reply1","reply2","reply3","advice","nextAction"],
    });
  } catch (error) {
    if (!res.headersSent) return res.status(error?.statusCode || 500).json({ error:"스트리밍 분석을 생성하지 못했습니다.", detail:error?.message || "알 수 없는 오류", serverVersion:SERVER_VERSION });
    if (!res.writableEnded) { sendSse(res,"error",{message:error?.message || "스트리밍 오류"}); res.end(); }
  }
});

app.post("/api/starter-stream", async (req,res) => {
  try {
    const { relation,nickname,message,tone,starterGoal,profile,recentMemory } = req.body || {};
    const context = typeof message === "string" ? message.trim() : "";
    const prompt = `
사용자가 지금 상대에게 먼저 보낼 카카오톡/DM 첫 메시지 3개를 만드세요.
이 작업은 답장 추천이 아니라 사용자가 먼저 보내는 선톡입니다.
최근 상황은 과거 배경정보이며 상대가 방금 보낸 메시지가 아닙니다.
'응', '웅', '나도', '그래'처럼 답장처럼 시작하지 마세요.
정보가 부족해도 추가 질문 없이 바로 추천하세요.
[상대] ${nickname || "새로운/임의 상대"}
[현재 관계] ${relation || "애매한 관계"}
[오늘의 목표] ${starterGoal || "부담 없이 먼저 연락하기"}
[원하는 말투] ${tone || "자연스럽게"}
[최근 상황 - 과거 배경정보] ${context || "입력 없음"}
[저장된 상대 프로필] ${profile ? JSON.stringify(profile) : "없음"}
[최근 관계 기억] ${recentMemory || "없음"}
아래 표식을 정확히 같은 순서로 출력하세요. 코드블록/설명/머리말 금지.
[[reply1]]
{"label":"자연스럽게","text":"먼저 보낼 메시지","reason":"이유 1문장"}
[[reply2]]
{"label":"다정하게","text":"먼저 보낼 메시지","reason":"이유 1문장"}
[[reply3]]
{"label":"센스 있게","text":"먼저 보낼 메시지","reason":"이유 1문장"}
[[done]]
`;
    setStreamHeaders(res);
    await streamClaudeSections({ res,model:"claude-haiku-4-5",maxTokens:320,content:prompt,sectionOrder:["reply1","reply2","reply3"] });
  } catch (error) {
    if (!res.headersSent) return res.status(500).json({ error:"선톡 스트리밍 추천을 생성하지 못했습니다.", detail:error?.message || "알 수 없는 오류", serverVersion:SERVER_VERSION });
    if (!res.writableEnded) { sendSse(res,"error",{message:error?.message || "스트리밍 오류"}); res.end(); }
  }
});

app.listen(PORT,() => {
  console.log(`썸톡 AI 서버 실행 중: ${PORT} / ${SERVER_VERSION}`);
});
