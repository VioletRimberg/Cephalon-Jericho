import httpx
import asyncio
import logging

DEFAULT_SUCCESS_CODES = [200, 201, 202, 203, 204, 205, 206, 207, 208]
WARFRAME_API_SUCCESS_CODES = [200, 201, 202, 203, 204, 205, 206, 207, 208, 409]


class HardenedHttpClient:
    """
    A hardened HTTP client that uses the httpx library, with retry policies and timeouts.
    """

    def __init__(
        self,
        client: httpx.AsyncClient,
        success_codes: list[int] = DEFAULT_SUCCESS_CODES,
        retries: int = 5,
        wait_time: int = 1,
    ):
        self.client = client
        self.success_codes = success_codes
        self.retries = retries
        self.wait_time = wait_time

    async def get(self, url: str, **kwargs) -> httpx.Response:
        retries = 0
        while retries < self.retries:
            try:
                result = await self.client.get(url, **kwargs)
            except Exception as e:
                logging.debug(f"An error occurred while trying to GET `{url}`: {e}")
                await asyncio.sleep(self.wait_time)
                retries += 1
                continue

            if result.status_code in self.success_codes:
                return result
            else:
                await asyncio.sleep(self.wait_time)
                retries += 1
        return result

    async def post(self, url: str, **kwargs) -> httpx.Response:
        retries = 0
        while retries < self.retries:
            try:
                result = await self.client.post(url, **kwargs)
            except Exception as e:
                logging.debug(f"An error occurred while trying to POST `{url}`: {e}")
                await asyncio.sleep(self.wait_time)
                retries += 1
                continue

            if result.status_code in self.success_codes:
                return result
            else:
                await asyncio.sleep(self.wait_time)
                retries += 1
        return result
