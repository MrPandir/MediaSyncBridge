import logging
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl
from shikimori import RequestError
from shikimori.client import Shikimori as AsyncShikimoriClient

from src.types import ServiceId, ServiceName

Services = Literal[
    "official_site",  # Official Site
    "wikipedia",  # Wikipedia
    "anime_news_network",  # Anime News Network
    "myanimelist",  # MyAnimeList
    "anime_db",  # AniDB
    "world_art",  # World Art
    "kinopoisk",  # KinoPoisk
    "kage_project",  # Kage Project
    "twitter",  # Twitter/X
    "smotret_anime",  # Anime 365
    "shiki",  # Shikimori
    "amediateka",  # Amediateka
    "crunchyroll",  # Crunchyroll
    "amazon",  # Amazon
    "hidive",  # Hidive
    "hulu",  # Hulu
    "ivi",  # Ivi
    "kinopoisk_hd",  # KinoPoisk HD
    "wink",  # Wink
    "netflix",  # Netflix
    "okko",  # Okko
    "youtube",  # Youtube
    "readmanga",  # ReadManga
    "mangalib",  # MangaLib
    "remanga",  # ReManga
    "mangaupdates",  # Baka-Updates
    "mangadex",  # MangaDex
    "mangafox",  # MangaFox
    "mangachan",  # Mangachan
    "mangahub",  # Mangahub
    "novel_tl",  # Novel.tl
    "ruranobe",  # RuRanobe
    "ranobelib",  # RanobeLib
    "novelupdates",  # Novel Updates
]


class ExternalLink(BaseModel):
    service: Services | str
    url: HttpUrl


class Anime(BaseModel):
    id: str
    url: HttpUrl
    name: str
    russian: str | None
    english: str | None
    japanese: str | None
    synonyms: list[str]
    external_links: list[ExternalLink] = Field(alias="externalLinks")


class ShikimoriAPI:
    def __init__(self):
        self.client: AsyncShikimoriClient = AsyncShikimoriClient(
            user_agent="MediaSyncBridge"
        )
        self.logger: logging.Logger = logging.getLogger(__name__)

    async def get_external_urls(
        self, anime_id: ServiceId
    ) -> tuple[ServiceId, dict[ServiceName, HttpUrl]]:
        self.logger.info(f"Requesting external links for anime with ID {anime_id!r}.")
        response = await self.client.graphql.animes(
            fields="""{
            id, url
            name
            russian
            english
            japanese
            synonyms

            externalLinks {
                service: kind
                url
            }}
            """,
            ids=anime_id,
        )

        if isinstance(response, RequestError):
            raise response

        animes = response["data"]["animes"]

        if not animes:
            raise ValueError(f"Anime with ID {anime_id!r} not found")

        anime = Anime(**animes[0])

        return anime.id, {el.service: el.url for el in anime.external_links}
