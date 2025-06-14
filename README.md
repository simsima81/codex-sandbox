# Hanauer-style ML Mispricing Model

이 프로젝트는 FMP와 SEC 데이터를 이용해 주식별 내재가치와 시장가격 차이를 계산하고, 머신러닝으로 기대수익률을 예측하여 롱숏 전략을 백테스트합니다.

## 설치
```bash
pip install -r requirements.txt
```

## 실행 예시
```python
from src.fetcher import fetch_fmp
from src.features import compute_features
from src.model import MispricingModel
from src.signal import generate_signals
from src.backtest import run_backtest
```

## 환경 변수
`.env` 파일에 API 키를 설정하세요.
```env
FMP_KEY=<...>
SEC_AGENT=Mozilla/5.0 (X11; Codex Bot)
```

## 테스트
```bash
black -q .
pytest -q
```
