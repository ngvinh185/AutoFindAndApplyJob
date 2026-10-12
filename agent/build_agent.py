from deepagents import create_deep_agent
from tools.playwright_tools import mcp_tools
from tools.excel_tools import find_job, read_pending_apply, mark_ai_applied, write_excel
from agent.prompts import MAIN_AGENT_PROMPT, BROWSER_AGENT_PROMPT, EXCEL_AGENT_PROMPT
import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any
from deepagents.backends.filesystem import FilesystemBackend
from langchain_google_genai import ChatGoogleGenerativeAI
from agent.schema import BrowserOutput
from dotenv import load_dotenv
from pathlib import Path
from langchain.agents.middleware import ModelFallbackMiddleware
ROOT = Path(__file__).resolve().parents[1]      
load_dotenv(ROOT / ".env")   # D:\agent_auto_job\.env
backend = FilesystemBackend(root_dir = ROOT / "backend", virtual_mode=True)
llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash", temperature=0)

def make_fallback():
    return ModelFallbackMiddleware(
        "google_genai:gemini-3.6-flash",
        "google_genai:gemini-3.5-flash-lite",
    )
@asynccontextmanager
async def build_agent() -> AsyncGenerator[Any, None]:
    """Giữ session MCP mở trong khi agent còn được dùng."""
    async with mcp_tools() as tools_mcp:
      excel_tools = [find_job, read_pending_apply, mark_ai_applied, write_excel]
      excel_agent: dict[str, Any] = {
        "name": "excel-agent",
        "description": (
            "Quản lý file Excel danh sách job: kiểm tra job đã có trong Excel chưa, ghi dòng job mới, "
            "lấy các job người dùng muốn AI ứng tuyển (human_apply=1, ai_apply=0), "
            "và đánh dấu ai_apply=1 khi đã ứng tuyển. Không duyệt web."
        ),
        "system_prompt": EXCEL_AGENT_PROMPT,
        "tools": excel_tools,
        "middleware": [make_fallback()]
      }

      browser_agent: dict[str, Any] = {
          "name": "browser-agent",
          "description": (
              "Điều khiển trình duyệt (Playwright MCP) trên TopCV: duyệt danh sách việc làm, "
              "đọc chi tiết từng job và tóm tắt, và nộp đơn ứng tuyển khi được yêu cầu. "
              "Không làm việc với Excel."
          ),
          "system_prompt": BROWSER_AGENT_PROMPT,
          "tools": tools_mcp,
          "skills": ["/skills/"],
          "response_format": BrowserOutput,
          "middleware": [make_fallback()]
      }
      yield create_deep_agent(
          model=llm,
          middleware=[make_fallback()],
          subagents=[excel_agent, browser_agent],
          backend=backend,
          system_prompt=MAIN_AGENT_PROMPT,
      )
      
async def main() -> None:
    async with build_agent() as agent:
        # Mọi lượt hỏi dưới đây dùng chung một session Playwright MCP.
        while True:
            question = await asyncio.to_thread(input, "> ")
            if question.strip().lower() in {"exit", "quit", ""}:
                break
            result = await agent.ainvoke(
                {"messages": [{"role": "user", "content": question}]},
                config={"recursion_limit": 150},
            )
            print(result["messages"][-1].content)
 
 
if __name__ == "__main__":
    asyncio.run(main())
 