import re
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import date
from enum import Enum
from sys import stderr
from time import sleep
from typing import Any, Callable, Dict, List, Optional, TextIO, Tuple
from urllib.parse import urlparse

import requests
import validators
from dateutil.parser import parse

from github_api import GithubRepo, github_api
from gitlab_api import GitlabRepo
from utils import Activity, License

# TODO: ist this a good approach?
# class Category(Enum):
#     MODELING
#     SIMULATION
#     INTERFACES
#     PLATFORM
#     FORECASTING
#     STATE_ESTIMATION
#     OPTIMIZATION
#     POWER_QUALITY
#     FIRMWARE
#     ALGORITHMS


@dataclass
class OpenSourceProject:
    """Class for keeping track of an item in inventory."""

    # mandatory
    name: str
    repository: str
    description: str

    # optional
    homepage: Optional[str]

    # auto generated if not given
    license_name: Optional[License]
    languages: Optional[List[str]]
    tags: Optional[List[str]]
    first_release: Optional[Activity]

    # auto generated
    # category: str
    last_update: Optional[Activity]
    latest_release: Optional[Activity]

    # Ideas:
    # Contributors
    # CI/Coverage

    @classmethod
    def from_dict(cls, d: dict) -> "OpenSourceProject":
        def get_dict_value(
            d: Dict[str, Any], key: str, validator: Callable[[str], bool] = None
        ) -> Optional[Any]:
            if not key in d:
                return None
            val = d[key]
            if not val:
                return None
            if validator is not None:
                if not validator(val):
                    raise RuntimeError(f"{val} is not a valid value in this context")
            return val

        # Mandatory
        name = get_dict_value(d, "name")
        assert isinstance(name, str), "Project needs to have a name!"

        repository = get_dict_value(d, "repository")
        assert isinstance(repository, str), "Project needs to have a valid url!"

        repo_api: Any = None
        parsed_repo_url = urlparse(repository)
        if parsed_repo_url.netloc == "github.com":
            try:
                repo_api = GithubRepo(repository)
            except ValueError:
                repo_api = None
        else:
            try:
                repo_api = GitlabRepo(repository)
            except:
                pass

        description = get_dict_value(d, "description")
        assert isinstance(
            description, str
        ), "Project needs to have a proper description!"

        # Manual
        homepage = get_dict_value(d, "homepage", validators.url)

        # Semi autogenerated

        license_usr = get_dict_value(d, "license")
        if license_usr is None and repo_api is not None:
            license_name = repo_api.get_license()
        elif isinstance(license_usr, str):
            license_name = License(license_usr, None)
        else:
            license_name = None

        first_release_str = get_dict_value(d, "first_release")
        first_release = None
        if first_release_str is not None:
            if isinstance(first_release_str, date):
                first_release = Activity(first_release_str, None)
            else:
                first_release = Activity(parse(first_release_str).date(), None)
        elif repo_api is not None:
            first_release = repo_api.get_first_release()

        languages = get_dict_value(d, "languages")
        if languages is None:
            if repo_api is not None:
                languages = repo_api.get_languages()

        tags = get_dict_value(d, "tags")
        if tags is None:
            if repo_api is not None:
                tags = repo_api.get_tags()
            else:
                tags = []

        # Autogenerated

        last_update = None
        if repo_api is not None:
            last_update = repo_api.get_last_activity()

        latest_release = None
        if repo_api is not None:
            latest_release = repo_api.get_latest_release()

        return cls(
            name=name,
            repository=repository,
            description=description,
            homepage=homepage,
            license_name=license_name,
            languages=languages,
            tags=tags,
            # category=category,
            last_update=last_update,
            latest_release=latest_release,
            first_release=first_release,
        )

    @classmethod
    def list_headers(cls) -> List[Tuple[str, Optional[str]]]:
        return [
            ("Project", "width: 10%"),
            ("Repository URL", "width: 12.5%"),
            ("Description", "width: 20%"),
            ("Homepage", "width: 12.5%"),
            ("License", None),
            ("Languages", "width: 10%"),
            ("Tags/Topics", "width: 10%"),
            # ("Category", None),
            ("Last Update", None),
            ("Latest Release", None),
            (
                "First Release",
                None,
            ),
        ]

    def to_html_list(self) -> List[Tuple[str, Optional[str]]]:
        def simple_url(url: str) -> str:
            retval = f'<a href="{url}">{url}</a>'
            return retval

        def safe_fmt(o: Optional[Any], formatter: Callable[[Any], str]):
            if o:
                return formatter(o)
            else:
                return ""

        def fmt_list(l: List[str]) -> str:
            return ", ".join(l)

        return [
            (self.name, None),
            (safe_fmt(self.repository, simple_url), None),
            (self.description, None),
            (safe_fmt(self.homepage, simple_url), None),
            (safe_fmt(self.license_name, License.as_html), None),
            (safe_fmt(self.languages, fmt_list), None),
            (safe_fmt(self.tags, fmt_list), None),
            # (self.category, None),
            (safe_fmt(self.last_update, Activity.as_html), "text-align: center"),
            (safe_fmt(self.latest_release, Activity.as_html), "text-align: center"),
            (safe_fmt(self.first_release, Activity.as_html), "text-align: center"),
        ]

    def to_csv_list(self) -> List[str]:
        def safe_fmt(o: Optional[Any], formatter: Callable[[Any], str]):
            if o:
                return formatter(o)
            else:
                return ""

        def fmt_list(l: List[str]) -> str:
            return ", ".join(l)

        return [
            self.name,
            self.repository,
            self.description,
            safe_fmt(self.homepage, str),
            safe_fmt(self.license_name, License.as_str),
            safe_fmt(self.languages, fmt_list),
            safe_fmt(self.tags, fmt_list),
            #  self.category,
            safe_fmt(self.last_update, Activity.as_str),
            safe_fmt(self.latest_release, Activity.as_str),
            safe_fmt(self.first_release, Activity.as_str),
        ]


