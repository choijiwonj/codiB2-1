"""공통 데코레이터 및 애플리케이션 예외 정의"""
import os
import sys
import time
import functools
from typing import Callable


# ---------- 애플리케이션 예외 ----------
class AppError(Exception):
    """
    사용자에게 보여줄 비즈니스 오류.
    - message: 오류 원인
    - hint: 해결 방법 안내 (선택)
    """
    def __init__(self, message: str, hint: str = ""):
        super().__init__(message)
        self.message = message
        self.hint = hint


# ---------- 예외 처리 데코레이터 ----------
def handle_errors(func: Callable) -> Callable:
    """
    main() 함수를 감싸 모든 예외를 가로채고
    스택트레이스 없이 깔끔한 메시지로 출력한다.

    종료 코드:
      0   : 정상
      1   : 애플리케이션 오류
      130 : 사용자 중단 (Ctrl+C)
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except AppError as e:
            print(f"[오류] {e.message}", file=sys.stderr)
            if e.hint:
                print(f"[힌트] {e.hint}", file=sys.stderr)
            sys.exit(1)

        except KeyboardInterrupt:
            print("\n[중단] 사용자가 작업을 취소했습니다.", file=sys.stderr)
            sys.exit(130)

        except FileNotFoundError as e:
            print(f"[오류] 파일을 찾을 수 없습니다: {e.filename}", file=sys.stderr)
            print("[힌트] 경로를 다시 확인하세요.", file=sys.stderr)
            sys.exit(1)

        except PermissionError as e:
            print(f"[오류] 권한이 없습니다: {e.filename}", file=sys.stderr)
            sys.exit(1)

        except ValueError as e:
            # 모델 검증 실패 등
            print(f"[오류] 입력값 오류: {e}", file=sys.stderr)
            print("[힌트] 입력 형식을 다시 확인하세요.", file=sys.stderr)
            sys.exit(1)

        except Exception as e:
            # 예상치 못한 오류 - 디버그 모드일 때만 상세 출력
            if os.environ.get("BUDGET_DEBUG"):
                raise
            print(f"[오류] 알 수 없는 오류: {type(e).__name__}: {e}",
                  file=sys.stderr)
            print("[힌트] BUDGET_DEBUG=1 환경변수로 상세 로그를 볼 수 있습니다.",
                  file=sys.stderr)
            sys.exit(1)

    return wrapper


# ---------- 실행 시간 측정 데코레이터 ----------
def timed(func: Callable) -> Callable:
    """
    함수 실행 시간을 측정해 stderr에 출력.
    BUDGET_DEBUG 환경변수가 설정된 경우에만 활성화된다.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not os.environ.get("BUDGET_DEBUG"):
            return func(*args, **kwargs)

        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = (time.perf_counter() - start) * 1000
            print(f"[timed] {func.__qualname__}: {elapsed:.2f} ms",
                  file=sys.stderr)

    return wrapper