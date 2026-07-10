import asyncio
import os
from concurrent.futures import ProcessPoolExecutor

import uvicorn

from app.bot.main import start_admin_bot, start_bot
from app.cache.redis_cache import redis_cache, redis_config
from app.dota_data_api import dota_data_app
from app.main import app
from app.models.database import db
from app.services.dota_data_service import dota_data_service


async def start_gsi():
    """Start local GSI API server."""
    # Run FastAPI server inside the same local event loop.
    config = uvicorn.Config(app=app, host='127.0.0.1', port=8000, log_level='info')
    server = uvicorn.Server(config)
    await server.serve()


async def start_dota_data_api():
    """Start local Dota data API server."""
    # Run Dota data API on a separate local port.
    config = uvicorn.Config(app=dota_data_app, host='127.0.0.1', port=8001, log_level='info')
    server = uvicorn.Server(config)
    await server.serve()


async def prepare_runtime():
    """Prepare local runtime state before services start."""
    await db.create_tables()
    if redis_config.clear_gsi_state_on_start:
        # Clear stale local GSI state before collecting a new test match.
        deleted = await redis_cache.clear_gsi_state()
        print(f'GSI Redis state cleared: deleted={deleted}')


def main_process(): 
    """Start all local project services."""
    with open('error_log.txt', 'a', encoding='utf-8') as output:
        output.write(f"Main process started in PID: {os.getpid()}\n")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(prepare_runtime())
    loop.create_task(dota_data_service.start_daily_update())
    loop.create_task(start_bot())
    loop.create_task(start_admin_bot())
    loop.create_task(start_gsi())
    loop.create_task(start_dota_data_api())
    loop.run_forever()


if __name__ == '__main__':
    with ProcessPoolExecutor(max_workers=1) as executor:
        executor.submit(main_process)
