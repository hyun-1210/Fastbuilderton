# 데이터베이스 설정 가이드

## 🗄️ SQLite 사용 (별도 서버 불필요!)

**중요**: SQLite는 **파일 기반 데이터베이스**입니다. 
- ❌ Docker 필요 없음
- ❌ 별도 서버 실행 필요 없음
- ❌ PostgreSQL/MySQL 설치 필요 없음
- ✅ 단순히 파일(`app.db`)로 저장됨

## 📁 데이터베이스 파일 위치

앱을 처음 실행하면 `backend/app.db` 파일이 자동으로 생성됩니다.

```
backend/
  ├── app.db          # ← SQLite 데이터베이스 파일 (자동 생성)
  ├── main.py
  ├── database.py
  └── models.py
```

## 🚀 사용 방법

### 1. 앱 실행 시 자동 생성

FastAPI 앱을 실행하면 자동으로 테이블이 생성됩니다:

```bash
cd backend
py -3.13 -m uvicorn main:app --reload
```

실행하면:
- `app.db` 파일이 자동 생성됨
- 모든 테이블이 자동 생성됨 (Users, Personas, InteractionLogs 등)

### 2. 데이터베이스 확인

SQLite 브라우저 도구로 확인할 수 있습니다:
- [DB Browser for SQLite](https://sqlitebrowser.org/) (무료 GUI 도구)
- 또는 VS Code 확장: "SQLite Viewer"

### 3. PostgreSQL로 전환하고 싶다면?

나중에 PostgreSQL을 사용하고 싶다면:

1. `.env` 파일에 DATABASE_URL 추가:
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
```

2. `requirements.txt`에 추가:
```
asyncpg>=0.29.0
```

3. `database.py`는 그대로 사용 가능 (자동으로 PostgreSQL 연결)

## 📊 테이블 구조

다음 6개 테이블이 자동 생성됩니다:

1. **users** - 사용자 정보
2. **personas** - 페르소나 (관리 대상 인물)
3. **interaction_logs** - 상호작용 기록
4. **persona_profiles** - AI 분석 성향
5. **persona_notes** - 메모 및 질문
6. **notification_logs** - 알림 로그

## 🔍 데이터베이스 파일 확인

```bash
# Windows PowerShell
cd backend
dir app.db

# 파일이 있으면 정상적으로 생성된 것
```

## ⚠️ 주의사항

- `app.db` 파일은 Git에 커밋하지 마세요 (`.gitignore`에 추가 권장)
- 개발/테스트용으로는 SQLite가 완벽합니다
- 프로덕션 환경에서는 PostgreSQL 권장 (하지만 해커톤에서는 SQLite로 충분!)

