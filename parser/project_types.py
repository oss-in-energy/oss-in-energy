from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Activity:
    date: date
    url: Optional[str]

    def as_html(self) -> str:
        if self.url is not None:
            retval = f'<a href="{self.url}">{self.date}</a>'
            return retval
        else:
            return str(self.date)

    def as_str(self) -> str:
        return str(self.date)

@dataclass
class License:
    name: str
    url: Optional[str]

    def as_html(self) -> str:
        if self.url is not None:
            retval = f'<a href="{self.url}">{self.name}</a>'
            return retval
        else:
            return str(self.name)

    def as_str(self) -> str:
        return str(self.name)