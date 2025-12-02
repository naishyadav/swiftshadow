from asyncio import as_completed, gather
from aiohttp import ClientResponse, ClientSession, ClientTimeout
from swiftshadow.models import Proxy


async def validate_for_target(
    session: ClientSession,
    url: str,
    proxy: Proxy,
    headers: dict[str, str] = {},
    timeout: int = 2,
) -> tuple[Proxy, ClientResponse]:
    result = await session.get(
        url, headers=headers, proxy=proxy.as_string(), timeout=ClientTimeout(timeout)
    )
    return proxy, result


async def filter_on_target(
    url: str,
    proxies: list[Proxy],
    headers: dict[str, str] = {},
    timeout: int = 2,
) -> list[Proxy]:
    working: list[Proxy] = []
    async with ClientSession() as session:
        tasks = []
        for proxy in proxies:
            task = validate_for_target(
                session, url, headers=headers, proxy=proxy, timeout=timeout
            )
            tasks.append(task)

        results: list[tuple[Proxy, ClientResponse] | BaseException] = await gather(
            *tasks, return_exceptions=True
        )
        for result in results:
            if isinstance(result, BaseException):
                continue
            else:
                if result[1].status == 200:
                    working.append(result[0])
    return working


async def get_for_target(
    url: str, proxies: list[Proxy], headers: dict[str, str] = {}, timeout: int = 2
) -> Proxy | None:
    async with ClientSession() as session:
        tasks = []
        for proxy in proxies:
            task = validate_for_target(
                session, url, headers=headers, proxy=proxy, timeout=timeout
            )
            tasks.append(task)

        for task in as_completed(tasks):
            result: tuple[Proxy, ClientResponse] = await task
            if isinstance(result, BaseException):
                continue
            else:
                if result[1].status == 200:
                    return result[0]
