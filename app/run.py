import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from settings import limiter
from src.routes.index import api_router
from args import env
from config import ( 
    DEV_PORT,
    DEV_HOST,
    PROD_HOST,
    PROD_PORT,
    DOMAIN,
    ROOT_DIR,
    origins,
    FASTAPI_LOG_CONFIG              
)
from db.context import ddb
from db.init import generate_tables as init_db



app = FastAPI(
    title="DesignBytes",
    description=""
)
# Add rate limiter, to prevent false traffic abuse
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# Mount static directory containing all static/asset files
app.mount("/assets", StaticFiles(directory="src/assets"), name="assets")
# Connect all routes
app.include_router(api_router)
# Redirect all 404 routes
@app.exception_handler(404)
async def custom_404_handler(_, __):
    return RedirectResponse("/")


# Create essential db tables
init_db(ddb=ddb())



if __name__ == "__main__":
    _reload = False if env == "production" else True
    uvicorn.run(
        "run:app",
        host=PROD_HOST if env == "production" else DEV_HOST,
        port=int(PROD_PORT) if env == "production" else int(DEV_PORT),
        log_level="debug",
        log_config=FASTAPI_LOG_CONFIG,
        reload=_reload,
        reload_dirs=ROOT_DIR
    )
    
