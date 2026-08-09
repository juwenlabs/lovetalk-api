require("dotenv").config();
const express = require("express");
const cors = require("cors");
const Anthropic = require("@anthropic-ai/sdk");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json({ limit: "10mb" }));

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

app.get("/", (req, res) => {
  res.json({ ok: true, message: "썸톡 AI 서버가 작동 중입니다." });
});

app.post("/api/love-analysis", async (req, res) => {
  try {
    const { relation, nickname, message, tone, image } = req.body;

    if ((!message || typeof message !== "string" || !message.trim()) && !image?.data) {
      return res.status(400).json({
        error: "메시지를 입력하거나 대화 스크린샷을 올려주세요."
      });
    }

    const prompt = `
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

아래 JSON 형식으로만 답하세요. 코드블록은 사용하지 마세요.

{
  "meaning": "대화의 핵심 의미와 흐름을 1~3문장으로 간결하게 설명",
  "emotion": "상대에게서 읽힐 수 있는 감정 또는 태도를 가능성 중심으로 1~3문장으로 설명",
  "caution": "지금 피하면 좋은 행동이나 표현을 1~2문장으로 설명",
  "replies": [
    {"label":"가장 자연스러운 답장","text":"1~2문장의 실제 보낼 수 있는 짧은 답장"},
    {"label":"조금 더 다정한 답장","text":"1~2문장의 실제 보낼 수 있는 짧은 답장"},
    {"label":"조금 더 여유 있는 답장","text":"1~2문장의 실제 보낼 수 있는 짧은 답장"}
  ],
  "advice": "지금 상황에서 가장 현실적인 한 줄 조언"
}
`;

    const content = [];

    if (image?.data) {
      const allowedTypes = ["image/jpeg", "image/png", "image/webp"];
      const mediaType = allowedTypes.includes(image.mediaType) ? image.mediaType : "image/jpeg";

      content.push({
        type: "image",
        source: {
          type: "base64",
          media_type: mediaType,
          data: image.data,
        },
      });
    }

    content.push({ type: "text", text: prompt });

    const ai = await anthropic.messages.create({
      model: "claude-sonnet-5",
      max_tokens: 850,
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
