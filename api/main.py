import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import re
from api.cheat import Cheat
from api.player import HumanPlayer

app = FastAPI()

cheat = Cheat()


@app.get("/")
async def root():
    return HTMLResponse("<html><body>Hello World</body></html>")


@app.websocket("/cheat")
async def websocket_endpoint(websocket: WebSocket):
    if cheat.all_ready:
        print("already playing")
        return

    await websocket.accept()

    try:
        # name
        data = await websocket.receive_text()
        name = re.sub(r"\s+", "", data)
        player = HumanPlayer(websocket, name)
        cheat.join(player)
        await cheat.broadcast({"message": f"Player {name} joined."})

        # ready
        await websocket.receive_text()
        player.ready_up()
        print(f"{player.name} ready")
        asyncio.create_task(cheat.start())

        while True:
            await asyncio.sleep(1)
            if cheat.playing:
                pass
                # print(f"sending {player.name} the game data")
    except WebSocketDisconnect:
        print("Failed to join cheat")
