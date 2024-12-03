import asyncio
import os

import websockets
from groq import Groq

API_KEY = os.getenv("groq")

client = Groq(
    api_key=API_KEY,
)


def generategroq(promt):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": str(promt),
            }
        ],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content


async def echo(websocket):
    print("Client connected")
    try:
        async for message in websocket:
            print(f"Received from client: {message}")
            response = generategroq(message)  # ответное сообщение
            print(f"Recieved from groq: {response}")
            await websocket.send(response)  # Отправляем ответ клиенту
    except websockets.exceptions.ConnectionClosed as e:
        print("Connection closed", e)


async def main():
    async with websockets.serve(echo, "0.0.0.0", 8765):
        print("Server running on ws://0.0.0.0:8765")
        await asyncio.Future()  # Работает как вечный цикл


if __name__ == "__main__":
    asyncio.run(main())

