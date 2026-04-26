from fastapi import FastAPI, Request
from fastapi.responses import Response
import json
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# =====================================================
# 1. Limiter 初始化
# =====================================================
# `slowapi` 使用 "key function" 来区分不同的请求。默认是按IP地址。
# 我们将为每个限流场景自定义 key function。
# Redis 的连接信息在初始化时直接提供。
# `key_style="host"` is the crucial setting that allows sharing limits across
# different routes by preventing the endpoint path from being part of the key.
limiter = Limiter(key_func=get_remote_address, storage_uri="redis://localhost:6379/3", key_style="host")

# =====================================================
# 2. FastAPI App 初始化
# =====================================================
app = FastAPI()
# 将 limiter 实例注册到 app state 中
app.state.limiter = limiter
# 添加全局的限流异常处理器
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def log_response_body(request: Request, call_next):
    print(f"\n--- Request Headers for {request.method} {request.url.path} ---")
    for name, value in request.headers.items():
        print(f"  {name}: {value}")
    print("------------------------------------------")
    response = await call_next(request)
    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk
    
    # 打印 body, 尝试用 JSON 格式化
    log_message = f"Response Body for {request.method} {request.url.path}: "
    try:
        # For 429 responses, slowapi returns plain text
        if response.status_code == 429:
            print(log_message + response_body.decode())
        else:
            body_json = json.loads(response_body)
            print(log_message)
            print(json.dumps(body_json, indent=2, ensure_ascii=False))

    except (json.JSONDecodeError, UnicodeDecodeError):
        print(log_message + response_body.decode(errors='ignore'))

    # 因为 body_iterator 已被消耗, 需要返回一个新的 Response
    return Response(
        content=response_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type
    )


# =====================================================
# 3. 定义不同场景的限流器
# =====================================================

# 1️⃣ 全局限流 (所有接口共享)
# 定义一个 key function，它总是返回同一个字符串，这样所有请求都会累加到同一个“桶”里
def global_key_func(request: Request):
    return "GLOBAL_ALL_API"

# 2️⃣ 按“字段”限流 (例如 user-id)
def by_user_id_key_func(request: Request):
    # 例子：按请求头 user-id 限流
    return request.headers.get("user-id", "anonymous")

# =====================================================
# 4. 定义路由和应用限流
# `slowapi` 通过堆叠装饰器来应用多个限流规则
# 装饰器从下往上依次应用
# =====================================================

# 1️⃣ 单接口限流（接口级）
@app.get("/single")
@limiter.limit("10/minute", key_func=global_key_func)      # 先应用全局限流
@limiter.limit("2/minute", key_func=lambda request: "/single") # 再应用接口独立限流（所有客户端共享）
async def single_api(request: Request):
    """
    /single 自己独享 2 / min (所有客户端共享)
    同时也会计入全局的 10 / min
    """
    return {"api": "single"}


# 2️⃣ 按“字段”限流（例如 user-id）
@app.get("/per-user")
@limiter.limit("10/minute", key_func=global_key_func)     # 先应用全局限流
@limiter.limit("5/minute", key_func=by_user_id_key_func)  # 再应用按 user-id 的限流
async def per_user_api(request: Request):
    """
    同一个 user-id：5 / min
    不同 user-id：互不影响
    """
    return {"api": "per-user"}
