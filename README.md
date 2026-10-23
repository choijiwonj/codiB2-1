# codiB2-1# 📒 콘솔 가계부 (Budget App)

표준 라이브러리만 사용한 Python 콘솔 가계부 애플리케이션입니다.
JSONL 파일 기반 영구 저장, 제너레이터 스트리밍, 데코레이터 기반 공통 처리를 적용했습니다.

## ✨ 주요 기능

| 명령 | 설명 |
|------|------|
| `add` | 거래 추가 (대화형) |
| `list` | 거래 목록 (최신순) |
| `search` | 조건 검색 (기간/카테고리/타입/메모/태그) |
| `summary` | 월별 요약 + 카테고리 TOP N + 예산 사용률 |
| `budget set` | 월 예산 설정 |
| `category list/add/remove` | 카테고리 관리 |
| `update` | 거래 수정 (옵션 기반) |
| `delete` | 거래 삭제 |
| `import` | CSV 가져오기 |
| `export` | CSV 내보내기 |

## 📁 프로젝트 구조

```
budget_app/
├── __init__.py
├── __main__.py       # python -m budget_app 진입점
├── models.py         # 데이터 모델 + 입력 검증
├── decorators.py     # 예외처리/실행시간 데코레이터
├── repositories.py   # 파일 I/O (JSONL 스트리밍)
├── services.py       # 비즈니스 로직
└── cli.py            # CLI 파싱/대화형 입력
data/
├── transactions.jsonl
├── categories.jsonl
└── budgets.jsonl
```

## 🚀 실행 방법

### 요구 사항
- Python 3.10 이상 (타입 힌트 `list[str]` 사용)
- 외부 라이브러리 **불필요**

### 실행
```bash
python -m budget_app <명령> [옵션]
```

## 📖 사용 예시

### 거래 추가 (대화형)
```bash
$ python -m budget_app add
[거래 추가] 값을 입력하세요. (Ctrl+C로 취소)
  사용 가능한 카테고리: food, transport, rent, etc
날짜(YYYY-MM-DD): 2025-01-15
타입(income/expense): expense
카테고리: food
금액(양수): 12000
메모(선택): 점심 샌드위치
태그(쉼표 구분, 선택): lunch, work
[성공] 거래 저장 완료. id=a1b2c3d4
```

### 목록 조회
```bash
python -m budget_app list --limit 10
```

### 검색
```bash
# 1월 식비 지출
python -m budget_app search --from 2025-01-01 --to 2025-01-31 \
  --category food --type expense

# 메모 키워드
python -m budget_app search --q "커피"

# 태그
python -m budget_app search --tag lunch
```

### 월별 요약
```bash
python -m budget_app summary --month 2025-01 --top 5
```

출력 예시:
```
=== 2025-01 월별 요약 ===
 총 수입 :    3,000,000원
 총 지출 :    1,250,000원
 잔액    :    1,750,000원
 예산    :    1,500,000원  (사용률 83.3%)

--- 지출 TOP 5 ---
  rent          800,000원
  food          280,000원
  transport     120,000원
  etc            50,000원
```

### 예산 설정
```bash
python -m budget_app budget set --month 2025-01 --amount 1500000
```

### 카테고리 관리
```bash
python -m budget_app category list
python -m budget_app category add --name coffee
# 사용 중인 카테고리를 다른 이름으로 대체하면서 삭제
python -m budget_app category remove --name coffee --replace-with food
```

### 거래 수정/삭제
```bash
python -m budget_app update --id a1b2c3d4 --amount 15000 --memo "점심+커피"
python -m budget_app delete --id a1b2c3d4
```

### 가져오기/내보내기
```bash
# CSV 가져오기 (헤더: date,type,category,amount,memo,tags)
python -m budget_app import --from backup.csv

# 월별 내보내기
python -m budget_app export --out jan.csv --month 2025-01

# 기간 지정 내보내기
python -m budget_app export --out q1.csv --from 2025-01-01 --to 2025-03-31
```

## 🧩 설계 포인트

### 1. 모듈화 (책임 분리)
- **models**: 데이터 구조 + 입력 검증
- **repositories**: 파일 I/O만 담당 (JSONL 스트리밍)
- **services**: 비즈니스 로직
- **cli**: 사용자 입출력
- **decorators**: 공통 관심사(예외/로그)

### 2. 제너레이터 스트리밍
`TransactionRepository.stream()`은 파일을 한 줄씩 `yield` 하여 대용량 파일에도 **메모리 사용량이 일정**합니다.

```python
def stream(self) -> Iterator[Transaction]:
    with self.path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            yield Transaction.from_dict(json.loads(line))
```

### 3. 원자적 파일 쓰기
`update`/`delete`는 임시 파일에 쓴 뒤 `os.replace()`로 교체하여 **쓰기 중 중단되어도 원본 파일이 손상되지 않습니다.**

### 4. 데코레이터 기반 예외 처리
`@handle_errors`가 모든 예외를 가로채어 **스택트레이스 대신 "원인 + 해결 힌트"**를 출력합니다.

```
[오류] 날짜 형식 오류: '2025/1/15' (예: 2025-01-15)
[힌트] 입력 형식을 다시 확인하세요.
```

종료 코드:
- `0`: 정상
- `1`: 애플리케이션 오류
- `130`: 사용자 중단 (Ctrl+C)

### 5. 타입 힌트
모든 공개 함수/메서드에 타입 힌트를 적용했습니다. (`Iterator[Transaction]`, `Optional[str]` 등)

## 💾 데이터 파일 포맷 (JSONL)

**transactions.jsonl**
```json
{"id":"a1b2c3d4","type":"expense","date":"2025-01-15","category":"food","amount":12000,"memo":"점심","tags":["lunch"]}
```

**categories.jsonl**
```json
{"name":"food"}
{"name":"transport"}
```

**budgets.jsonl**
```json
{"month":"2025-01","amount":1500000}
```

## ⚠️ 제약 사항 준수

- ✅ 표준 라이브러리만 사용
- ✅ 저장 파일 3개 분리 (transactions / categories / budgets)
- ✅ CLI 옵션 `--` 통일
- ✅ 스택트레이스 출력 금지
- ✅ 오류 시 exit code ≠ 0

## 🐛 디버그 모드

실행 시간 로그를 보려면:
```bash
BUDGET_DEBUG=1 python -m budget_app summary --month 2025-01
```