from fastapi import APIRouter, HTTPException, Request

from app.services.client_link_service import client_link_service
from app.services.match_service import match_service

router = APIRouter()


@router.post("/gsi")
async def receive_gsi(request: Request):
    """Receive live Dota 2 data through GSI."""
    # Read raw JSON payload from the Dota 2 client.
    payload = await request.json()
    token = payload['auth']['token']
    user_id = await client_link_service.get_user_by_token(token)
    if user_id is None:
        # Reject snapshots that are not linked to a Telegram user.
        raise HTTPException(status_code=403, detail='Unknown GSI token')

    # Pass linked user snapshot to the match service and keep endpoint thin.
    await match_service.process_snapshot(user_id, payload)

    return {"success": True}