class InvalidUrlStrategy(Enum):
    IGNORE = 1
    ABORT = 2
    REPORT = 3


@dataclass
class OpenSourceProjectList:
    projects: Dict[str, List[OpenSourceProject]]

    @classmethod
    def from_yaml(
        cls,
        yaml_content,
        invalid_url_strategy: InvalidUrlStrategy = InvalidUrlStrategy.IGNORE,
    ) -> "OpenSourceProjectList":

        raw_project_list = []

        for category in yaml_content:
            for proj in yaml_content[category]:
                raw_project_list.append((category, proj))

        invalid_urls = None
        if (
            invalid_url_strategy == InvalidUrlStrategy.ABORT
            or invalid_url_strategy == InvalidUrlStrategy.REPORT
        ):
            invalid_urls = generate_invalid_url_list(
                list(map(lambda proj: proj[1]["repository"], raw_project_list))
            )
        if invalid_urls is not None:
            print("The following repository URLs are invalid:", file=stderr)
            for inv_url in invalid_urls:
                print(f"- {inv_url[0]} (response code {inv_url[1]})", file=stderr)
            if invalid_url_strategy == InvalidUrlStrategy.ABORT:
                raise RuntimeError("Aborting due to invalid URLs")

        with ThreadPoolExecutor(max_workers=2) as executor:
            proj_list = list(
                executor.map(
                    lambda cat_proj: (
                        cat_proj[0],
                        OpenSourceProject.from_dict(cat_proj[1]),
                    ),
                    raw_project_list,
                )
            )
        projects = defaultdict(list)
        for category, proj in proj_list:
            projects[category].append(proj)

        print(f"Successfully parsed {len(proj_list)} projects")

        print(
            f"GitHub RateLimit: remaining after {github_api.get_rate_limit().core.remaining}"
        )

        return OpenSourceProjectList(projects)

    def check_for_duplicates(self):
        projs = []
        for proj_list in self.projects.values():
            for proj in proj_list:
                projs.append(proj.name)
        if len(projs) != len(set(projs)):
            for proj in set(projs):
                projs.remove(proj)
            raise RuntimeError(f'Found duplicate projects: {", ".join(projs)}')

    def write_as_html(self, htmlfile: TextIO):
        for category in self.custom_sorted_categories():
            htmlfile.write(f"<h2>{category}</h2>\n")

            htmlfile.write(f'<table style="table-layout: fixed; width: 250%">')
            htmlfile.write(f"<thead>\n")
            htmlfile.write(f"<tr>\n")
            for header, style in OpenSourceProject.list_headers():
                if style is not None:
                    htmlfile.write(f'<th style="{style}">{header}</th>\n')
                else:
                    htmlfile.write(f"<th>{header}</th>\n")
            htmlfile.write("</tr>\n")
            htmlfile.write("</thead>\n")

            htmlfile.write('<tbody style="font-size: 15px">\n')
            for proj in self.projects_sorted(category):
                htmlfile.write(f"<tr>\n")
                for entry, style in proj.to_html_list():
                    if style is not None:
                        htmlfile.write(f'<td style="{style}">{entry}</td>\n')
                    else:
                        htmlfile.write(f"<td>{entry}</td>\n")
                htmlfile.write(f"</tr>\n")
            htmlfile.write("</tbody>\n")
            htmlfile.write("</table>\n")

    def write_as_csv(self, csvfile: TextIO):
        csvfile.write("Category;")
        for (header, html_fmt) in OpenSourceProject.list_headers():
            csvfile.write(f"{header};")
        csvfile.write("\n")

        for category in self.custom_sorted_categories():
            for proj in self.projects_sorted(category):
                csvfile.write(f"{category};")
                for entry in proj.to_csv_list():
                    csvfile.write(f"{entry.replace(';',',')};")
                csvfile.write(f"\n")

    def projects_sorted(self, category: str) -> List[OpenSourceProject]:
        def sort_projects_alphanumeric(l: List[OpenSourceProject]):
            convert = lambda text: int(text) if text.isdigit() else str.casefold(text)
            alphanum_key = lambda key: [
                convert(c) for c in re.split("([0-9]+)", key.name)
            ]
            return sorted(l, key=alphanum_key)

        return sort_projects_alphanumeric(self.projects[category])

    def custom_sorted_categories(self) -> List[str]:
        # Other category should always be at the end of the list
        categories = sorted([c for c in self.projects.keys() if "Other" not in c])
        categories.append("Other")
        return categories


def generate_invalid_url_list(url_list: List[str]) -> Optional[List[Tuple[str, int]]]:
    def do_request(url):
        retry_attempt = 0
        resp = requests.get(url)
        while resp.status_code == 429:
            print(f"Got rate-limited (response 429) for {url} - retrying", file=stderr)
            retry_attempt += 1
            sleep(2.0 * retry_attempt)
            resp = requests.get(url)
        return (url, resp.status_code)

    response_codes = []
    for i, url in enumerate(url_list):
        response_codes.append(do_request(url))

    failures = list(filter(lambda resp: resp[1] != 200, response_codes))
    if len(failures) == 0:
        return None
    return failures
