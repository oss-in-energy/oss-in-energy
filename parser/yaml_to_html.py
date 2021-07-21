#!/usr/bin/env python

import argparse

import yaml

from oss_project import OpenSourceProjectList

parser = argparse.ArgumentParser()
parser.add_argument("yamlfilename", help="the yamlfile with the projcets")
args = parser.parse_args()

with open(args.yamlfilename, "r") as yamlfile:
    try:
        yaml_content = yaml.safe_load(yamlfile)
    except yaml.YAMLError as exc:
        print("Error: Invalid yaml file:")
        print(exc)
        exit(-1)

    projects = OpenSourceProjectList.from_yaml(yaml_content)

    projects.check_for_duplicates()

    with open("table.html", "w") as htmlfile:
        projects.write_as_html(htmlfile)

    with open("table.csv", "w") as csvfile:
        projects.write_as_csv(csvfile)
