import asyncio
import websockets
import os

IP = os.getenv("ip_server")


async def send_message(promt):
    uri = IP  # IP
    async with websockets.connect(uri) as websocket:
        while True:
            message = promt
            await websocket.send(message)  # Отправляем
            response = await websocket.recv()  # Ждем ответ
            return response

def generategroq(promt):
    requ = asyncio.run(send_message(promt))
    return requ
