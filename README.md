# SDET BDD - pytest-bdd + Selenium + Security Scenarios

QA/SDET 面試可用的專案模板:
feature file (Gherkin) → @scenario (pytest 入口) → @given/@when/@then (Python code)
- **Unit Tests**：直接測試業務邏輯（AuthService）- 快速、不依賴 server
- **API Tests**：測試 HTTP endpoints（lockout、session、權限）
- **UI Tests**：pytest-bdd + Selenium Page Object（防暴力破解、權限導向）
- **Web App**：Flask 登入系統（session 管理、帳號鎖定）
- **資安思維**：錯誤訊息不洩漏帳號、多次失敗鎖帳、權限檢查

## 專案結構

```
.
├── src/app/
│   ├── auth.py              # AuthService 業務邏輯
│   ├── web.py               # Flask web 應用程式
│   └── templates/           # HTML 模板
├── tests/
│   ├── steps/
│   │   ├── test_login_steps.py      # Unit BDD 測試（直接測 AuthService）
│   │   └── test_login_ui_steps.py   # UI BDD 測試（Selenium）
│   ├── test_api_endpoints.py        # HTTP API 測試（requests）
│   └── features/            # Gherkin feature files
└── run_server.py            # 啟動 Flask server 的腳本
```

## 快速啟動

```bash
# 1. 建立環境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. 安裝依賴
pip install -e ".[test]"

# 3. 跑 Unit 測試（直接測試 AuthService 業務邏輯，不需要 web server）
pytest -m unit -v   # pytest tests/steps/test_login_steps.py -v

# 4. 跑 API 測試（測試 HTTP endpoints，需要先啟動 web server）
# Terminal 1: 啟動 Flask server
python run_server.py
# Terminal 2: 執行 API 測試
pytest -m api -v    # pytest tests/test_api_endpoints.py -v

# 5. 跑 UI 測試（執行 Web UI 測試，需要先啟動 web server）
# Terminal 1: 啟動 Flask server
python run_server.py
# Terminal 2: 執行 Web UI 測試
pytest -m ui -v    # pytest tests/steps/test_login_ui_steps.py -v

# 6. 跑所有測試（需要 server 在背景執行）
# Terminal 1: 啟動 Flask server
python run_server.py
# Terminal 2
pytest -v

# 7. 手動測試 Web UI
# 開啟瀏覽器訪問 http://localhost:3000
# 帳號: demo / 密碼: demo
```

## 測試架構說明（測試金字塔）

展示完整的三層測試架構，符合測試金字塔最佳實踐：

```
        /\
       /UI\          ← 最慢、最脆弱（需要 browser + server）
      /____\           @pytest.mark.ui
     /      \
    /  API   \       ← 中等速度（需要 server，測試 HTTP）
   /__________\        @pytest.mark.api
  /            \
 /     Unit     \    ← 最快、最穩定（不需要 server）
/________________\     @pytest.mark.unit
```

### Unit Tests (`@pytest.mark.unit`)
**測試對象**：Python 類別和方法（業務邏輯層）
**不需要**：Web server, HTTP, Browser
**測試文件**：`tests/steps/test_login_steps.py`

```python
from app.auth import AuthService  # 直接 import Python class

def test_login_success():
    auth_service = AuthService()  # 直接建立物件
    result = auth_service.login("user@test.com", "pass123")  # 直接呼叫方法
    assert result["ok"] is True
```

**優點**：
- 超快速（毫秒級）
- 測試精確，容易定位問題
- 適合 TDD 開發流程
- 適合 CI/CD 大量平行執行

### API Tests (`@pytest.mark.api`)
**測試對象**：HTTP endpoints（Web API 層）
**需要**：Web server 運行在 localhost:3000
**測試**：`tests/test_api_endpoints.py`

```python
import requests

def test_login_endpoint():
    response = requests.post(
        "http://localhost:3000/login",  # 真正的 HTTP 請求
        data={"username": "demo", "password": "demo"}
    )
    assert response.status_code == 302  # 測試 HTTP status code
    assert "/dashboard" in response.headers["Location"]
```

**優點**：
- 測試 HTTP layer（routing, status codes, headers）
- 測試 session 管理、cookies
- 測試安全性（CSRF, XSS 防護等）
- 更接近真實使用場景

### UI Tests (`@pytest.mark.ui`)
**測試對象**：完整的使用者流程（透過瀏覽器）
**需要**：Web server + Selenium WebDriver
**測試**：`tests/steps/test_login_ui_steps.py`

```python
from selenium import webdriver

def test_user_can_login():
    driver = webdriver.Chrome()
    driver.get("http://localhost:3000/login")
    driver.find_element(By.ID, "username").send_keys("demo")
    driver.find_element(By.ID, "password").send_keys("demo")
    driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
    assert "Dashboard" in driver.page_source
```

**優點**：
- 測試真實使用者體驗（點擊、輸入、導航）
- 測試 UI/UX（按鈕是否 disabled、錯誤訊息顯示）
- 端到端（E2E）測試
- 可測試 RWD、跨瀏覽器

### 執行速度比較

| 測試類型 | 執行時間 | 需要 Server | 測試數量建議 |
|---------|---------|------------|-------------|
| Unit    | ~0.1 秒  | ❌         | 70% (最多)   |
| API     | ~1-2 秒  | ✅         | 20%         |
| UI      | ~5-10 秒 | ✅ + Browser | 10% (最少)   |

### 面試重點

**Q1: 為什麼 Unit 測試不需要 server？**

> Unit 測試直接測試 Python 類別的業務邏輯（如 `AuthService.login()`），不經過 HTTP layer。這樣測試執行速度快、容易定位問題，符合測試金字塔原則。
> 而 API 測試則測試 HTTP endpoints（如 `POST /login`），需要啟動 Flask server，測試 routing、status codes、session 管理等 web layer 的行為。
> UI 測試則是透過 Selenium 模擬真實使用者操作瀏覽器，測試完整的使用者體驗。

**Q2: 為什麼 `test_api_endpoints.py` 不在 `tests/steps/` 目錄下？**

> `tests/steps/` 目錄是專門給 BDD (pytest-bdd) 測試使用的，裡面的測試文件都使用 `@scenario`、`@given`、`@when`、`@then` 等 pytest-bdd decorators，並對應 `features/*.feature` 的 Gherkin scenarios。
> 而 `test_api_endpoints.py` 是傳統的 pytest 測試風格，直接使用 `requests` 庫測試 HTTP endpoints，沒有使用 pytest-bdd，也沒有對應的 .feature 文件。
> 這樣的目錄結構設計讓職責更清晰：`steps/` 專門放 BDD step definitions，其他傳統 pytest 測試放在 `tests/` 根目錄下。
