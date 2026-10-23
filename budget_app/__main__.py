# __main__.py
"""python -m budget_app 로 실행하는 진입점"""
import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())