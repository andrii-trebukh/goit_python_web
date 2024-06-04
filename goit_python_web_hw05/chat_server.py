import asyncio
from datetime import datetime
import logging
from aiofile import async_open
import websockets
from websockets import WebSocketServerProtocol
import names
from websockets.exceptions import ConnectionClosedOK
from aiopath import AsyncPath
from currency_exchange import out_for_chat

logging.basicConfig(level=logging.INFO)


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            if message.startswith("exchange"):
                message = await out_for_chat(message)
                await self.exchange_logger(ws.name, message)
            await self.send_to_clients(f"{ws.name}: {message}")

    async def exchange_logger(self, name, message):
        file_name = "exchange.log"
        apath = AsyncPath(file_name)
        async with async_open(apath, "a") as afp:
            await afp.write(f"{datetime.today()}: {name}: {message}\n")


async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, '0.0.0.0', 8080):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())
