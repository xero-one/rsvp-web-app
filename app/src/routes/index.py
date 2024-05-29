from fastapi import APIRouter
from src.routes.views import pages
from src.routes.v2 import index as v2

api_router = APIRouter()

# Grab all the view routes
api_router.include_router(pages.router, tags=["landing pages"])
api_router.include_router(v2.v2_router, tags=["v2"])