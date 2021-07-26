import re
from dataclasses import dataclass
from datetime import date
from typing import Optional


def sort_tags_alphanumeric( l ):
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key.name)]
    return sorted(l, key = alphanum_key)

reg = re.compile("v? ?\d+.\d+(?:.\d+)?") # simple regex to match version strings like "v1.3.4 or v 4.0 or 1.2.3"

def is_release_tag(tag):
    return reg.match(tag.name)

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
