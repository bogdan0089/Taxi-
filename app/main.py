from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logger import logger
from app.core.exceptions import BaseAppException
from app.routers.auth_router.auth_router import router as auth_router
from app.routers.user_router.user_router import router as user_router
from app.routers.trip_router.trip_router import router as trip_router
from app.routers.rating_router.rating_router import router as rating_router
from app.routers.admin_router.admin_router import router as admin_router
from app.routers.payment_router.payment_router import router as payment_router


app = FastAPI(title="Uber Clone API")


@app.middleware("http")
async def log_request(request: Request, call_next):
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} → {response.status_code}")
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(BaseAppException)
async def app_exception_handler(_request: Request, exc: BaseAppException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(trip_router)
app.include_router(rating_router)
app.include_router(admin_router)
app.include_router(payment_router)
