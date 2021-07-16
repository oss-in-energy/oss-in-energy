#!/usr/bin/env python

import yaml
from oss_project import OpenSourceProject

with open("../projects.yaml", "r") as stream:
    try:
        with open("table.html", "w") as htmlfile:
            data = yaml.safe_load(stream)
            for category in data:
                proj_list = []
                for p in data[category]:
                    project = OpenSourceProject.from_dict(p)
                    print(project)
                    proj_list.append(project.to_list())

                htmlfile.write(f"<h1>{category}</h1>\n")

                htmlfile.write(f'<table style="table-layout: fixed; width: 250%">')
                htmlfile.write(f'<thead>\n')
                htmlfile.write(f'<tr>\n')
                for header, style in OpenSourceProject.list_headers():
                    if style is not None:
                        htmlfile.write(f'<th style="{style}">{header}</th>\n')
                    else:
                        htmlfile.write(f"<th>{header}</th>\n")
                htmlfile.write('</tr>\n')
                htmlfile.write('</thead>\n')

                htmlfile.write('<tbody style="font-size: 15px">\n')
                for proj in proj_list:
                    htmlfile.write(f'<tr>\n')
                    for entry, style in proj:
                        if style is not None:
                            htmlfile.write(f'<td style="{style}">{entry}</td>\n')
                        else:
                            htmlfile.write(f"<td>{entry}</td>\n")
                    htmlfile.write(f'</tr>\n')
                htmlfile.write('</tbody>\n')
                htmlfile.write('</table>\n')

    except yaml.YAMLError as exc:
        print("Error: Invalid yaml file:")
        print(exc)
        exit(-1)
