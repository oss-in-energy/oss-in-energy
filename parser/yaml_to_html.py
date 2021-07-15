#!/usr/bin/env python

import yaml
from oss_project import OpenSourceProject
from tabulate import tabulate

with open("../projects.yaml", "r") as stream:
    try:
        with open("table.html", "w") as htmlfile:
            # htmlfile.write("<!DOCTYPE html>\n")
            # htmlfile.write("<html>\n")
            # htmlfile.write(
            #     '<head>\n\
            #     <link rel="stylesheet" type="text/css" href="table.css">\n\
            #     </head>\n'
            # )
            data = yaml.safe_load(stream)
            for category in data:
                proj_list = []
                for p in data[category]:
                    project = OpenSourceProject.from_dict(p)
                    print(project)
                    proj_list.append(project.to_list())
                htmlfile.write(f"<h1>{category}</h1>\n")
                htmlfile.write(
                    tabulate(
                        proj_list,
                        tablefmt="unsafehtml",
                        headers=OpenSourceProject.list_headers(),
                    )
                )
            # htmlfile.write("</html>\n")

    except yaml.YAMLError as exc:
        print("Error: Invalid yaml file:")
        print(exc)
        exit(-1)
