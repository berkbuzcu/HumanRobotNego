import asyncio
import websockets

async def echo(websocket, path):
    async for message in websocket:
        print(message)

async def main():
    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    asyncio.get_event_loop().run_forever()
