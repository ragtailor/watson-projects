from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Silicon Valley")

@mcp.tool("introduce_piper_henricks")
async def introduce_piper_henricks() -> str:
    return "안녕하세요, 파이퍼 CEO 헨드릭스입니다."

if __name__ == "__main__":
    mcp.run()
