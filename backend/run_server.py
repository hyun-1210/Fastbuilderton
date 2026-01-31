"""
서버 실행 스크립트. 시작 시 오류가 나면 전체 traceback을 출력합니다.
사용법: python run_server.py   또는   py run_server.py
"""
import sys
import traceback

def main():
    try:
        import uvicorn
        # --reload 없이 실행 (Windows에서 서브프로세스 크래시 방지)
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
        )
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
