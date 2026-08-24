const fs=require("fs");
const path=require("path");
try{
  const serverPath=path.join(process.cwd(),"server.js");
  const src=fs.existsSync(serverPath)?fs.readFileSync(serverPath,"utf8"):"";
  if(src.includes("2026-08-24-potentia-v80-pro-differentiation")){
    console.log("v80 PRO differentiation preload: already applied");
  }else{
    require("./patch_v80_pro_difference.js");
  }
}catch(error){
  console.error("v80 preload failed:",error?.stack||error);
  throw error;
}
