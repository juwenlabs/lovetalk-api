const fs=require("fs");
const path=require("path");
try{
  const serverPath=path.join(process.cwd(),"server.js");
  const src=fs.existsSync(serverPath)?fs.readFileSync(serverPath,"utf8"):"";
  if(src.includes("2026-08-24-potentia-v82-clarification-guard")){
    console.log("v82 clarification preload: already applied");
  }else{
    require("./patch_v82_clarification_guard.js");
  }
}catch(error){
  console.error("v82 preload failed:",error?.stack||error);
  throw error;
}
