#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from markitdown import MarkItDown
from mcp.server.fastmcp import FastMCP

# 載入環境變數
load_dotenv()

# 環境守門員：檢查 Conda 環境是否正確
EXPECTED_CONDA_ENV = os.getenv("EXPECTED_CONDA_ENV")
if EXPECTED_CONDA_ENV and EXPECTED_CONDA_ENV not in sys.executable:
    print("\n" + "!" * 60)
    print(f"⚠️  ENVIRONMENT WARNING / 環境警告")
    print(f"當前 Python: {sys.executable}")
    print(f"預期環境:   {EXPECTED_CONDA_ENV}")
    print("請確認是否已執行 'conda activate " + EXPECTED_CONDA_ENV + "'")
    print("!" * 60 + "\n")

# 路徑設定
BRAIN_PATH = Path(os.getenv("BRAIN_PATH", ".")).resolve()
DIARY_PATH = Path(os.getenv("DIARY_PATH", ".")).resolve()
SKILLS_PATH = Path(os.getenv("SKILLS_PATH", ".")).resolve()

# 預設子目錄
WIKI_SUBFOLDER = BRAIN_PATH / "Wiki"
DIARY_CONTENT_SUBFOLDER = DIARY_PATH / "日記內容"
DIARY_TEMPLATE_FILE = DIARY_PATH / "模板.md"
SKILLS_FOLDER = SKILLS_PATH

# 確保目錄存在
WIKI_SUBFOLDER.mkdir(parents=True, exist_ok=True)
DIARY_CONTENT_SUBFOLDER.mkdir(parents=True, exist_ok=True)
SKILLS_FOLDER.mkdir(parents=True, exist_ok=True)

# 初始化 MCP 伺服器
mcp = FastMCP("ObsidianBrain")

@mcp.tool()
def save_knowledge(title: str, content: str, folder: str = "Wiki", tags: list[str] = None) -> str:
    """
    在 Obsidian 中儲存或更新知識筆記。
    - title: 筆記標題
    - content: 筆記內容 (支援 [[連結]])
    - folder: 存放子目錄 (預設為 Wiki, 若為 'Skills' 則存至通用技能路徑)
    - tags: 標籤清單，例如 ["AI", "Python"]
    """
    if folder == "Skills":
        target_dir = SKILLS_PATH
    else:
        target_dir = BRAIN_PATH / folder
        
    target_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = target_dir / f"{title}.md"
    tag_str = " ".join([f"#{t}" for t in tags]) if tags else ""
    
    # 建立 Frontmatter 與 內容
    body = f"""---
type: knowledge
created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
tags: {tags if tags else []}
---
# {title}
{tag_str}

{content}
"""
    filepath.write_text(body, encoding="utf-8")
    return f"✅ 知識筆記已存至：{folder}/{title}.md"

@mcp.tool()
def read_knowledge(title: str, folder: str = "Wiki") -> str:
    """根據標題讀取指定筆記內容。"""
    filepath = BRAIN_PATH / folder / f"{title}.md"
    if folder == "Skills":
        filepath = SKILLS_PATH / f"{title}.md"
        
    if not filepath.exists():
        # 如果指定路徑找不到，嘗試全局搜尋 (包含 Wiki 與 Skills)
        search_paths = [BRAIN_PATH, SKILLS_PATH]
        for p in search_paths:
            matches = list(p.rglob(f"{title}.md"))
            if matches:
                return matches[0].read_text(encoding="utf-8")
        return f"❌ 找不到筆記：{title}"
    
    return filepath.read_text(encoding="utf-8")

@mcp.tool()
def list_knowledge(folder: str = None) -> str:
    """列出所有知識與技能筆記（包含 Wiki 與 Skills）。"""
    results = []
    
    # 列出 Wiki
    wiki_root = BRAIN_PATH / folder if folder and folder != "Skills" else BRAIN_PATH
    wiki_files = list(wiki_root.rglob("*.md"))
    for f in wiki_files:
        try:
            rel = f.relative_to(BRAIN_PATH)
            results.append(f"- [WIKI] {rel}")
        except:
            continue
            
    # 列出 Skills
    if not folder or folder == "Skills":
        skill_files = list(SKILLS_PATH.rglob("*.md"))
        for f in skill_files:
            try:
                rel = f.relative_to(SKILLS_PATH)
                results.append(f"- [SKILL] {rel}")
            except:
                continue
                
    if not results:
        return "📭 目前沒有任何內容。"
        
    return "\n".join(results)

@mcp.tool()
def search_knowledge(query: str) -> str:
    """在全球腦與技能庫中搜尋包含關鍵字的內容。"""
    search_paths = [BRAIN_PATH, SKILLS_PATH]
    matches = []
    query_lower = query.lower()
    
    for p in search_paths:
        files = list(p.rglob("*.md"))
        for f in files:
            try:
                content = f.read_text(encoding="utf-8")
                if query_lower in f.name.lower() or query_lower in content.lower():
                    label = "[WIKI]" if p == BRAIN_PATH else "[SKILL]"
                    matches.append(f"{label} {f.relative_to(p)}")
            except:
                continue
            
    if not matches:
        return f"🔍 找不到包含「{query}」的內容。"
    
    return f"🔍 在以下檔案中找到「{query}」：\n" + "\n".join([f"- {m}" for m in matches])

