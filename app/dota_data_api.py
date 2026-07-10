from fastapi import FastAPI

from app.services.dota_data_service import dota_data_service


dota_data_app = FastAPI()


@dota_data_app.get('/dota-data')
async def get_dota_data():
    """Return collected Dota data."""
    return dota_data_service.get_data()
