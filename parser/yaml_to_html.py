#!/usr/bin/env python

import argparse
from sys import stderr

import yaml

from oss_project import (InvalidUrlStrategy, OpenSourceProjectList,
                         RawOpenSourceProjectList)

parser = argparse.ArgumentParser()
parser.add_argument("yamlfilename", help="the yamlfile with the projcets")
parser.add_argument(
    "-i",
    "--invalid_url",
    help="How to handle invalid URLs in the list (default: report)",
    choices=["report", "abort"],
)
validation_opts = parser.add_mutually_exclusive_group()
validation_opts.add_argument(
    "--validate-only",
    help="Only validate the list but don't create csv/html",
    action="store_true",
)
validation_opts.add_argument(
    "--skip-validation",
    help="Skip the validation of the URLs. Saves time when the list is valid but a failure in the list results in a crash",
    action="store_true",
)
args = parser.parse_args()

with open(args.yamlfilename, "r") as yamlfile:
    try:
        yaml_content = yaml.safe_load(yamlfile)
    except yaml.YAMLError as exc:
        print("Error: Invalid yaml file:")
        print(exc)
        exit(-1)

    valid = True

    inv_strat = InvalidUrlStrategy.REPORT
    if args.invalid_url == "abort":
        inv_strat = InvalidUrlStrategy.ABORT

    raw_project_list = RawOpenSourceProjectList.from_yaml(yaml_content)

    if not args.skip_validation:
        if raw_project_list.contains_duplicates():
            valid = False
            if inv_strat == InvalidUrlStrategy.ABORT:
                print("Aborting due to duplicate Projects", file=stderr)
                exit(-1)

        if (
            not raw_project_list.repo_urls_are_valid()
            or not raw_project_list.homepage_urls_are_valid()
        ):
            valid = False
            if inv_strat == InvalidUrlStrategy.ABORT:
                print("Aborting due to invalid URLs", file=stderr)
                exit(-1)

    if args.validate_only:
        if valid:
            exit(0)
        else:
            exit(-1)

    projects = OpenSourceProjectList.from_raw_list(raw_project_list)

    with open("table.html", "w") as htmlfile:
        projects.write_as_html(htmlfile)

    with open("table.csv", "w") as csvfile:
        projects.write_as_csv(csvfile)
