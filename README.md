# 🤖 Groq Pro Chat - 高效能 AI 對話介面

一個基於 **Streamlit** 與 **Groq API** 打造的極速 AI 聊天網頁。本專案專注於提供流暢的用戶體驗，具備自動對話命名、多對話管理、自定義 UI 樣式以及對話匯出功能。

## 🌟 核心功能

* **⚡ 極速推理**：利用 Groq 雲端 LPU 推理加速，支援 Llama 3.3、Qwen 與 Gemma 等最新模型，實現毫秒級串流輸出。
* **📂 對話管理**：
    * **自動標題生成**：根據首條對話內容，自動透過 LLM 總結出 5 字以內的繁體中文標題。
    * **多對話切換**：側邊欄分頁式管理，輕鬆切換不同的討論主題。
    * **一鍵刪除**：具備歷史紀錄管理功能，隨時清理過時對話。
* **🎨 進階 UI/UX**：
    * **現代化對話氣泡**：重新定義 CSS 樣式，提供藍色系的使用者對話框與清晰的助手回覆。
    * **響應式佈局**：適配各種螢幕尺寸。
* **📥 數據安全與匯出**：
    * **Markdown 匯出**：支援將當前對話一鍵轉換為 Markdown 檔案下載，方便紀錄筆記。
    * **Session 持久化**：在單次執行期間，透過 `st.session_state` 保持對話狀態。

## 🛠️ 專案技術

* **前端/框架**：Streamlit
* **AI 推理**：Groq API (支援 Llama-3.3-70b-versatile, Qwen-2.5-32b 等)
* **環境管理**：Python `python-dotenv`

## 🚀 快速開始

### 1. 取得 API Key
前往 [Groq Cloud 控制台](https://console.groq.com/) 申請免費的 API Key。

### 2. 環境設定
在專案根目錄建立 `.env` 檔案，並填入你的 Key：
```
GROQ_API_KEY=你的_GROQ_API_KEY
```

### 3. 安裝依賴

建議使用虛擬環境進行安裝：
```
pip install streamlit groq python-dotenv
```

### 4. 啟動程式
```
streamlit run app.py
```

## 📂 專案結構
```
.
├── app.py              # 主程式邏輯、UI 介面與 CSS 樣式
├── .env                # 環境變數 (儲存 API Key)
├── README.md           # 專案說明文件
└── requirements.txt    # 套件依賴清單
```

## 📝 筆記

* **State Management**：利用 Streamlit 的關鍵字 st.session_state 解決了 Web App 無狀態性的問題，實現了類似後端資料庫的對話快取與多會話切換邏輯。

* **Asynchronous UX**：透過 stream=True 與 resp_place.markdown 實作串流輸出，極大地優化了模型生成的體感等待時間，避免 UI 阻塞。

* **Dynamic Title Logic**：在對話長度達標時觸發標題生成，透過 Prompt Engineering 確保產出的標題精簡且符合上下文語境。