import logging
import os
from typing import Literal

from async_igdb import IGDBClient
from pydantic import BaseModel, HttpUrl

from src.types import ServiceId, ServiceName

GameSourceNames = Literal[
    "Steam",
    "GOG",
    "Youtube",
    "Microsoft",
    "Apple",
    "Twitch",
    "Android",
    "Amazon",
    "Amazon Luna",
    "Amazon ADG",
    "Epic Games Store",
    "Oculus",
    "Utomik",
    "Itchio",
    "Xbox Marketplace",
    "Kartridge",
    "Playstation Store US",
    "Focus Entertainment",
    "Xbox Game Pass Ultimate Cloud",
    "GameJolt",
    "GiantBomb",
]

GameSourceIDs = Literal[
    1, 5, 10, 11, 13, 14, 15, 20, 22, 23, 26, 28, 29, 30, 31, 32, 36, 37, 54, 55, 3
]


class ExternalGameSource(BaseModel):
    id: GameSourceIDs | int
    name: GameSourceNames | str


class ExternalGame(BaseModel):
    id: int
    uid: str
    url: HttpUrl | None = None
    external_game_source: ExternalGameSource


class Game(BaseModel):
    id: int
    external_games: list[ExternalGame]
    url: HttpUrl

    @property
    def external_ids(self) -> dict[ServiceName, ServiceId]:
        return {eg.external_game_source.name: eg.uid for eg in self.external_games}


class IgdbAPI:
    def __init__(self):
        self.client_id: str | None = os.getenv("IGDB_CLIENT_ID")
        self.client_secret: str | None = os.getenv("IGDB_CLIENT_SECRET")

        if not self.client_id or not self.client_secret:
            raise ValueError(
                "IGDB_CLIENT_ID or IGDB_CLIENT_SECRET not found in environment variables."
            )

        self.client: IGDBClient = IGDBClient(
            self.client_id, client_secret=self.client_secret
        )
        self.logger: logging.Logger = logging.getLogger(__name__)

    async def connect(self):
        await self.client.__aenter__()
        self.logger.info("Connected to IGDB API.")

    async def _game_request(self, query: str) -> Game:
        response = await self.client.request(
            "games",
            fields=[
                "url",
                "external_games.url",
                "external_games.uid",
                "external_games.external_game_source.name",
            ],
            queries=[query, "limit 1"],
            # IMPORTANT: Use only double quotes in the query string
        )

        if not response:
            raise ValueError("No game found.")

        return Game(**response[0])

    async def get_external_ids_by_slug(self, slug: str) -> dict[ServiceName, ServiceId]:
        self.logger.info(f"Requesting external links for game with slug {slug!r}.")

        query = f'where slug = "{slug}"'
        game = await self._game_request(query)
        return game.external_ids | {"IGDB": f"{game.id}"}

    async def close(self):
        await self.client.__aexit__()

    async def search_by_external_service_id(
        self, game_id: str, service_source_id: GameSourceIDs
    ):
        self.logger.info(
            f"Requesting external links for game with id {game_id!r}, service {service_source_id!r}."
        )
        query = f'where external_games.uid = "{game_id}" & external_games.external_game_source = {service_source_id}'
        game = await self._game_request(query)
        return game.external_ids | {"IGDB": f"{game.id}"}
