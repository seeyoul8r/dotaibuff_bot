import asyncio
import logging
import os

import uvicorn


logger = logging.getLogger(__name__)


async def start_gsi():
    """Start GSI API server."""
    from app.core.config import load_server_config
    from app.main import app

    server_config = load_server_config()
    # Host/port come from env so the same code runs unchanged locally and in Docker.
    config = uvicorn.Config(app=app, host=server_config.gsi_host, port=server_config.gsi_port, log_level='info')
    server = uvicorn.Server(config)
    await server.serve()


async def start_dota_data_api():
    """Start Dota data API server."""
    from app.core.config import load_server_config
    from app.dota_data_api import dota_data_app

    server_config = load_server_config()
    # Host/port come from env so the same code runs unchanged locally and in Docker.
    config = uvicorn.Config(
        app=dota_data_app, host=server_config.dota_data_host, port=server_config.dota_data_port, log_level='info'
    )
    server = uvicorn.Server(config)
    await server.serve()


async def prepare_runtime():
    """Prepare local runtime state before services start."""
    from app.cache.redis_cache import redis_cache, redis_config
    from app.models.database import db

    await db.create_tables()
    if redis_config.clear_gsi_state_on_start:
        # Clear stale local GSI state before collecting a new test match.
        deleted = await redis_cache.clear_gsi_state()
        logger.info(f'GSI Redis state cleared: deleted={deleted}')


def main_process(): 
    """Start all local project services."""
    from app.bot.bot_instances import notify_admins
    from app.bot.main import start_admin_bot, start_bot
    from app.services.dota_data_service import dota_data_service

    with open('error_log.txt', 'a', encoding='utf-8') as output:
        output.write(f"Main process started in PID: {os.getpid()}\n")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(prepare_runtime())
    dota_data_service.set_admin_update_notifier(notify_admins)
    loop.create_task(dota_data_service.load_startup_data())
    loop.create_task(start_bot())
    loop.create_task(start_admin_bot())
    loop.create_task(start_gsi())
    loop.create_task(start_dota_data_api())
    loop.run_forever()


if __name__ == '__main__':
    main_process()
