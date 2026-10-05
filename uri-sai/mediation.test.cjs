const test = require('node:test');
const assert = require('node:assert/strict');
const express = require('express');
const { mountMediation } = require('./mediation.cjs');

async function fixture(options = {}) {
  const app = express();
  mountMediation(app, options);
  app.use(express.json());
  app.post('/api/love-analysis', (req, res) => res.json({ legacy: true, value: req.body.value }));
  app.get('/', (req, res) => res.json({ legacy: true }));
  const server = await new Promise(resolve => { const s = app.listen(0, '127.0.0.1', () => resolve(s)); });
  return { url: `http://127.0.0.1:${server.address().port}`, close: () => new Promise(resolve => server.close(resolve)) };
}
const payload = () => ({stage:'clarify',topic:'test',context:'',people:[{name:'a',facts:'a',feelings:'a',wishes:'a',consent:true},{name:'b',facts:'b',feelings:'b',wishes:'b',consent:true}]});
test('legacy routes remain reachable after new routes mount', async () => {
  const f = await fixture(); try {
    assert.deepEqual(await (await fetch(f.url)).json(), {legacy:true});
    const response = await fetch(f.url+'/api/love-analysis',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({value:7})});
    assert.deepEqual(await response.json(), {legacy:true,value:7});
  } finally { await f.close(); }
});
test('health, Android preflight and denied origin do not call the AI',async()=>{
  const f=await fixture({env:{OPENAI_API_KEY:'test'},analyze:()=>{throw Error('must not call');}});try{
    const health=await(await fetch(f.url+'/api/health')).json();assert.equal(health.product,'uri-sai');assert.equal(health.aiConfigured,true);
    const preflight=await fetch(f.url+'/api/mediate',{method:'OPTIONS',headers:{Origin:'https://localhost','Access-Control-Request-Headers':'content-type'}});assert.equal(preflight.status,204);assert.equal(preflight.headers.get('access-control-allow-origin'),'https://localhost');
    const denied=await fetch(f.url+'/api/health',{headers:{Origin:'https://untrusted.example'}});assert.equal(denied.status,403);
  }finally{await f.close();}
});
test('valid request uses separate mediation model and output',async()=>{
  let count=0;const f=await fixture({env:{OPENAI_API_KEY:'test',OPENAI_MODEL:'legacy-model'},analyze:async(input,options)=>{count++;assert.equal(options.model,'gpt-4.1-mini');return {safety:false,questions:['one','two']};}});try{
    const r=await fetch(f.url+'/api/mediate',{method:'POST',headers:{'Content-Type':'application/json',Origin:'https://localhost'},body:JSON.stringify(payload())});assert.equal(r.status,200);assert.equal((await r.json()).questions.length,2);assert.equal(count,1);
  }finally{await f.close();}
});
test('invalid consent, malformed JSON and oversized body never call the AI',async()=>{
  const f=await fixture({analyze:()=>{throw Error('must not call');}});try{
    const data=payload();data.people[1].consent=false;
    for(const [body,status] of [[JSON.stringify(data),400],['{bad',400],[' '.repeat(70000),413]]){
      const r=await fetch(f.url+'/api/mediate',{method:'POST',headers:{'Content-Type':'application/json'},body});assert.equal(r.status,status);assert.ok((await r.json()).error);
    }
  }finally{await f.close();}
});
test('twenty requests trigger a limit and error detail is not exposed',async()=>{
  const f=await fixture({analyze:async()=>{throw Error('private-provider-detail');}});try{
    for(let i=0;i<21;i++){
      const r=await fetch(f.url+'/api/mediate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload())});assert.equal(r.status,i===20?429:500);assert.ok(!(await r.text()).includes('private-provider-detail'));
    }
  }finally{await f.close();}
});
