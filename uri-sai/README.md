# 기존 Render 서버에 우리 사이 중재 API 추가

대상: `juwenlabs/lovetalk-api`의 `main`, 기존 서비스 `https://lovetalk-api.onrender.com`.

기존 `server.js`를 기준으로 새 중재 기능을 추가했습니다. 기존 썸톡 API와 package.json의 시작 명령은 유지합니다.

## 변경 파일

- `server.js`: 기존 `app.use(cors());` 앞에 중재 기능 등록 한 줄 추가
- `uri-sai/mediation.cjs`: `/api/health`, `/api/mediate` 등록, Origin 제한, 60kb 입력 제한, 요청 제한, 오류 처리
- `uri-sai/core.mjs`: 앱에서 검증한 OpenAI 중재 엔진
- `uri-sai/core.test.mjs`, `uri-sai/mediation.test.cjs`: 실제 AI 전송 없이 테스트

## Render 환경 변수

기존 서버에 설정된 `OPENAI_API_KEY`를 사용합니다. PC의 `.env`는 Render로 자동 전송되지 않습니다. 키가 없다면 Render의 Environment에 직접 설정하세요. 키를 GitHub에 올리지 마세요.

새 중재 기능의 모델은 `URI_SAI_OPENAI_MODEL=gpt-4.1-mini`로 별도 지정할 수 있습니다. 생략하면 같은 모델을 사용합니다. 기존 썸톡의 `OPENAI_MODEL` 설정에는 영향을 주지 않습니다.

기본 Android Origin `https://localhost`, `http://localhost`와 해당 Render 주소를 허용합니다. 추가 웹 프런트엔드가 있다면 `URI_SAI_ALLOWED_ORIGINS`에 쉼표로 구분해 등록하세요.

## 배포와 확인

검토 후 변경을 `main`에 반영하면 자동 배포 설정에 따라 기존 Render 서버가 업데이트될 수 있습니다. 현재 운영 코드에 영향을 주는 최종 반영은 검토 후 진행하세요.

현재 Render의 Root Directory와 Build Command, Start Command는 바꿀 필요가 없습니다. 새 라이브러리는 추가하지 않았으며 기존 Express를 사용합니다. Node.js 22 이상 환경에서 확인했습니다.

배포 후 `https://lovetalk-api.onrender.com/api/health`에서 `product: uri-sai`, `aiConfigured: true`를 확인합니다. 이 표시는 키가 설정됐다는 뜻이며 실제 AI 응답 검증을 대신하지 않습니다.

테스트 명령:

```text
node --test uri-sai/core.test.mjs uri-sai/mediation.test.cjs
```

원래 대화는 로그나 파일에 저장하지 않습니다. 기존 호스팅·AI 제공자의 데이터 처리 정책은 별도로 적용됩니다. 요청 제한은 서버 메모리와 접속 IP 기준입니다. Render 프록시의 주소가 공통으로 보이면 여러 이용자가 제한을 공유할 수 있습니다. 계정별 제한과 인증은 별도 운영 작업입니다.

