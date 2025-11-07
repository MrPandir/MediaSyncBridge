from contextlib import asynccontextmanager
from logging import ERROR, INFO, basicConfig, getLogger

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .api import IgdbAPI, KinopoiskAPI, ShikimoriAPI
from .exceptions import UnsupportedLink, UnsupportedLinkType
from .services import (
    IgdbService,
    ImdbService,
    KinopoiskService,
    Service,
    ShikimoriService,
    SteamService,
)
from .types import LinkInfo, ServiceId, ServiceName

igdb_api = IgdbAPI()
kinopoisk_api = KinopoiskAPI()
shikimori_api = ShikimoriAPI()

services: set[Service] = {
    IgdbService(igdb_api),
    ImdbService(kinopoisk_api),
    KinopoiskService(kinopoisk_api),
    ShikimoriService(shikimori_api),
    SteamService(igdb_api),
}


def get_service(link: str) -> tuple[Service, LinkInfo]:
    link = Service.normalize_url(link)

    for service in services:
        if link_info := service.process_link(link):
            return service, link_info
    raise UnsupportedLink(link)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await igdb_api.connect()
    yield
    await igdb_api.close()


logger = getLogger()
basicConfig(
    level=INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)-8s | %(message)s",
    datefmt="%m-%d %H:%M:%S",
)
getLogger("httpx").setLevel(ERROR)

app = FastAPI(title="MediaSyncBridge", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
)


class ResponseModel(BaseModel):
    ids: dict[ServiceName, ServiceId]
    clean_url: str
    service: ServiceName


@app.get("/get", response_model=ResponseModel)
async def get_external_ids(url: str):
    try:
        service, link_info = get_service(url)
        ids = await service.get_external_ids(link_info)
        return ResponseModel(
            ids=ids, clean_url=link_info.clean_url, service=link_info.service
        )
    except (UnsupportedLink, UnsupportedLinkType) as e:
        type = e.type if isinstance(e, UnsupportedLinkType) else None
        logger.info(
            f"Unsupported link: {e.link!r}{f' with type {type}' if type else ''}"
        )
        json = {"error": "Unsupported link", "link": e.link}
        return JSONResponse(json, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
    except ValueError as e:
        return JSONResponse({"error": e.args[0]}, status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JSONResponse({"error": e.args[0]}, status.HTTP_500_INTERNAL_SERVER_ERROR)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
