require("dotenv").config();
const express = require("express");
const cors = require("cors");
const Anthropic = require("@anthropic-ai/sdk");

const app = express();
const PORT = process.env.PORT || 3000;
const SERVER_VERSION = "2026-08-10-starter-v4";

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

function parseClaudeJson(ai) {
  const text = ai.content
    .filter(item => item.type === "text")
    .map(item => item.text)
    .join("\n")
    .trim();

  try {
    return JSON.parse(text);
  } catch {
    const cleaned = text
      .replace(/^```json\s*/i, "")
      .replace(/```$/i, "")
      .trim();
    return JSON.parse(cleaned);
  }
}

app.post("/api/starter", async (req, res) => {
  try {
    const {
      relation,
      nickname,
      message,
      tone,
      starterGoal,
      profile,
      recentMemory,
    } = req.body || {};

    const context = typeof message === "string" ? message.trim() : "";

    const prompt = `
사용자가 지금 상대에게 먼저 보낼 카카오톡/DM 첫 메시지 3개를 만들어주세요.
이 작업은 절대로 '답장 추천'이 아닙니다.

[상대]
${nickname || "새로운/임의 상대"}

[현재 관계]
${relation || "애매한 관계"}

[오늘의 목표]
${starterGoal || "부담 없이 먼저 연락하기"}

[원하는 말투]
${tone || "자연스럽게"}

[최근 상황 - 과거 배경정보]
${context || "입력 없음"}

[저장된 상대 프로필]
${profile ? JSON.stringify(profile) : "없음"}

[최근 관계 기억]
${recentMemory || "없음"}

반드시 지킬 규칙:
- 사용자가 '지금 먼저 보내는 말'만 작성하세요.
- 최근 상황은 상대가 방금 보낸 메시지가 아닙니다.
- '어제', '지난주', '아까', '지난번'은 이미 끝난 과거 사건입니다.
- 예: '어제 데이트하고 집에 잘 들어갔다'가 입력돼도 '응 나도 잘 들어왔어' 같은 답장을 만들면 안 됩니다.
- '응', '웅', '나도', '그래'처럼 답장처럼 시작하지 마세요.
- 최근 상황이 비어 있어도 추가 정보를 요구하지 말고 관계와 목표만 보고 바로 3개를 작성하세요.
- 각 문장은 짧고 실제 카카오톡에서 바로 보낼 수 있는 자연스러운 한국어로 작성하세요.
- 세 문장의 느낌은 서로 조금씩 다르게 하세요.

아래 JSON만 출력하세요. 코드블록 금지.
{
  "replies": [
    {"label":"자연스럽게","text":"먼저 보낼 메시지"},
    {"label":"다정하게","text":"먼저 보낼 메시지"},
    {"label":"센스 있게","text":"먼저 보낼 메시지"}
  ]
}
`;

    const ai = await anthropic.messages.create({
      model: "claude-haiku-4-5",
      max_tokens: 180,
      messages: [{ role: "user", content: prompt }],
    });

    const parsed = parseClaudeJson(ai);

    if (!Array.isArray(parsed.replies) || parsed.replies.length < 3) {
      throw new Error("AI가 추천 문장 3개를 반환하지 않았습니다.");
    }

    res.json({
      ...parsed,
      serverVersion: SERVER_VERSION,
    });
  } catch (error) {
    console.error("선톡 API 오류:", error);
    res.status(500).json({
      error: "선톡 추천을 생성하지 못했습니다.",
      detail: error?.message || "알 수 없는 오류",
      serverVersion: SERVER_VERSION,
    });
  }
});

