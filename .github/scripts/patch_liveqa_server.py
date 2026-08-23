from pathlib import Path

p=Path('server.js')
s=p.read_text(encoding='utf-8')

assert '2026-08-23-potentia-v29-coach-safety' in s, 'expected v29 server not found'
s=s.replace('const SERVER_VERSION = "2026-08-23-potentia-v29-coach-safety";', 'const SERVER_VERSION = "2026-08-23-potentia-v30-starter-json-recovery";', 1)

old='''function parseClaudeJson(ai) {
  const text=getClaudeText(ai); const cleaned=text.replace(/^```json\\s*/i,"").replace(/^```\\s*/i,"").replace(/```$/i,"").trim();
  const first=cleaned.indexOf("{"); const last=cleaned.lastIndexOf("}");
  return JSON.parse(first>=0&&last>first?cleaned.slice(first,last+1):cleaned);
}
async function createJsonWithRetry({model,maxTokens,content,retryMaxTokens}){
  let ai=await anthropic.messages.create({model,system:POTENTIA_SYSTEM_PROMPT,max_tokens:maxTokens,messages:[{role:"user",content}]});
  try{return parseClaudeJson(ai);}catch(firstError){
    const retryContent=Array.isArray(content)?[...content,{type:"text",text:"\\n중요: 반드시 완전하고 유효한 JSON 하나만 출력하세요. 코드블록과 설명은 금지합니다."}]:String(content)+"\\n\\n반드시 완전하고 유효한 JSON 하나만 출력하세요.";
    ai=await anthropic.messages.create({model,system:POTENTIA_SYSTEM_PROMPT,max_tokens:retryMaxTokens||maxTokens,messages:[{role:"user",content:retryContent}]});
    return parseClaudeJson(ai);
  }
}'''
new=r'''function parseClaudeJson(ai) {
  const text=getClaudeText(ai); const cleaned=text.replace(/^```json\s*/i,"").replace(/^```\s*/i,"").replace(/```$/i,"").trim();
  const first=cleaned.indexOf("{"); const last=cleaned.lastIndexOf("}");
  return JSON.parse(first>=0&&last>first?cleaned.slice(first,last+1):cleaned);
}
function recoverReplyArrayJson(text){
  const cleaned=String(text||"").replace(/^```json\s*/i,"").replace(/^```\s*/i,"").replace(/```$/i,"").trim();
  const replies=[];
  let depth=0,start=-1,inString=false,escaped=false;
  for(let i=0;i<cleaned.length;i++){
    const ch=cleaned[i];
    if(inString){
      if(escaped){escaped=false;continue;}
      if(ch==='\\'){escaped=true;continue;}
      if(ch==='"')inString=false;
      continue;
    }
    if(ch==='"'){inString=true;continue;}
    if(ch==='{'){
      depth++;
      if(depth===2)start=i;
      continue;
    }
    if(ch==='}'){
      if(depth===2 && start>=0){
        const block=cleaned.slice(start,i+1);
        try{const obj=JSON.parse(block);if(obj&&typeof obj==='object'&&obj.text)replies.push(obj);}catch(_){}
        start=-1;
      }
      depth=Math.max(0,depth-1);
    }
  }
  if(replies.length>=3)return {replies:replies.slice(0,3)};
  const texts=[];
  const re=/"text"\s*:\s*"((?:\\.|[^"\\])*)"/g;
  let m;
  while((m=re.exec(cleaned))){
    let value=m[1];
    try{value=JSON.parse('"'+value+'"');}catch(_){}
    texts.push(String(value));
  }
  if(texts.length>=3){
    const labels=["자연스럽게","다정하게","센스 있게"];
    return {replies:texts.slice(0,3).map((text,i)=>({label:labels[i],text,reason:""}))};
  }
  return null;
}
async function createJsonWithRetry({model,maxTokens,content,retryMaxTokens}){
  let ai=await anthropic.messages.create({model,system:POTENTIA_SYSTEM_PROMPT,max_tokens:maxTokens,messages:[{role:"user",content}]});
  try{return parseClaudeJson(ai);}catch(firstError){
    const recovered=recoverReplyArrayJson(getClaudeText(ai));
    if(recovered)return recovered;
    const retryContent=Array.isArray(content)?[...content,{type:"text",text:"\n중요: 반드시 완전하고 유효한 JSON 하나만 출력하세요. reply 3개를 모두 끝까지 닫고 코드블록과 설명은 금지합니다."}]:String(content)+"\n\n반드시 완전하고 유효한 JSON 하나만 출력하세요. reply 3개를 모두 끝까지 닫으세요.";
    ai=await anthropic.messages.create({model,system:POTENTIA_SYSTEM_PROMPT,max_tokens:retryMaxTokens||maxTokens,messages:[{role:"user",content:retryContent}]});
    try{return parseClaudeJson(ai);}catch(secondError){
      const recoveredRetry=recoverReplyArrayJson(getClaudeText(ai));
      if(recoveredRetry)return recoveredRetry;
      throw secondError;
    }
  }
}'''
assert old in s, 'json helper anchor missing'
s=s.replace(old,new,1)

old='''createJsonWithRetry({model:"claude-haiku-4-5",maxTokens:advanced?420:300,retryMaxTokens:advanced?520:380,content:prompt})'''
new='''createJsonWithRetry({model:"claude-haiku-4-5",maxTokens:advanced?620:420,retryMaxTokens:advanced?760:560,content:prompt})'''
assert old in s, 'starter token anchor missing'
s=s.replace(old,new,1)

assert '2026-08-23-potentia-v30-starter-json-recovery' in s
assert 'function recoverReplyArrayJson' in s
p.write_text(s,encoding='utf-8')
print('Potentia v30 robust starter JSON recovery patch applied')
