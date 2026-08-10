require("dotenv").config();
const express = require("express");
const cors = require("cors");
const Anthropic = require("@anthropic-ai/sdk");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json({ limit: "35mb" }));

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

app.get("/", (req, res) => {
  res.json({ ok: true, message: "썸톡 AI 서버가 작동 중입니다." });
});

app.post("/api/love-analysis", async (req, res) => {
  try {
    const { relation, nickname, message, tone, image, images, mode = "quick", starterGoal, profile, recentMemory } = req.body;

    if ((!message || typeof message !== "string" || !message.trim()) && !image?.data && !(Array.isArray(images) && images.length)) {
      return res.status(400).json({
        error: "메시지를 입력하거나 대화 스크린샷을 올려주세요."
      });
    }

    const isDetail = mode === "detail";

    const commonPrompt = `
당신은 연애 상황을 차분하고 현실적으로 분석하는 AI 코치입니다.

중요 원칙:
- 상대의 속마음을 사실처럼 확정적으로 단정하지 마세요.
- 대화에서 확인되는 사실과 추정/가능성을 구분하세요.
- 과도한 밀당, 심리 조종, 집착, 감정적 압박을 권하지 마세요.
- 답장은 실제 카카오톡/문자/DM에서 자연스럽게 쓸 수 있는 짧은 한국어로 작성하세요.
- 스크린샷이 제공된 경우 이미지 속 대화를 직접 읽고, 말풍선의 순서와 앞뒤 맥락을 최대한 반영하세요.
- 스크린샷에서 누가 사용자이고 누가 상대방인지 확실하지 않다면 임의로 확정하지 말고 불확실성을 표시하세요.
- 프로필 사진, 이름, 전화번호 같은 개인정보 자체를 평가하지 말고 대화 내용과 맥락에 집중하세요.
- 이미지가 흐리거나 일부 문장이 잘려 읽기 어렵다면 그 사실을 솔직히 언급하세요.

[현재 관계]
${relation || "미입력"}

[상대 별명]
${nickname || "미입력"}

[사용자가 직접 입력한 대화/설명]
${message?.trim() || "없음 - 첨부된 대화 스크린샷을 중심으로 분석"}

[원하는 답장 분위기]
${tone || "자연스럽게"}

[상대 프로필 / AI 기억]
${profile ? JSON.stringify(profile) : "저장된 프로필 없음"}

[최근 이 상대와의 분석 흐름]
${recentMemory || "최근 기록 없음"}
`;

    const quickPrompt = `
${commonPrompt}

[분석 모드]
간편 추천: 속도와 실용성을 우선합니다. 불필요한 설명은 줄이고 바로 사용할 수 있게 간결하게 답하세요.

아래 JSON 형식으로만 답하세요. 코드블록은 사용하지 마세요.
{
  "meaning": "대화의 핵심 의미를 1~2문장으로 아주 간결하게 설명",
  "emotion": "상대의 감정 또는 태도를 가능성 중심으로 1~2문장으로 설명",
  "caution": "지금 피하면 좋은 행동을 1문장으로 설명",
  "replies": [
    {"label":"가장 자연스러운 답장","text":"1문장의 실제 보낼 수 있는 짧은 답장","reason":"왜 이 답장이 좋은지 1문장"},
    {"label":"조금 더 다정한 답장","text":"1문장의 실제 보낼 수 있는 짧은 답장","reason":"왜 이 답장이 좋은지 1문장"},
    {"label":"조금 더 여유 있는 답장","text":"1문장의 실제 보낼 수 있는 짧은 답장","reason":"왜 이 답장이 좋은지 1문장"}
  ],
  "advice": "현실적인 한 줄 조언"
}
`;

    const detailPrompt = `
${commonPrompt}

[분석 모드]
상세 추천: 대화의 앞뒤 흐름과 상대의 태도 변화를 더 깊게 분석하세요. 단, 추측은 가능성으로 표현하고 과도하게 길게 쓰지 마세요.

아래 JSON 형식으로만 답하세요. 코드블록은 사용하지 마세요.
{
  "meaning": "대화의 핵심 의미와 숨은 맥락을 2~4문장으로 설명",
  "emotion": "상대에게서 읽힐 수 있는 감정·거리감·관심도의 가능성을 2~4문장으로 설명",
  "flow": "앞뒤 대화 흐름과 상대의 태도 변화, 질문 빈도나 말투 변화를 2~4문장으로 설명",
  "strategy": "지금 답장의 목표와 타이밍, 어떤 톤이 좋은지 2~4문장으로 설명",
  "caution": "지금 피하면 좋은 행동이나 표현을 2~3문장으로 설명",
  "replies": [
    {"label":"가장 자연스러운 답장","text":"1~2문장의 실제 보낼 수 있는 답장","reason":"왜 이 답장이 좋은지 1~2문장"},
    {"label":"조금 더 다정한 답장","text":"1~2문장의 실제 보낼 수 있는 답장","reason":"왜 이 답장이 좋은지 1~2문장"},
    {"label":"조금 더 여유 있는 답장","text":"1~2문장의 실제 보낼 수 있는 답장","reason":"왜 이 답장이 좋은지 1~2문장"}
  ],
  "advice": "지금 상황에서 가장 현실적인 한 줄 조언"
}
`;

    const starterPrompt = `
${commonPrompt}

[분석 모드]
오늘 뭐라고 보내지?: 상대가 먼저 메시지를 보낸 상황이 아니라, 사용자가 먼저 가볍게 연락을 시작하고 싶은 상황입니다.

[오늘의 목표]
${starterGoal || "자연스럽게 대화 다시 이어가기"}

다음 원칙을 지키세요.
- 부담스럽거나 과하게 의미심장한 첫 연락은 피하세요.
- 답장을 강요하는 표현, 감정 압박, 밀당 유도는 피하세요.
- 실제 카카오톡/DM에서 바로 보낼 수 있는 짧고 자연스러운 문장으로 제안하세요.
- 사용자의 관계와 목표에 맞춰 3가지 서로 다른 시작 메시지를 제안하세요.

아래 JSON 형식으로만 답하세요. 코드블록은 사용하지 마세요.
{
  "meaning": "오늘 먼저 연락할 때의 핵심 방향을 1~2문장으로 설명",
  "emotion": "현재 관계에서 너무 부담스럽지 않게 접근하기 위한 분위기를 1~2문장으로 설명",
  "strategy": "언제, 어떤 톤으로 시작하면 좋은지 1~3문장으로 설명",
  "caution": "피하면 좋은 시작 방식이나 표현을 1~2문장으로 설명",
  "replies": [
    {"label":"가장 자연스러운 시작","text":"실제로 바로 보낼 수 있는 짧은 첫 메시지","reason":"왜 이 시작이 자연스러운지 1문장"},
    {"label":"조금 더 다정하게","text":"실제로 바로 보낼 수 있는 짧은 첫 메시지","reason":"왜 이 시작이 자연스러운지 1문장"},
    {"label":"조금 더 센스 있게","text":"실제로 바로 보낼 수 있는 짧은 첫 메시지","reason":"왜 이 시작이 자연스러운지 1문장"}
  ],
  "advice": "오늘 먼저 연락할 때 기억하면 좋은 한 줄 조언"
}
`;

    const prompt = mode === "starter" ? starterPrompt : (isDetail ? detailPrompt : quickPrompt);

    const content = [];

    const allowedTypes = ["image/jpeg", "image/png", "image/webp"];
    const imageList = Array.isArray(images) && images.length
      ? images.slice(0,5)
      : (image?.data ? [image] : []);

    for (const img of imageList) {
      if (!img?.data) continue;
      const mediaType = allowedTypes.includes(img.mediaType) ? img.mediaType : "image/jpeg";
      content.push({
        type: "image",
        source: {
          type: "base64",
          media_type: mediaType,
          data: img.data,
        },
      });
    }

    content.push({ type: "text", text: prompt });

    const ai = await anthropic.messages.create({
      model: "claude-sonnet-5",
      max_tokens: mode === "starter" ? 620 : (isDetail ? 1150 : 520),
      messages: [{ role: "user", content }],
    });

    const text = ai.content
      .filter(item => item.type === "text")
      .map(item => item.text)
      .join("\n")
      .trim();

    let parsed;
    try {
      parsed = JSON.parse(text);
    } catch {
      const cleaned = text.replace(/^```json\s*/i, "").replace(/```$/i, "").trim();
      parsed = JSON.parse(cleaned);
    }

    res.json(parsed);
  } catch (error) {
    console.error("Claude API 오류:", error);
    res.status(500).json({
      error: "AI 분석을 생성하지 못했습니다.",
      detail: error?.message || "알 수 없는 오류",
    });
  }
});

app.listen(PORT, () => {
  console.log("썸톡 AI 서버 실행 중:", PORT);
});
