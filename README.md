# SDET BDD - pytest-bdd + Selenium + Security Scenarios

feature file (Gherkin) → @scenario (pytest 入口) → @given/@when/@then (Python code)

資安公司 SDET 面試專案，展示：
- **API BDD**：pytest-bdd + requests（lockout、錯誤不洩漏）
- **UI BDD**：pytest-bdd + Selenium Page Object（防暴力破解、權限導向）
- **資安思維**：錯誤訊息不洩漏帳號、多次失敗鎖帳、權限檢查

## 🚀 快速啟動

```bash
# 1. 建立環境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. 安裝依賴
pip install -e ".[test]"

# 3. 跑所有 BDD 測試
pytest -q

# 4. 只跑 UI 測試（看 Selenium）
pytest tests/steps/test_login_ui_steps.py -s -v

# 5. 開發模式（不 headless，看畫面）
pytest tests/steps/test_login_ui_steps.py --headed -s -v
