from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')

old='const Anthropic = require("@anthropic-ai/sdk");\n'
if old not in s: raise SystemExit('Anthropic import missing')
s=s.replace(old,'',1)

old='const SERVER_VERSION = "2026-08-24-potentia-v76-reply-detail-safety";'
new='const SERVER_VERSION = "2026-08-24-potentia-v77-openai-terra";'
if old not in s: raise SystemExit('v76 version marker missing')
s=s.replace(old,new,1)

old='const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });'
new=r'''const OPENAI_MODEL = process.env.OPENAI_MODEL || "gpt-5.6-terra";

function toOpenAIInput(messages=[]){
  const input=[];
  for(const msg of Array.isArray(messages)?messages:[]){
    const parts=[];
    const content=msg?.content;
    if(typeof content==="string"){
      parts.push({type:"input_text",text:content});
    }else if(Array.isArray(content)){
      for(const part of content){
        if(part?.type==="text"){
          parts.push({type:"input_text",text:String(part.text||"")});
        }else if(part?.type==="image" && part?.source?.type==="base64" && part?.source?.data){
          const media=String(part.source.media_type||"image/jpeg");
          parts.push({type:"input_image",image_url:`data:${media};base64,${part.source.data}`});
        }
      }
    }
    if(parts.length) input.push({role:msg?.role==="assistant"?"assistant":"user",content:parts});
  }
  return input;
}

function extractOpenAIText(data){
  if(typeof data?.output_text==="string" && data.output_text.trim()) return data.output_text;
  const chunks=[];
  for(const item of Array.isArray(data?.output)?data.output:[]){
    for(const part of Array.isArray(item?.content)?item.content:[]){
      if(part?.type==="output_text" && typeof part.text==="string") chunks.push(part.text);
      else if(typeof part?.text==="string") chunks.push(part.text);
    }
  }
  return chunks.join("").trim();
}

async function openAICompatCreate(opts={}){
  const apiKey=String(process.env.OPENAI_API_KEY||"").trim();
  if(!apiKey) throw new Error("OPENAI_API_KEY is not configured");
  const controller=new AbortController();
  const timer=setTimeout(()=>controller.abort(),45000);
  try{
    const body={
      model:OPENAI_MODEL,
      input:toOpenAIInput(opts.messages),
      max_output_tokens:Math.max(256,Number(opts.max_tokens)||800)
    };
    if(opts.system) body.instructions=String(opts.system);
    const r=await fetch("https://api.openai.com/v1/responses",{
      method:"POST",
      headers:{"Content-Type":"application/json","Authorization":`Bearer ${apiKey}`},
      body:JSON.stringify(body),
      signal:controller.signal
    });
    const raw=await r.text();
    let data={};
    try{ data=JSON.parse(raw); }catch(_){ }
    if(!r.ok){
      const msg=data?.error?.message||raw||`HTTP ${r.status}`;
      throw new Error(`OpenAI API ${r.status}: ${String(msg).slice(0,500)}`);
    }
    const text=extractOpenAIText(data);
    if(!text) throw new Error("OpenAI API returned empty text");
    // Preserve the Anthropic SDK response shape used throughout this server.
    return {content:[{type:"text",text}],model:data?.model||OPENAI_MODEL,usage:data?.usage||{}};
  }finally{
    clearTimeout(timer);
  }
}

// Compatibility wrapper: existing app logic can keep calling anthropic.messages.create,
// while every model request is now served by OpenAI Responses API.
const anthropic={messages:{create:openAICompatCreate}};'''
if old not in s: raise SystemExit('Anthropic client anchor missing')
s=s.replace(old,new,1)

# Strengthen the grounding rule for questions such as "내일 뭐해?".
anchor='''- 사용자가 제공하지 않은 현재 날씨, 장소, 일정, 직업 사정, 상대의 피곤함·기분·의도·활동을 사실처럼 만들어 답장에 넣지 않는다. 필요한 정보가 없으면 추측을 문장 재료로 채우지 말고 입력된 사실만 사용하거나 낮은 위험의 질문으로 확인한다.'''
extra='''- 사용자가 제공하지 않은 현재 날씨, 장소, 일정, 직업 사정, 상대의 피곤함·기분·의도·활동을 사실처럼 만들어 답장에 넣지 않는다. 필요한 정보가 없으면 추측을 문장 재료로 채우지 말고 입력된 사실만 사용하거나 낮은 위험의 질문으로 확인한다.\n- 특히 상대가 “오늘 뭐해?”, “내일 뭐해?”, “주말 뭐해?”처럼 사용자의 일정을 묻는 경우, 사용자가 실제 일정을 입력하지 않았다면 평일/주말이라는 달력 정보만으로 바쁘다·시간이 없다·약속이 없다·집에 있다·쉬고 있다 등을 추정하지 않는다. 일정 사실을 모르면 “왜, 무슨 일 있어?”, “왜? 뭐 하려고?”처럼 거짓 사실 없이 의도를 되묻는 짧은 답장을 우선한다.'''
if anchor not in s: raise SystemExit('grounding prompt anchor missing')
s=s.replace(anchor,extra,1)

p.write_text(s,encoding='utf-8')
