from re import IGNORECASE, VERBOSE, Pattern, compile
from typing import override

from src.api.igdb import IgdbAPI
from src.types import LinkInfo, ServiceId, ServiceName

from . import Service


class SteamService(Service):
    def __init__(self, api: IgdbAPI):
        super().__init__()
        self.api: IgdbAPI = api

    domains: list[str] = ["store.steampowered.com", "steamcommunity.com"]
    _pattern: Pattern[str] = compile(
        r"""
        (store\.)?(?P<service>steam)             # Service
        (?(1)powered|community)\.com/
        (?P<type>app|bundle|sub|sharedfiles|id|  # Type
        profiles|groups|discussions|tradeoffer
        market)/
        (?P<id>\d+)                              # ID
        (?:/[^/]+)?                              # Optional slug
        (?:/.*)?$                                # Optional trailing path
        """,
        VERBOSE | IGNORECASE,
    )
    _valid_types: list[str] = ["app"]

    @override
    async def get_external_ids(
        self, link_info: LinkInfo
    ) -> dict[ServiceName, ServiceId]:
        # 1 is the Steam service id in the igdb database
        ids = await self.api.search_by_external_service_id(link_info.id, 1)
        return {"IGDB": ids["IGDB"], "Steam": ids["Steam"]}
