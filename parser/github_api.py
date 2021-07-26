from datetime import datetime
from os import environ
from typing import List, Optional, Tuple
from urllib.parse import urlparse

from dateutil.parser import parse
from github import Github
from github.Tag import Tag
from github.GithubException import UnknownObjectException
from github.Repository import Repository

from utils import Activity, License, is_release_tag, sort_tags_alphanumeric

api_key = environ.get("GITHUB_API_KEY")
github_api = Github() if api_key is None else Github(api_key)


class GithubRepo:
    url: str
    repo: Repository

    def __init__(self, url: str):
        parsed_url = urlparse(url)
        assert parsed_url.netloc == "github.com"

        repo_path = parsed_url.path.rstrip("/").lstrip("/")
        if len(repo_path.split("/")) == 1:
            raise ValueError(
                "Cannot use API calls for Github organizations at the moment"
            )
        assert len(repo_path.split("/")) == 2
        repo = github_api.get_repo(repo_path)
        self.url = url
        self.repo = repo

    def get_tag_nr(self, nr: int) -> Tag:
        tags = list(self.repo.get_tags())
        release_tags = sort_tags_alphanumeric(
            filter(is_release_tag, tags),
        )
        tag = tags[nr]
        return tag

    def get_tag_activity(self, nr: int) -> Activity:
        tag = self.get_tag_nr(nr)
        # I have no clue, why you can't use tag.commit.last_modified here, but it delivers wrong values
        commit = self.repo.get_commit(tag.commit.sha)
        assert isinstance(commit.last_modified, str)
        date = parse(commit.last_modified).date()
        url = f"{self.repo.html_url}/releases/tag/{tag.name}"
        return Activity(date, url)

    def get_latest_release(self) -> Optional[Activity]:
        try:
            latest_release = self.repo.get_releases()[0]
            return Activity(latest_release.created_at.date(), latest_release.html_url)
        except IndexError:
            # sometimes stuff is only available as tag in the API
            try:
                return self.get_tag_activity(0)
            except IndexError:
                return None

    def get_first_release(self) -> Optional[Activity]:
        try:
            first_release = self.repo.get_releases()[0]
            return Activity(first_release.created_at.date(), first_release.html_url)
        except IndexError:
            # sometimes stuff is only available as tag in the API
            try:
                return self.get_tag_activity(-1)
            except IndexError:
                return None

    def get_license(self) -> Optional[License]:
        try:
            gh_license = self.repo.get_license()
            return License(gh_license.license.name, gh_license.html_url)
        except UnknownObjectException:
            # Probably no License found
            return None

    def get_last_activity(self) -> Optional[Activity]:
        last_commit = self.repo.get_commits()[0]
        date = parse(last_commit.last_modified).date()
        return Activity(date, last_commit.html_url)

    def get_languages(self) -> List[str]:
        gh_langs = self.repo.get_languages()
        lang_sum = sum(gh_langs.values())
        current_lang_sum = 0
        lang_list = []
        # Only keep the 80% most used langs here
        for lang, loc in sorted(gh_langs.items(), key=lambda itm: itm[1], reverse=True):
            lang_list.append(lang)
            current_lang_sum += loc
            if current_lang_sum / lang_sum > 0.8:
                break

        return lang_list

    def get_tags(self) -> List[str]:
        gh_topics = self.repo.get_topics()
        return gh_topics
