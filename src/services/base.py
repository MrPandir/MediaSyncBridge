from abc import ABC
from re import Pattern

from ..exceptions import UnsupportedLinkType
from ..types import LinkInfo, ServiceId, ServiceName


class Service(ABC):
    domains: list[str]
    """List of domains associated with the service. The first element is used as a standard for a clean link."""
    _pattern: Pattern[str]
    """Regex pattern to match the service URLs."""
    _valid_types: list[str]
    """List of valid link types for the service."""

    def __init__(self):
        if not self.domains:
            raise NotImplementedError("domains must be set")
        if not self._pattern:
            raise NotImplementedError("_pattern must be set")
        if not self._valid_types:
            raise NotImplementedError("_valid_types must be set")

    async def get_external_ids(
        self, link_info: LinkInfo
    ) -> dict[ServiceName, ServiceId]:
        """Fetch external IDs."""
        raise NotImplementedError(
            "Implement this method to fetch external IDs in service."
        )

    @staticmethod
    def normalize_url(link: str) -> str:
        """Add https:// scheme to the link if no scheme is present and convert to lowercase."""
        if not link.startswith(("http://", "https://")):
            return "https://" + link.lower()
        return link.lower()

    @classmethod
    def process_link(cls, link: str) -> LinkInfo | None:
        """Process a link and return structured information or None if no match."""
        match = cls._pattern.search(link)
        if not match:
            return None

        gd = match.groupdict()

        link_type = gd["type"]
        if link_type not in cls._valid_types:
            raise UnsupportedLinkType(link, link_type)

        return LinkInfo(
            service=gd["service"],
            clean_url=f"https://{cls.domains[0]}/{link_type}/{gd['id']}",
            type=link_type,
            id=gd["id"],
        )
