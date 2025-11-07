from re import IGNORECASE, VERBOSE, Pattern, compile
from typing import override

from src.api.kinopoisk import KinopoiskAPI
from src.types import LinkInfo, ServiceId, ServiceName

from . import Service


class ImdbService(Service):
    def __init__(self, api: KinopoiskAPI):
        super().__init__()
        self.api: KinopoiskAPI = api

    domains: list[str] = ["imdb.com"]
    _pattern: Pattern[str] = compile(
        r"""
        (?P<service>imdb)\.com/  # Service
        (?P<type>title|name)/    # Type
        (?P<id>(tt|nm)\d{7,})    # ID
        (?:/.*)?$                # Optional trailing path
        """,
        VERBOSE | IGNORECASE,
    )
    _valid_types: list[str] = ["title"]

    @override
    async def get_external_ids(
        self, link_info: LinkInfo
    ) -> dict[ServiceName, ServiceId]:
        return await self.api.search_by_external_id(link_info.id)
