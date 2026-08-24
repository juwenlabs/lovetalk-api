const fs=require("fs");
const path=require("path");
const serverPath=path.join(process.cwd(),"server.js");
let src=fs.readFileSync(serverPath,"utf8");

if(src.includes("2026-08-24-potentia-v82-clarification-guard")){
  console.log("v82 clarification guard already applied");
}else{
  if(!src.includes("2026-08-24-potentia-v80-pro-differentiation")){
    require("./patch_v80_pro_difference.js");
    src=fs.readFileSync(serverPath,"utf8");
  }

  src=src.replace(/const SERVER_VERSION = "[^"]+";/,'const SERVER_VERSION = "2026-08-24-potentia-v82-clarification-guard";');

  const marker='[관계·참여·과투자]';
  const rules=`[정보 부족과 추가 질문]\n- 답장의 방향을 바꿀 수 있는 핵심 정보가 없으면 그 빈칸을 추측으로 채우지 않는다. 필요한 추가 질문은 최대 3개이며 실제 행동과 시간 순서를 확인하는 질문을 우선한다.\n- 프런트가 메시지 안에 '[사용자 추가 정보]' 블록을 넣어 보낸 경우, 그 안의 답변은 사용자가 이번 요청에서 직접 제공한 확인 사실로 취급한다. 단, 그 답변에 없는 내용을 확장 추론하지 않는다.\n- 프런트가 '[추가 정보 부족: 사용자가 정보 없이 진행을 선택함'이라고 표시한 경우, 부족한 사실을 새로 만들지 말고 가장 낮은 위험의 보수적인 답장과 행동을 선택한다.\n- 특히 읽씹·안읽씹·짧은 답장·느린 답장·약속 거절·취소처럼 시간 경과, 후속 연락 여부, 대안 날짜, 반복 여부에 따라 판단이 달라지는 상황에서는 해당 사실이 없으면 확정적으로 해석하지 않는다.\n\n`;
  if(!src.includes(marker)) throw new Error("v82 prompt marker not found");
  src=src.replace(marker,rules+marker);

  fs.writeFileSync(serverPath,src,"utf8");
  console.log("Applied Potentia v82 clarification guard");
}
