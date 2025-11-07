from typing import final


@final
class UnsupportedLink(Exception):
    def __init__(self, link: str):
        self.link = link
        super().__init__(f"Unsupported link {link!r}")


@final
class UnsupportedLinkType(Exception):
    def __init__(self, link: str, type: str):
        self.link = link
        self.type = type
        super().__init__(f"Unsupported link {link!r} with type {type!r}")