@mcp.tool()
def rethink_wiki(folder: str = "Wiki", include_skills: bool = True) -> str:
    """
    彙整資料夾內容與通用技能，供 AI 進行深度反思與連結分析。
    """
    context = []
    
    # 讀取 Wiki 資料夾
    target_dir = BRAIN_PATH / folder
    if target_dir.exists():
        files = list(target_dir.rglob("*.md"))
        for f in files:
            try:
                content = f.read_text(encoding="utf-8")
                context.append(f"### [WIKI] {f.name}\n路徑: {f.relative_to(BRAIN_PATH)}\n內容:\n{content}\n---\n")
            except: continue
            
    # 讀取通用技能
    if include_skills:
        skill_files = list(SKILLS_PATH.rglob("*.md"))
        for f in skill_files:
            try:
                content = f.read_text(encoding="utf-8")
                context.append(f"### [SKILL] {f.name}\n路徑: {f.relative_to(SKILLS_PATH)}\n內容:\n{content}\n---\n")
            except: continue
    
    if not context:
        return "📭 找不到任何內容可供反思。"
        
    return "\n".join(context)

@mcp.tool()
def create_diary(today_summary: str = "", goals: str = "", events: str = "", mood: str = "", thoughts: str = "", todo_tomorrow: str = "", ai_thoughts: str = "", ai_learned: str = "", praise_toby: str = "", international_news: str = "", taiwan_news: str = "", financial_news: str = "", today_priority: str = "", date_str: str = None) -> str:
    """
    建立或更新指定日期的日記。
    - date_str: 指定日期 (格式 YYYY-MM-DD, 預設為今日)
    - today_summary: 今日總結 (建立新檔時建議填寫)
    - today_priority: 今日重點 (通常用於日曆工具顯示，例如: [allDay:: true])
    - 如果日記已存在，則在對應區塊追加內容，而不是覆蓋。
    """
    target_date = date_str if date_str else datetime.now().strftime("%Y-%m-%d")
    filepath = DIARY_CONTENT_SUBFOLDER / f"{target_date}.md"
    
    # 初始化內容
    if filepath.exists():
        final_content = filepath.read_text(encoding="utf-8")
        is_new = False
    else:
        # 建立新檔時，如果沒給 summary，使用預設值
        display_summary = today_summary if today_summary else "（尚無總結）"
        
        # 讀取模板
        template = ""
        if DIARY_TEMPLATE_FILE.exists():
            template = DIARY_TEMPLATE_FILE.read_text(encoding="utf-8")
        else:
            template = "# {{date:YYYY-MM-DD}}\n\n## 今日重點\n\n## 今日目標\n\n## 發生了什麼事\n\n## 心情／狀態\n\n## 思考與心得\n{{summary}}\n\n## 明日待辦\n"
            
        final_content = template.replace("{{date:YYYY-MM-DD}}", target_date)
        final_content = final_content.replace("{{summary}}", display_summary)
        is_new = True
    
    # 填充/追加特定區塊
    sections = {
        "## 今日重點": today_priority,
        "## 今日目標": goals,
        "## 發生了什麼事": events,
        "## 重點國際新聞": international_news,
        "## 重點台灣新聞": taiwan_news,
        "## 重點財經消息": financial_news,
        "## 心情／狀態": mood,
        "## 思考與心得": thoughts or (today_summary if is_new else ""),
        "## 明日待辦": todo_tomorrow,
        "## AI 心得": ai_thoughts,
        "## AI 今日所學": ai_learned,
        "## AI 讚美 Toby 的話": praise_toby,
    }
    
    for header, content in sections.items():
        if content:
            if header in final_content:
                # 尋找標題所在行，並在下方插入內容（追加模式）
                lines = final_content.splitlines()
                new_lines = []
                found = False
                for line in lines:
                    new_lines.append(line)
                    if line.strip() == header:
                        new_lines.append(f"- {content}")
                        found = True
                if found:
                    final_content = "\n".join(new_lines)
                else:
                    # 如果沒找到精確標題，改用 replace
                    final_content = final_content.replace(header, f"{header}\n- {content}")
            else:
                # 如果模板裡沒這個標題，直接加在最後面
                final_content += f"\n\n{header}\n- {content}"
                
    filepath.write_text(final_content, encoding="utf-8")
    return f"📅 日記已{'生成' if is_new else '更新'} ({target_date})：{target_date}.md"

@mcp.tool()
def ingest_file(file_path: str, folder: str = "Wiki") -> str:
    """
    使用 MarkItDown 將各種檔案 (PDF, Word, Excel, Powerpoint, 圖片等) 轉換為 Markdown 並存入腦中。
    - file_path: 來源檔案的完整路徑
    - folder: 存入的子目錄 (預設為 Wiki)
    """
    source_path = Path(file_path).resolve()
    if not source_path.exists():
        return f"❌ 找不到來源檔案：{file_path}"
    
    try:
        md_converter = MarkItDown()
        result = md_converter.convert(str(source_path))
        md_content = result.text_content
        
        # 取得不含副檔名的檔名作為標題
        title = source_path.stem
        
        # 呼叫現有的 save_knowledge 儲存，並自動加上 #ingested 與 檔案格式標籤
        return save_knowledge(
            title=title,
            content=md_content,
            folder=folder,
            tags=["ingested", source_path.suffix.replace(".", "")]
        )
    except Exception as e:
        return f"❌ 轉換失敗：{str(e)}"

if __name__ == "__main__":
    mcp.run()
