from re import IGNORECASE, VERBOSE, Pattern, compile
from typing import override

from src.api.kinopoisk import KinopoiskAPI
from src.types import LinkInfo, ServiceId, ServiceName

from . import Service


class KinopoiskService(Service):
    def __init__(self, api: KinopoiskAPI):
        super().__init__()
        self.api: KinopoiskAPI = api

    domains: list[str] = ["kinopoisk.ru"]
    _pattern: Pattern[str] = compile(
        r"""
        (?P<service>kinopoisk)\.ru/   # Service
        (?P<type>film|series|name)/   # Type
        (?P<id>\d+)                   # ID
        (?:/.*)?$                     # Optional trailing path
        """,
        VERBOSE | IGNORECASE,
    )
    _valid_types: list[str] = ["film", "series"]

    @override
    async def get_external_ids(
        self, link_info: LinkInfo
    ) -> dict[ServiceName, ServiceId]:
        return await self.api.get_external_ids(link_info.id)
