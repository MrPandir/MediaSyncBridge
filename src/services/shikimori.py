from logging import getLogger
from re import IGNORECASE, VERBOSE, Pattern, compile
from typing import override

from src.api.shikimori import ShikimoriAPI
from src.types import LinkInfo, ServiceId, ServiceName

from . import Service
from .kinopoisk import KinopoiskService

logger = getLogger(__name__)


class ShikimoriService(Service):
    def __init__(self, api: ShikimoriAPI):
        super().__init__()
        self.api: ShikimoriAPI = api

    domains: list[str] = ["shikimori.one", "shikimori.me"]
    _pattern: Pattern[str] = compile(
        r"""
        (?P<service>shikimori)\.(one|me)/  # Service
        (?P<type>animes|mangas|ranobe      # Type
        |characters|people|clubs)/
        [a-z]?                             # Optional prefix
        (?P<id>\d+)                        # ID
        (?:-[^/]+)?                        # Optional slug
        (?:/.*)?$                          # Optional trailing path
        """,
        VERBOSE | IGNORECASE,
    )
    _valid_types: list[str] = ["animes"]

    @override
    async def get_external_ids(
        self, link_info: LinkInfo
    ) -> dict[ServiceName, ServiceId]:
        shikimori_id, external_urls = await self.api.get_external_urls(link_info.id)

        response = {"Shikimori": shikimori_id}

        kinopoisk_url = external_urls.get("kinopoisk")
        if not kinopoisk_url:
            logger.warning(f"ShikimoriService: No kinopoisk URL found for {link_info}")
            return response

        kinopoisk_link_info = KinopoiskService.process_link(str(kinopoisk_url))
        if not kinopoisk_link_info:
            logger.warning(
                f"ShikimoriService: Not detected pattern for {kinopoisk_url!r} in {link_info}"
            )
            return response

        return response | {"Kinopoisk": kinopoisk_link_info.id}
