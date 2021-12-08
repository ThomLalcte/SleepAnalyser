#!/usr/bin/env python

import asyncio
from websockets import serve

async def echo(websocket,e):
    async for message in websocket:
        await websocket.send("Monkey")

async def main():
    async with serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever

asyncio.run(main())