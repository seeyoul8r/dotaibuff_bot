from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/gsi")
async def receive_gsi(request: Request):
    """Receive live Dota 2 data through GSI."""
    # Read raw JSON payload from the Dota 2 client.
    payload = await request.json()

    # Print only key test fields to keep console output compact.
    game_time = payload.get("map", {}).get("game_time", 0)
    hero_name = payload.get("hero", {}).get("name", "Unknown Hero")
    gold = payload.get("player", {}).get("gold", 0)

    print(f"[{game_time}s] Hero: {hero_name} | Gold: {gold}")

    # Print allplayers only when the GSI payload includes it.
    if "allplayers" in payload:
        print("--- Found allplayers field! ---")
        print(payload["allplayers"])
        print("-------------------------------")

    return {"success": True}
