# Fastbuilderton : FastAPI + React Native 모노레포 프로젝트

## 💡 프로젝트 소개
Fastbuilderton은 해커톤을 위한 모노레포 프로젝트입니다.
FastAPI 백엔드와 React Native(Expo) 프론트엔드를 포함하며, NVIDIA NIM API를 통합할 수 있는 구조로 설계되었습니다.

### ✨ Key Features
- **Real-time AI Analysis:** NVIDIA NIM(Llama 3)을 활용한 고속 추론
- **Relationship Coaching:** 사용자 맞춤형 대화 가이드 및 메시지 추천
- **Cross Platform:** React Native 기반으로 Android/iOS 모두 지원

## 🛠 Tech Stack
| Category | Technology | Usage |
| --- | --- | --- |
| **AI / ML** | **NVIDIA NIM** | Llama-3-70b-instruct (핵심 추론 엔진) |
| | **RAG** | 사용자 데이터 기반 맞춤형 응답 생성 |
| **Backend** | **FastAPI** | 비동기 API 서버, REST API |
| **Frontend** | **React Native** | Cross-platform Mobile App (Expo) |
| **Infra** | **Railway** | Server Deployment (CI/CD) |

## 📁 프로젝트 구조

```
Fastbuilderton/
├── backend/                 # FastAPI 백엔드
│   ├── main.py              # FastAPI 앱 진입점
│   ├── requirements.txt     # Python 의존성
│   ├── .env.example         # 환경 변수 템플릿
│   ├── routes/              # API 라우터
│   │   ├── __init__.py
│   │   └── ai_router.py    # NVIDIA NIM API 라우터
│   ├── Lib/                 # Python 3.13 로컬 패키지 (gitignore)
│   └── Scripts/             # Python 스크립트 (gitignore)
│
└── frontend/                # React Native (Expo) 프론트엔드
    ├── App.js               # 메인 앱 컴포넌트
    ├── package.json          # Node.js 의존성
    ├── src/
    │   └── services/
    │       ├── __init__.js
    │       └── api.js       # 백엔드 API 통신 서비스
    └── node_modules/        # Node 패키지 (gitignore)
```

## 🚀 How to Run

### Backend (FastAPI)

**⚠️ 중요: Python 3.13 사용 필수 (Python 3.14는 호환성 문제로 사용 불가)**

1. 환경 변수 설정 (`.env` 파일 생성)
   ```bash
   cd backend
   cp .env.example .env
   # .env 파일에 NVIDIA_API_KEY 추가
   ```

2. 패키지 설치 및 실행
   ```bash
   cd backend
   # Python 3.13으로 패키지 설치
   py -3.13 -m pip install -r requirements.txt
   
   # Python 3.13으로 서버 실행 (반드시 py -3.13 사용!)
   py -3.13 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. 서버 확인
   - Swagger UI: http://localhost:8000/docs
   - 헬스 체크: http://localhost:8000/health
   - API 테스트: http://localhost:8000/api/ai/test

**참고**: Windows에서 `py` 명령어는 기본적으로 Python 3.14를 사용하므로, 반드시 `py -3.13`을 명시해야 합니다.

### Frontend (React Native / Expo)

1. 패키지 설치
   ```bash
   cd frontend
   npm install
   ```

2. 앱 실행
   ```bash
   # 개발 서버 시작
   npx expo start
   
   # 플랫폼별 실행
   # - Android: Press 'a' 또는 npx expo start --android
   # - iOS: Press 'i' 또는 npx expo start --ios
   # - Web: Press 'w' 또는 npx expo start --web
   ```

3. 웹에서 테스트하기
   ```bash
   # 웹 지원 패키지가 이미 설치되어 있음
   npx expo start --web
   # 브라우저에서 http://localhost:19006 자동으로 열림
   ```

**참고**: 
- Android 에뮬레이터: 백엔드는 `http://10.0.2.2:8000`으로 자동 연결
- iOS 시뮬레이터: 백엔드는 `http://127.0.0.1:8000`으로 자동 연결
- 웹 브라우저: 백엔드는 `http://localhost:8000`으로 자동 연결

## 📝 주요 API 엔드포인트

### Backend API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | 루트 엔드포인트 |
| GET | `/health` | 헬스 체크 |
| GET | `/api/ai/test` | AI 라우터 테스트 |
| POST | `/api/ai/chat` | AI 채팅 (더미 응답) |

### API 사용 예시

```javascript
// 프론트엔드에서 사용
import { apiService } from './src/services/api';

// 헬스 체크
const health = await apiService.healthCheck();

// AI 채팅
const response = await apiService.chatWithAI('안녕하세요!', 100);
```

## 🔧 개발 환경 설정

### 필수 요구사항
- **Python**: 3.13 (3.14는 호환성 문제로 사용 불가)
- **Node.js**: 18.x 이상
- **Expo CLI**: `npm install -g expo-cli` (선택사항)

### 환경 변수 설정

1. `backend/.env` 파일 생성:
   ```bash
   cd backend
   cp .env.example .env
   ```

2. `.env` 파일에 API 키 추가:
   ```
   NVIDIA_API_KEY=your_nvidia_api_key_here
   ```

## 🐛 문제 해결

### Python 3.14 호환성 문제
- **증상**: `TypeError: _eval_type() got an unexpected keyword argument 'prefer_fwd_module'`
- **해결**: 반드시 `py -3.13`을 사용하여 Python 3.13으로 실행

### 포트 충돌
- **증상**: `Address already in use`
- **해결**: 
  ```powershell
  # Windows에서 포트 8000 사용 프로세스 확인 및 종료
  netstat -ano | findstr :8000
  Stop-Process -Id [PID] -Force
  ```

### CORS 오류
- 백엔드 `main.py`에서 이미 `allow_origins=["*"]`로 설정되어 있음
- 문제가 지속되면 백엔드 서버 재시작

## 📚 참고 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Expo 공식 문서](https://docs.expo.dev/)
- [React Native 공식 문서](https://reactnative.dev/)

---

## 👨‍💻 Team
[팀원 이름을 여기에 추가하세요]

---

**해커톤 프로젝트** - 빠른 개발과 코드 가독성을 우선시합니다.