app.post("/api/love-analysis", async (req, res) => {
  try {
    const {
      relation,
      nickname,
      message,
      tone,
      image,
      images,
      mode = "quick",
      profile,
      recentMemory,
    } = req.body || {};

    const hasText = typeof message === "string" && message.trim();
    const hasSingleImage = !!image?.data;
    const hasImages = Array.isArray(images) && images.some(img => img?.data);

    if (!hasText && !hasSingleImage && !hasImages) {
      return res.status(400).json({
        error: "메시지를 입력하거나 대화 스크린샷을 올려주세요.",
        serverVersion: SERVER_VERSION,
      });
    }

    const isDetail = mode === "detail";

    const commonPrompt = `
당신은 연애 상황을 차분하고 현실적으로 분석하는 AI 코치입니다.

중요 원칙:
- 상대의 속마음을 사실처럼 단정하지 마세요.
- 확인되는 사실과 추정/가능성을 구분하세요.
- 실제 카카오톡/문자/DM에서 자연스럽게 쓸 수 있는 짧은 한국어 답장을 작성하세요.
- 스크린샷이 있으면 대화 순서와 앞뒤 맥락을 반영하세요.

[현재 관계]
${relation || "미입력"}

[상대 별명]
${nickname || "미입력"}

[대화/설명]
${hasText ? message.trim() : "첨부된 스크린샷을 분석"}

[원하는 답장 분위기]
${tone || "자연스럽게"}

[상대 프로필]
${profile ? JSON.stringify(profile) : "없음"}

[최근 기억]
${recentMemory || "없음"}
`;

    const quickPrompt = `
${commonPrompt}

JSON만 출력하세요.
{
  "meaning":"핵심 의미 1~2문장",
  "emotion":"감정/태도 가능성 1~2문장",
  "caution":"피하면 좋은 행동 1문장",
  "replies":[
    {"label":"가장 자연스러운 답장","text":"짧은 답장","reason":"이유 1문장"},
    {"label":"조금 더 다정한 답장","text":"짧은 답장","reason":"이유 1문장"},
    {"label":"조금 더 여유 있는 답장","text":"짧은 답장","reason":"이유 1문장"}
  ],
  "advice":"한 줄 조언"
}
`;

    const detailPrompt = `
${commonPrompt}

JSON만 출력하세요.
{
  "meaning":"핵심 의미와 맥락 2~4문장",
  "emotion":"감정·거리감·관심도의 가능성 2~4문장",
  "flow":"대화 흐름과 태도 변화 2~4문장",
  "strategy":"답장 목표와 톤 2~4문장",
  "caution":"피하면 좋은 행동 2~3문장",
  "replies":[
    {"label":"가장 자연스러운 답장","text":"답장","reason":"이유"},
    {"label":"조금 더 다정한 답장","text":"답장","reason":"이유"},
    {"label":"조금 더 여유 있는 답장","text":"답장","reason":"이유"}
  ],
  "advice":"한 줄 조언"
}
`;

    const content = [];
    const allowedTypes = ["image/jpeg", "image/png", "image/webp"];
    const imageList = Array.isArray(images) && images.length
      ? images.slice(0, 5)
      : (image?.data ? [image] : []);

    for (const img of imageList) {
      if (!img?.data) continue;
      const mediaType = allowedTypes.includes(img.mediaType)
        ? img.mediaType
        : "image/jpeg";

      content.push({
        type: "image",
        source: {
          type: "base64",
          media_type: mediaType,
          data: img.data,
        },
      });
    }

    content.push({
      type: "text",
      text: isDetail ? detailPrompt : quickPrompt,
    });

    const ai = await anthropic.messages.create({
      model: "claude-sonnet-5",
      max_tokens: isDetail ? 1150 : 520,
      messages: [{ role: "user", content }],
    });

    const parsed = parseClaudeJson(ai);
    res.json({ ...parsed, serverVersion: SERVER_VERSION });
  } catch (error) {
    console.error("Claude API 오류:", error);
    res.status(500).json({
      error: "AI 분석을 생성하지 못했습니다.",
      detail: error?.message || "알 수 없는 오류",
      serverVersion: SERVER_VERSION,
    });
  }
});

app.listen(PORT, () => {
  console.log(`썸톡 AI 서버 실행 중: ${PORT} / ${SERVER_VERSION}`);
});
