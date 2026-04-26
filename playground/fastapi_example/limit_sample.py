import redis.asyncio as redis
from fastapi import FastAPI, Depends, Request
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

async def global_identifier(_: Request):
    return "GLOBAL_ALL_API"


app = FastAPI(
    dependencies=[
        Depends(
            RateLimiter(
                times=10,  # 全服务 10 次
                seconds=60,  # 每 60 秒
                identifier=global_identifier,
            )
        )
    ]
)

# =====================================================
# Redis 初始化（所有进程共享）
# =====================================================
@app.on_event("startup")
async def startup():
    r = redis.from_url(
        "redis://localhost:6379/3",
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(r, prefix="test_prefix")


# =====================================================
# 1️⃣ 全局限流（所有接口共享）
# =====================================================
# The faulty middleware was replaced by injecting the rate limiter as a
# global dependency into the FastAPI app, which is the correct approach.


# =====================================================
# 2️⃣ 单接口限流（接口级）
# =====================================================
@app.get(
    "/single",
    dependencies=[Depends(RateLimiter(times=2, seconds=60))]
)
async def single_api():
    """
    /single 自己独享 2 / min
    """
    return {"api": "single"}


# =====================================================
# 3️⃣ 组合接口共享限流（a / b 一组）
# =====================================================
async def group_ab(_: Request):
    return "GROUP_AB"


@app.get(
    "/a",
    dependencies=[Depends(RateLimiter(times=5, seconds=60, identifier=group_ab))]
)
async def api_a():
    """
    /a + /b 共享 5 / min
    """
    return {"api": "a"}


@app.get(
    "/b",
    dependencies=[Depends(RateLimiter(times=5, seconds=60, identifier=group_ab))]
)
async def api_b():
    return {"api": "b"}


# =====================================================
# 4️⃣ 单接口按“字段”限流（例如 user-id）
# =====================================================
async def by_user_id(request: Request):
    # 例子：按请求头 user-id 限流
    return request.headers.get("user-id", "anonymous")


@app.get(
    "/per-user",
    dependencies=[Depends(RateLimiter(times=5, seconds=60, identifier=by_user_id))]
)
async def per_user_api():
    """
    同一个 user-id：5 / min
    不同 user-id：互不影响
    """
    return {"api": "per-user"}

