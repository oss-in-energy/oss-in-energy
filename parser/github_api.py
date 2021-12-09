from datetime import datetime, timezone
from os import environ
from typing import List, Optional, Tuple
from urllib.parse import urlparse

from dateutil.parser import parse
from github import Github
from github.GithubException import UnknownObjectException
from github.GitRelease import GitRelease
from github.Repository import Repository
from github.Tag import Tag

from utils import Activity, License, is_release_tag, sort_tags_alphanumeric

api_key = environ.get("GITHUB_API_KEY")
github_api = Github() if api_key is None else Github(api_key)
print(f"GitHub rate limit: remaining {github_api.get_rate_limit().core.remaining}")
print(
    f"Resets in {round((github_api.get_rate_limit().core.reset.replace(tzinfo=timezone.utc) - datetime.now(timezone.utc)).seconds / 60, 1)} Minutes"
)


class GithubRepo:
    url: str
    repo: Repository
    taglist = Optional[List[Tuple[datetime, Tag]]]
    releases = Optional[List[GitRelease]]

    def __init__(self, url: str):
        parsed_url = urlparse(url)
        assert parsed_url.netloc == "github.com"

        repo_path = parsed_url.path.rstrip("/").lstrip("/")
        if len(repo_path.split("/")) == 1:
            raise ValueError(
                "Cannot use API calls for Github organizations at the moment"
            )
        assert len(repo_path.split("/")) == 2
        try:
            repo = github_api.get_repo(repo_path)
        except UnknownObjectException:
            # invalid url
            raise ValueError(
                f"Cannot open github repo {url}"
            )
        self.url = url
        self.repo = repo
        self.create_sorted_taglist()
        try:
            self.releases = self.repo.get_releases()
        except IndexError:
            self.releases = None

    def create_sorted_taglist(self):
        # This is a workaround, as the last_modified property in the taglist is buggy. See https://github.com/PyGithub/PyGithub/issues/1642
        tags = self.repo.get_tags().get_page(0)
        if len(tags) >= 30:
            tags += self.repo.get_tags().get_page(-1)
        if len(tags) > 8:
            # To save API calls, we only use the first and last tags by alphanumeric string
            alpha_tags = sort_tags_alphanumeric(filter(is_release_tag, tags))
            tags = alpha_tags[0:2] + alpha_tags[-2:]
        date_by_commit_list = [(parse(t.commit.stats.last_modified), t) for t in tags]
        self.taglist = sorted(date_by_commit_list, key=lambda dt: dt[0])

    def get_latest_release(self) -> Optional[Activity]:
        latest_tag = None
        latest_tag_activity = None
        try:
            latest_tag = self.taglist[-1]
            url = f"{self.repo.html_url}/releases/tag/{latest_tag[1].name}"
            latest_tag_activity = Activity(latest_tag[0].date(), url)
        except IndexError:
            pass

        latest_release = None
        latest_release_activity = None
        try:
            latest_release = self.releases[0]
            latest_release_activity = Activity(
                latest_release.created_at.date(), latest_release.html_url
            )
        except IndexError:
            pass

        if latest_release is not None and latest_tag is not None:
            if latest_release.created_at > latest_tag[0].replace(tzinfo=None):
                return latest_release_activity
            else:
                return latest_tag_activity
        elif latest_release is not None and latest_tag is None:
            return latest_release_activity
        elif latest_release is None and latest_tag is not None:
            return latest_tag_activity
        else:
            return None

    def get_first_release(self) -> Optional[Activity]:
        first_tag = None
        first_tag_activity = None
        try:
            first_tag = self.taglist[0]
            url = f"{self.repo.html_url}/releases/tag/{first_tag[1].name}"
            first_tag_activity = Activity(first_tag[0].date(), url)
        except IndexError:
            pass

        first_release = None
        first_release_activity = None
        try:
            first_release = self.releases[0]
            first_release_activity = Activity(
                first_release.created_at.date(), first_release.html_url
            )
        except IndexError:
            pass

        if first_release is not None and first_tag is not None:
            if first_release.created_at < first_tag[0].replace(tzinfo=None):
                return first_release_activity
            else:
                return first_tag_activity
        elif first_release is not None and first_tag is None:
            return first_release_activity
        elif first_release is None and first_tag is not None:
            return first_tag_activity
        else:
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
