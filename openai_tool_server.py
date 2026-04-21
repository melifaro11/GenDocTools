from __future__ import annotations

import uvicorn

from app.config import settings
from app.openapi_app import create_app


app = create_app()


def main() -> None:
    uvicorn.run(
        "openai_tool_server:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        proxy_headers=True,
    )


if __name__ == "__main__":
    main()
