# 🧠 Obsidian Brain MCP Server

> **"Capturing memories from the void, weaving them into a constellation of thought."**

**Obsidian Brain MCP** 是一個基於 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 的強大伺服器，旨在將您的 Obsidian 知識庫轉化為 AI 可讀、可寫、可反思的「數位大腦」。

透過整合 Microsoft 的 **MarkItDown** 與 **FastMCP** 框架，本專案實現了知識管理、多格式檔案吸入與非破壞性日記自動化的完美結合。

---

## ✨ 核心特色 (Key Features)

- **📚 知識三位一體 (The Three Pillars)**
    - **Wiki**：儲存與檢索結構化知識。
    - **Diary**：非破壞性日記自動化，支援「僅追加 (Append-only)」模式，保護每一吋記憶。
    - **Skills**：建立 AI 專用的 SOP 與通用技能庫，讓 AI 具備長期記憶與執行邏輯。
- **📄 多格式檔案吸入 (Ingestion)**
    - 整合 **MarkItDown**，支援將 PDF、Word、Excel、Powerpoint 甚至圖片一鍵轉換為 Markdown 並標記存檔。
- **🔍 深度反思 (Rethink)**
    - 具備資料夾遞迴掃描能力，能彙整大量筆記作為 AI 的思考背景進行關聯分析。
- **⚡ Vibe Coding 友善**
    - 專為 AI 共作開發模型優化，具備清晰的工具定義與易於擴展的工具集。

## 🚀 快速開始 (Quick Start)

### 1. 環境需求
- Python 3.10+ (建議使用 Conda 環境)
- [Obsidian](https://obsidian.md/) 筆記軟體

### 2. 安裝依賴
```bash
pip install -r requirements.txt
```

### 3. 設定環境變數
請在專案根目錄建立 `.env` 檔案並填入您的 Obsidian 路徑：
```env
BRAIN_PATH=/path/to/your/obsidian/brain
DIARY_PATH=/path/to/your/obsidian/diary
SKILLS_PATH=/path/to/your/obsidian/skills
```

### 4. 啟動伺服器
```bash
python brain_server.py
```

---

## 🛠️ MCP 工具集 (Tools)

| 工具 | 功能說明 |
| :--- | :--- |
| `save_knowledge` | 儲存/更新筆記，支援自動標籤與目錄分類。 |
| `read_knowledge` | 讀取特定筆記內容，支援跨路徑全局搜尋。 |
| `list_knowledge` | 列出目前知識庫與技能庫中所有檔案清單。 |
| `search_knowledge` | 全局關鍵字檢索語意相關內容。 |
| `rethink_wiki` | 彙整指定資料夾與技能庫，供 AI 進行深度反思。 |
| `create_diary` | 根據模板更新今日日記，支援智慧追加模式。 |
| `ingest_file` | 將外部檔案 (PDF/Office) 轉換為 Markdown 知識點。 |

---

## 🎨 專案哲學 (Philosophy)

此專案秉持著**「磨刀不誤砍材工」**的理念，致力於透過高品質的個人工具，解決資訊過載時代的記憶焦慮。我們不只是在儲存資料，我們是在為每個人打造專屬的「數位星系」。

---

## 🛡️ 安全與隱私 (Security & Privacy)

- **本地優先**：所有操作均在您的本地路徑執行，AI 僅根據您的指令讀取特定內容。
- **非破壞性設計**：核心工具（如 Diary）優先採用追加而非覆蓋邏輯，確保資料安全。

---

## 📄 License

MIT

---
*Created with the spirit of Vibe Coding & Innovative Intelligence.*
