require("dotenv").config();
const express=require("express");
const cors=require("cors");
const Anthropic=require("@anthropic-ai/sdk");
const app=express();
app.use(cors());
app.use(express.json({limit:"100kb"}));
const anthropic=new Anthropic({apiKey:process.env.ANTHROPIC_API_KEY});

app.get("/",(req,res)=>res.json({ok:true,message:"연애톡 AI 서버가 작동 중입니다."}));

app.post("/api/love-analysis",async(req,res)=>{
 try{
  const {relation,nickname,message,tone}=req.body;
  if(!message) return res.status(400).json({error:"메시지를 입력해주세요."});

  const prompt=`당신은 차분하고 현실적인 연애 코치입니다.
상대의 속마음을 확정적으로 단정하지 말고 가능성으로 표현하세요.
과도한 밀당, 조종, 집착을 권하지 마세요.
답장은 실제 카카오톡에서 쓸 수 있는 자연스러운 한국어로 작성하세요.

관계: ${relation||"미입력"}
상대 별명: ${nickname||"미입력"}
상대 메시지: ${message}
원하는 답장 분위기: ${tone||"자연스럽게"}

아래 JSON 형식으로만 답하세요.
{
  "meaning":"핵심 의미 2~4문장",
  "emotion":"가능성 있는 감정 2~4문장",
  "caution":"주의할 점 2~3문장",
  "replies":[
    {"label":"가장 자연스러운 답장","text":"답장"},
    {"label":"조금 더 다정한 답장","text":"답장"},
    {"label":"조금 더 여유 있는 답장","text":"답장"}
  ],
  "advice":"현실적인 한 줄 조언"
}`;
  const m=await anthropic.messages.create({model:"claude-sonnet-5",max_tokens:1200,messages:[{role:"user",content:prompt}]});
  const text=m.content.filter(x=>x.type==="text").map(x=>x.text).join("\n").trim().replace(/^```json\s*/i,"").replace(/```$/i,"").trim();
  res.json(JSON.parse(text));
 }catch(e){
  console.error(e);
  res.status(500).json({error:"AI 분석을 생성하지 못했습니다.",detail:e.message});
 }
});

app.listen(process.env.PORT||3000,()=>console.log("연애톡 AI 서버 실행 중"));
