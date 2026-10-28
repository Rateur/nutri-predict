from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import structlog
import logging

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

from app.api.endpoints import products, health_metrics, predict
from app.core.config import settings
from app.core.limiter import limiter


# Initialisation de l'application FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    version="0.1.0" # Version initiale SPRINT 1
)

# Configuration de slowapi (Rate Limiter)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Instrumentation Prometheus
Instrumentator().instrument(app).expose(app)


# Configuration du Middleware CORS (Restreint aux origines de confiance définies dans le .env)
allowed_origins_list = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-KEY"],
)


# Middleware personnalisé pour injecter les en-têtes HTTP de sécurité (OWASP Top 10)
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    # Exempter les pages de documentation interactive du CSP
    doc_paths = ("/docs", "/redoc", "/openapi.json")
    if not request.url.path.startswith(doc_paths):
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https://images.unsplash.com https://images.openfoodfacts.org https://fastapi.tiangolo.com; "
            "connect-src 'self' http://localhost:8000 http://127.0.0.1:8000;"
        )
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# Inclusion des routeurs
# Préfixe global paramétré dans settings.API_V1_STR ("/api/v1")
app.include_router(
    products.router,
    prefix=f"{settings.API_V1_STR}/products",
    tags=["products"]
)

app.include_router(
    health_metrics.router,
    prefix=f"{settings.API_V1_STR}/health-metrics",
    tags=["health-metrics"]
)

app.include_router(
    predict.router,
    tags=["prediction"]
)


@app.get("/")
async def root():
    """Point d'entrée de santé basique pour l'API."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "docs": f"{settings.API_V1_STR}/docs"
    }

