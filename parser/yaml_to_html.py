#!/usr/bin/env python

import yaml

from oss_project import OpenSourceProjectList

with open("../projects.yaml", "r") as stream:
    try:
        yaml_content = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print("Error: Invalid yaml file:")
        print(exc)
        exit(-1)

    projects = OpenSourceProjectList.from_yaml(yaml_content)
    with open("table.html", "w") as htmlfile:
        projects.write_as_html(htmlfile)
