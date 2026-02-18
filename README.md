# SDET BDD - pytest-bdd + Selenium + Security Scenarios

feature file (Gherkin) → @scenario (pytest 入口) → @given/@when/@then (Python code)

資安公司 SDET 面試專案，展示：
- **API BDD**：pytest-bdd + requests（lockout、錯誤不洩漏）
- **UI BDD**：pytest-bdd + Selenium Page Object（防暴力破解、權限導向）
- **Web App**：Flask 登入系統（session 管理、帳號鎖定）
- **資安思維**：錯誤訊息不洩漏帳號、多次失敗鎖帳、權限檢查

## 📁 專案結構

```
.
├── src/app/
│   ├── auth.py          # AuthService（業務邏輯）
│   ├── web.py           # Flask web 應用程式
│   └── templates/       # HTML 模板
├── tests/
│   ├── steps/
│   │   ├── test_login_steps.py       # API BDD 測試
│   │   └── test_login_ui_steps.py    # UI BDD 測試（Selenium）
│   └── features/        # Gherkin feature files
└── run_server.py        # 啟動 Flask server 的腳本

## 🚀 快速啟動

```bash
# 1. 建立環境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. 安裝依賴
pip install -e ".[test]"

# 3. 跑 API 測試（不需要 web server）
pytest -m api -v   # 使用 marker
# 或
pytest tests/steps/test_login_steps.py -v

# 4. 跑 UI 測試（需要先啟動 web server）
# Terminal 1: 啟動 Flask server
python run_server.py
# Terminal 2: 執行 UI 測試
pytest -m ui -v    # 使用 marker
# 或
pytest tests/steps/test_login_ui_steps.py -v

# 5. 跑所有測試（需要 server 在背景執行）
pytest -v

# 6. 手動測試 Web UI
# 開啟瀏覽器訪問 http://localhost:3000
# 帳號: demo / 密碼: demo
