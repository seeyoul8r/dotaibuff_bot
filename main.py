from fastapi import FastAPI, Request

app = FastAPI()


@app.post("/gsi")
async def receive_gsi(request: Request):
    """Получает live-данные Dota 2 через GSI."""
    # Получаем сырой JSON от игры
    payload = await request.json()

    # Выводим в консоль только самое важное для теста, чтобы не спамить
    game_time = payload.get("map", {}).get("game_time", 0)
    hero_name = payload.get("hero", {}).get("name", "Unknown Hero")
    gold = payload.get("player", {}).get("gold", 0)

    print(f"[{game_time}s] Hero: {hero_name} | Gold: {gold}")

    # Проверяем наличие allplayers для теста данных других игроков
    if "allplayers" in payload:
        print("--- Найдено поле allplayers! ---")
        print(payload["allplayers"])
        print("-------------------------------")

    return {"success": True}
