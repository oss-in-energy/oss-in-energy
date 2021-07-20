from datetime import datetime

# from os import environ
from typing import List, Optional, Tuple
from urllib.parse import urlparse

from dateutil.parser import parse

from project_types import Activity, License
from gitlab import Gitlab
from gitlab.exceptions import GitlabGetError, GitlabHttpError
from gitlab.v4.objects.projects import Project
import re

def sort_tags_alphanumeric( l ):
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key.name)]
    return sorted(l, key = alphanum_key)

reg = re.compile("v? ?\d+.\d+(?:.\d+)?") # simple regex to match version strings like "v1.3.4 or v 4.0 or 1.2.3"

def is_release_tag(tag):
    return reg.match(tag.name)

class GitlabRepo:
    url: str
    repo: Project

    def __init__(self, url: str):
        parsed_url = urlparse(url)

        repo_path = parsed_url.path.rstrip("/").lstrip("/")

        try:
            gl = Gitlab(parsed_url.scheme + "://" + parsed_url.netloc)
            repo = gl.projects.get(repo_path)
        except (GitlabGetError, GitlabHttpError):
            print(f"Warning: {url} doesn't seem to be a Gitlab repository")
            return None

        self.url = url
        self.repo = repo


    def get_latest_release(self) -> Optional[Activity]:
        try:
            latest_release = self.repo.releases.list()[-1]
            return Activity(latest_release.created_at.date(), latest_release.html_url)
        except (AttributeError, IndexError):
            try:
                tags = self.repo.tags.list()
                release_tags = sort_tags_alphanumeric(
                    filter(is_release_tag, self.repo.tags.list()),
                )
                date = parse(release_tags[-1].commit["created_at"]).date()
                return Activity(date, f"{self.url}/-/tags/{release_tags[-1].name}")
            except (AttributeError, IndexError):
                return None

    def get_first_release(self) -> Optional[Activity]:
        try:
            latest_release = self.repo.releases.list()[0]
            return Activity(latest_release.created_at.date(), latest_release.html_url)
        except (AttributeError, IndexError):
            try:
                tags = self.repo.tags.list()
                release_tags = sort_tags_alphanumeric(
                    filter(is_release_tag, self.repo.tags.list()),
                )
                date = parse(release_tags[0].commit["created_at"]).date()
                return Activity(date, f"{self.url}/-/tags/{release_tags[0].name}")
            except (AttributeError, IndexError):
                return None

    def get_license(self) -> Optional[License]:
        # TODO: I don't get how a license can be queried from the gitlab API.
        # According to https://docs.gitlab.com/ee/api/projects.html it should be
        # some property but this didn't work for any of the projects I tried...
        return None

    def get_last_activity(self) -> Optional[Activity]:
        try:
            # We could alternatively use the `last_activity_at` property, but then we won't have a url
            last_commit = self.repo.commits.list()[0]
            date = parse(last_commit.created_at).date()
            return Activity(date, last_commit.web_url)
        except AttributeError:
            return None

    def get_languages(self) -> List[str]:
        gl_langs = self.repo.languages()
        current_lang_sum = 0
        lang_list = []
        # Only keep the 80% most used langs here
        for lang, loc in sorted(gl_langs.items(), key=lambda itm: itm[1], reverse=True):
            lang_list.append(lang)
            current_lang_sum += loc
            if current_lang_sum > 0.8:
                break

        return lang_list

    def get_tags(self) -> List[str]:
        try:
            gl_topics = self.repo.tag_list
            return gl_topics
        except AttributeError:
            return []
