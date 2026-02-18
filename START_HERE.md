# 快速開始指南

## 方式 1: 只跑 API 測試（不需要 web server）

```bash
source .venv/bin/activate  # 或 .venv\Scripts\activate (Windows)
pytest -m api -v
```

✅ 這會測試 AuthService 的核心業務邏輯（登入、鎖定、錯誤處理）
✅ 3 個測試，不需要 Flask server

## 方式 2: 完整測試（API + UI）

### 步驟 1: 啟動 Flask Web Server

**Terminal 1:**
```bash
source .venv/bin/activate
python run_server.py
```

你會看到:
```
Starting Flask server on http://localhost:3000
Demo credentials:
  Username: demo
  Password: demo
```

### 步驟 2: 執行測試

**Terminal 2:**

```bash
source .venv/bin/activate

# 選項 A: 跑所有測試
pytest -v

# 選項 B: 只跑 UI 測試
pytest -m ui -v

# 選項 C: 跑 API + UI 測試
pytest -m "api or ui" -v
```

預期結果:
```
6 passed (3 API + 3 UI)
```

## 測試分類 (Markers)

專案使用 pytest markers 來分類測試:

| Marker | 測試數量 | 需要 Server | 執行指令 |
|--------|---------|------------|----------|
| `@pytest.mark.api` | 3 | ❌ 不需要 | `pytest -m api -v` |
| `@pytest.mark.ui` | 3 | ✅ 需要 | `pytest -m ui -v` |

**優點:**
- 可以只跑特定類型的測試
- CI/CD 可以分別執行（API 測試跑快速檢查，UI 測試跑完整驗證）
- 開發時不用啟動 server 也能跑 API 測試

## 方式 3: 手動測試 Web UI

1. 確保 Flask server 正在運行 (`python run_server.py`)
2. 開啟瀏覽器訪問 http://localhost:3000
3. 使用測試帳號登入:
   - Username: `demo`
   - Password: `demo`
4. 測試資安功能:
   - 輸入錯誤密碼 5 次 → 帳號會被鎖定 5 分鐘
   - 嘗試直接訪問 `/admin` 未登入 → 重導向到登入頁

## 專案特色

### ✅ API 測試 (pytest-bdd)
- 測試 `AuthService` 業務邏輯
- Gherkin scenarios: 成功登入、密碼錯誤、帳號鎖定
- 不需要外部依賴（純 Python）

### ✅ UI 測試 (Selenium + pytest-bdd)
- Page Object 模式
- 測試完整登入流程（輸入 → 點擊 → 驗證頁面）
- 測試暴力破解防護（5 次失敗 → 鎖定）
- 測試權限導向（未登入訪問 /admin → 重導向）

### ✅ 資安考量
1. **錯誤訊息不洩漏帳號存在性**
   - 不論帳號是否存在，都回傳 "Invalid email or password"

2. **暴力破解防護**
   - 5 次失敗嘗試 → 鎖定 5 分鐘
   - UI 顯示 "Account temporarily locked"
   - 登入按鈕變成 disabled 狀態

3. **權限檢查**
   - 未登入訪問受保護頁面 → 重導向到 /login
   - Session 驗證

## 故障排除

### UI 測試失敗: `ERR_CONNECTION_REFUSED`
→ Flask server 沒有運行。請在另一個 Terminal 執行 `python run_server.py`

### 測試互相干擾
→ 每個 UI 測試前會自動呼叫 `/reset-test-state` 重置狀態

### Chrome 瀏覽器問題
→ 確保已安裝 Chrome 瀏覽器（Selenium 會自動下載 ChromeDriver）

## 技術棧

- **測試框架**: pytest 9.0.2, pytest-bdd 7.2.0
- **Web 框架**: Flask 3.1.0
- **UI 測試**: Selenium 4.40.0
- **BDD**: Gherkin feature files
- **Python**: 3.11+
