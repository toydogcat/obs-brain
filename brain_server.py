#!/home/toymsi/miniconda3/envs/ai-brain/bin/python
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from markitdown import MarkItDown
from mcp.server.fastmcp import FastMCP

# 載入環境變數
load_dotenv()

# 路徑設定
BRAIN_PATH = Path(os.getenv("BRAIN_PATH", ".")).resolve()
DIARY_PATH = Path(os.getenv("DIARY_PATH", ".")).resolve()

# 預設子目錄
WIKI_SUBFOLDER = BRAIN_PATH / "Wiki"
DIARY_CONTENT_SUBFOLDER = DIARY_PATH / "日記內容"
DIARY_TEMPLATE_FILE = DIARY_PATH / "模板.md"

# 確保目錄存在
WIKI_SUBFOLDER.mkdir(parents=True, exist_ok=True)
DIARY_CONTENT_SUBFOLDER.mkdir(parents=True, exist_ok=True)

# 初始化 MCP 伺服器
mcp = FastMCP("ObsidianBrain")

@mcp.tool()
def save_knowledge(title: str, content: str, folder: str = "Wiki", tags: list[str] = None) -> str:
    """
    在 Obsidian 中儲存或更新知識筆記。
    - title: 筆記標題
    - content: 筆記內容 (支援 [[連結]])
    - folder: 存放子目錄 (預設為 Wiki)
    - tags: 標籤清單，例如 ["AI", "Python"]
    """
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
    if not filepath.exists():
        # 如果指定路徑找不到，嘗試全局搜尋
        matches = list(BRAIN_PATH.rglob(f"{title}.md"))
        if matches:
            filepath = matches[0]
        else:
            return f"❌ 找不到筆記：{title}"
    
    return filepath.read_text(encoding="utf-8")

@mcp.tool()
def list_knowledge(folder: str = None) -> str:
    """列出所有知識筆記（可選子目錄）。"""
    root = BRAIN_PATH / folder if folder else BRAIN_PATH
    files = list(root.rglob("*.md"))
    if not files:
        return "📭 目前沒有任何筆記。"
    
    result = []
    for f in files:
        try:
            rel_path = f.relative_to(BRAIN_PATH)
            result.append(f"- {rel_path}")
        except ValueError:
            result.append(f"- {f.name} (外連檔案)")
    
    return "\n".join(result)

@mcp.tool()
def search_knowledge(query: str) -> str:
    """在全球腦中搜尋包含關鍵字的筆記（標題或內容）。"""
    files = list(BRAIN_PATH.rglob("*.md"))
    matches = []
    query_lower = query.lower()
    
    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
            if query_lower in f.name.lower() or query_lower in content.lower():
                matches.append(str(f.relative_to(BRAIN_PATH)))
        except:
            continue
            
    if not matches:
        return f"🔍 找不到包含「{query}」的內容。"
    
    return f"🔍 在以下檔案中找到「{query}」：\n" + "\n".join([f"- {m}" for m in matches])

@mcp.tool()
def rethink_wiki(folder: str = "Wiki") -> str:
    """
    讀取整個資料夾的所有筆記內容，彙整成大型上下文供 AI 進行反思與連結分析。
    """
    target_dir = BRAIN_PATH / folder
    if not target_dir.exists():
        return f"❌ 資料夾不存在：{folder}"
    
    files = list(target_dir.rglob("*.md"))
    context = []
    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
            context.append(f"### 檔案名稱: {f.name}\n路徑: {f.relative_to(BRAIN_PATH)}\n內容:\n{content}\n---\n")
        except:
            continue
    
    if not context:
        return "📭 資料夾內無 Markdown 檔案。"
        
    return "\n".join(context)

@mcp.tool()
def create_diary(today_summary: str, goals: str = "", events: str = "", mood: str = "", thoughts: str = "", todo_tomorrow: str = "", ai_thoughts: str = "", ai_learned: str = "", praise_toby: str = "") -> str:
    """
    建立或更新今日日記。
    - today_summary: 今日總結 (必填)
    - 如果日記已存在，則在對應區塊追加內容，而不是覆蓋。
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    filepath = DIARY_CONTENT_SUBFOLDER / f"{today_str}.md"
    
    # 初始化內容
    if filepath.exists():
        final_content = filepath.read_text(encoding="utf-8")
        is_new = False
    else:
        # 讀取模板
        template = ""
        if DIARY_TEMPLATE_FILE.exists():
            template = DIARY_TEMPLATE_FILE.read_text(encoding="utf-8")
        else:
            template = "# {{date:YYYY-MM-DD}}\n\n## 今日總結\n{{summary}}"
            
        final_content = template.replace("{{date:YYYY-MM-DD}}", today_str)
        final_content = final_content.replace("{{summary}}", today_summary)
        is_new = True
    
    # 填充/追加特定區塊
    sections = {
        "## 今日目標": goals,
        "## 發生了什麼事": events,
        "## 心情／狀態": mood,
        "## 思考與心得": thoughts or (today_summary if is_new else ""),
        "## 明日待辦": todo_tomorrow,
        "## AI 心得": ai_thoughts,
        "## AI 今日所學": ai_learned,
        "## AI 讚美 Toby 的話": praise_toby,
        "## 今日重點": "", # 保留標題
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
    return f"📅 今日日記已{'生成' if is_new else '更新'}：{today_str}.md"
            
    filepath.write_text(final_content, encoding="utf-8")
    return f"📅 今日日記已生成：{today_str}.md"

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
