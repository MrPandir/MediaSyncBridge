from re import IGNORECASE, VERBOSE, Pattern, compile
from typing import override

from src.api.igdb import IgdbAPI
from src.types import LinkInfo, ServiceId, ServiceName

from . import Service


class IgdbService(Service):
    def __init__(self, api: IgdbAPI):
        super().__init__()
        self.api: IgdbAPI = api

    domains: list[str] = ["igdb.com"]
    _pattern: Pattern[str] = compile(
        r"""
        (?P<service>igdb)\.com/              # Service
        (?P<type>games|platforms|companies   # Type
        |genres|engines|themes|modes|series
        |collections|characters|people)/
        (?P<id>[^/]+)                        # ID
        (?:/.*)?$                            # Optional trailing path
        """,
        VERBOSE | IGNORECASE,
    )
    _valid_types: list[str] = ["games"]

    @override
    async def get_external_ids(
        self, link_info: LinkInfo
    ) -> dict[ServiceName, ServiceId]:
        ids = await self.api.get_external_ids_by_slug(link_info.id)
        response = {"IGDB": ids["IGDB"]}

        if steam_id := ids.get("Steam"):
            response["Steam"] = steam_id

        return response
