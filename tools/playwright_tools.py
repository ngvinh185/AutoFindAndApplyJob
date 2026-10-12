"""Tải tool từ Playwright MCP và giữ session mở suốt vòng đời của khối `async with`."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

SERVER_NAME = "playwright"

client = MultiServerMCPClient(
    {
        SERVER_NAME: {
            "command": "npx",
            "args": [
                "@playwright/mcp@latest",
                "--extension",             # điều khiển Chrome thật, giữ phiên đăng nhập
                "--image-responses=omit",  # agent dùng snapshot chữ, bỏ ảnh để giảm token
                "--timeout-settle=1000",   # chờ 1 giây sau mỗi thao tác (mặc định 500ms)
                "--timeout-action=10000",  # tối đa 10 giây cho một thao tác (mặc định 5000ms)
                # "--caps=vision",         # bỏ comment để có browser_mouse_wheel (cuộn bằng chuột)
            ],
            "transport": "stdio",
        },
    }
)


@asynccontextmanager
async def mcp_tools(
    server_name: str = SERVER_NAME,
) -> AsyncGenerator[list[BaseTool], None]:
    """Mở một session persistent tới server và trả về danh sách tool gắn với session đó.

    Mọi tool call trong khối `async with` đều đi qua CÙNG một session,
    nên trang đang mở được giữ nguyên giữa các bước (navigate, click, snapshot).
    Thoát khối thì session và subprocess được đóng.
    """
    async with client.session(server_name) as session:  # tự gọi initialize()
        tools = await load_mcp_tools(session, server_name=server_name)
        yield tools