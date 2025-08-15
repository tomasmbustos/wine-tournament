import abc
import httpx


class MyIP(abc.ABC):
    @abc.abstractmethod
    async def get_ip(self) -> str:
        pass


class MyIPImpl(MyIP):
    async def get_ip(self) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.ipify.org", timeout=30)
            return response.text
