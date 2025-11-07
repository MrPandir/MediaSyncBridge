import logging
import os
from typing import cast

from asyncopoisk import KinopoiskAPI as AsyncKinopoiskClient
from asyncopoisk.models.model import Film, FilmSearchByFiltersResponse

from src.types import ServiceId, ServiceName


class KinopoiskAPI:
    def __init__(self):
        self.api_key: str | None = os.getenv("KINOPOISK_API_KEY")

        if not self.api_key:
            raise ValueError("KINOPOISK_API_KEY not found in environment variables.")

        self.client: AsyncKinopoiskClient = AsyncKinopoiskClient(self.api_key)
        self.logger: logging.Logger = logging.getLogger(__name__)

    async def get_external_ids(
        self, film_id: ServiceId
    ) -> dict[ServiceName, ServiceId]:
        self.logger.info(f"Requesting external links for film with ID {film_id!r}.")

        film = cast(Film | None, await self.client.films(film_id=int(film_id)))

        if not film or not film.imdb_id or not film.kinopoisk_id:
            raise ValueError(
                f"No IMDb ID or Kinopoisk ID found for film with ID {film_id!r}."
            )

        return {"IMDb": film.imdb_id, "Kinopoisk": str(film.kinopoisk_id)}

    async def search_by_external_id(self, imdb_id: ServiceId) -> dict[str, str]:
        self.logger.info(f"Searching by external ID IMDb {imdb_id!r}.")

        result = cast(
            FilmSearchByFiltersResponse | None, await self.client.films(imdb_id=imdb_id)
        )

        if not result or not result.items:
            raise ValueError(f"No film found with IMDb ID {imdb_id!r}.")

        return {
            "IMDb": str(result.items[0].imdb_id),
            "Kinopoisk": str(result.items[0].kinopoisk_id),
        }
