#!/usr/bin/env python

from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import yaml

from oss_project import OpenSourceProject

with open("../projects.yaml", "r") as stream:
    try:
        with open("table.html", "w") as htmlfile:
            yaml_content = yaml.safe_load(stream)

            raw_project_list = []

            for category in yaml_content:
                for proj in yaml_content[category]:
                    raw_project_list.append((category, proj))

            with ThreadPoolExecutor() as executor:
                proj_list = executor.map(
                    lambda cat_proj: (
                        cat_proj[0],
                        OpenSourceProject.from_dict(cat_proj[1]),
                    ),
                    raw_project_list,
                )
            projects = defaultdict(list)
            for category, proj in proj_list:
                projects[category].append(proj)

            for category in projects.keys():
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
                for proj in sorted(projects[category], key= lambda proj: proj.name):
                    htmlfile.write(f"<tr>\n")
                    for entry, style in proj.to_list():
                        if style is not None:
                            htmlfile.write(f'<td style="{style}">{entry}</td>\n')
                        else:
                            htmlfile.write(f"<td>{entry}</td>\n")
                    htmlfile.write(f"</tr>\n")
                htmlfile.write("</tbody>\n")
                htmlfile.write("</table>\n")

    except yaml.YAMLError as exc:
        print("Error: Invalid yaml file:")
        print(exc)
        exit(-1)
