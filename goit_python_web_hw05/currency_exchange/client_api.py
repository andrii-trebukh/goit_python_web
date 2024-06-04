from abc import ABC, abstractmethod
import asyncio
import aiohttp


class Fetch(ABC):
    @abstractmethod
    async def get_single_fetch(self, session: aiohttp.ClientSession, url: str):
        pass

    @abstractmethod
    async def get_fetch(self, urls: list[str]) -> list[dict]:
        pass


class PBFetch(Fetch):
    async def get_single_fetch(self, session: aiohttp.ClientSession, url: str):
        try:
            async with session.get(url) as response:
                # print("Fetching data, URL:", url)
                if response.status == 200:
                    result = await response.json()
                    return result
                print(f"Error status: {response.status} for {url}")
        except aiohttp.ClientConnectorError as err:
            print(f'Connection error: {url}', str(err))

    async def get_fetch(self, urls: list[str]) -> list[dict]:
        async with aiohttp.ClientSession() as session:
            return await asyncio.gather(
                *(self.get_single_fetch(session, url) for url in urls)
            )
