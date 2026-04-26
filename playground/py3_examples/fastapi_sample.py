import asyncio
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def debug_all(request: Request, path: str = ""):
    body_raw = (await request.body()).decode("utf-8", errors="replace")
    json_body = None
    try:
        if request.headers.get("content-type", "").startswith("application/json"):
            json_body = await request.json()
    except Exception:
        pass

    result = {
        "body_raw": body_raw,
    }
    # result = {
    #     "method": request.method,
    #     "scheme": request.url.scheme,  # 显示是 http 还是 https
    #     "path": f"/{path}" if path else "/",
    #     "query_params": dict(request.query_params),
    #     "headers": dict(request.headers),
    #     "body_raw": body_raw,
    #     "json_body": json_body,
    # }
    #
    # print("\n" + "=" * 70)
    # print(f"🔧 {result['scheme'].upper()} {result['method']} {result['path']}")
    # print(f"❓ QUERY: {result['query_params']}")
    # print(f"❓ HEADERS: {result['headers']}")
    # print(f"❓ BODY: {result['body_raw']}")
    # print("=" * 70 + "\n")

    return JSONResponse(content=result)

if __name__ == "__main__":
    import sys

    async def run_servers():
        # HTTP 服务器
        http_config = uvicorn.Config(
            app, host="0.0.0.0", port=6123, log_level="critical"
        )
        http_server = uvicorn.Server(http_config)
        await http_server.serve()

        # HTTPS 服务器（需有 key.pem 和 cert.pem）
        # try:
        #     https_config = uvicorn.Config(
        #         app,
        #         host="0.0.0.0",
        #         port=6124,
        #         ssl_keyfile="key.pem",
        #         ssl_certfile="cert.pem",
        #         log_level="critical"
        #     )
        #     https_server = uvicorn.Server(https_config)
        #     print("🚀 HTTP server:  http://0.0.0.0:6123")
        #     print("🔒 HTTPS server: https://0.0.0.0:6124")
        #     await asyncio.gather(
        #         http_server.serve(),
        #         https_server.serve()
        #     )
        # except FileNotFoundError:
        #     print("⚠️  SSL files not found. Only HTTP will run.")
        #     print("   To enable HTTPS, generate key.pem and cert.pem with:")
        #     print("   openssl req -x509 -newkey rsa:4096 -nodes -keyout key.pem -out cert.pem -days 365")
        #     await http_server.serve()

    try:
        asyncio.run(run_servers())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")
        sys.exit(0)
