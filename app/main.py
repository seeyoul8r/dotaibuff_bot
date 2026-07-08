from fastapi import FastAPI

from app.api.gsi import router as gsi_router

app = FastAPI()

# Register GSI routes for live Dota 2 client updates.
app.include_router(gsi_router)
