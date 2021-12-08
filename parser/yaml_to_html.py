#!/usr/bin/env python

import argparse

import yaml

from oss_project import InvalidUrlStrategy, OpenSourceProjectList

parser = argparse.ArgumentParser()
parser.add_argument("yamlfilename", help="the yamlfile with the projcets")
parser.add_argument(
    "-i",
    "--invalid_url",
    help="How to handle invalid URLs in the list",
    choices=["ignore", "report", "abort"],
)
args = parser.parse_args()

with open(args.yamlfilename, "r") as yamlfile:
    try:
        yaml_content = yaml.safe_load(yamlfile)
    except yaml.YAMLError as exc:
        print("Error: Invalid yaml file:")
        print(exc)
        exit(-1)

    inv_strat = InvalidUrlStrategy.REPORT
    if args.invalid_url == "ignore":
        inv_strat = InvalidUrlStrategy.IGNORE
    elif args.invalid_url == "abort":
        inv_strat = InvalidUrlStrategy.ABORT

    projects = OpenSourceProjectList.from_yaml(
        yaml_content, invalid_url_strategy=inv_strat
    )

    projects.check_for_duplicates()

    with open("table.html", "w") as htmlfile:
        projects.write_as_html(htmlfile)

    with open("table.csv", "w") as csvfile:
        projects.write_as_csv(csvfile)
