# OpenSource in Energy

A catalog of of open-source software for the energy sector.

You can find the complete rendered table [-> here <-](https://oss-in-energy.github.io/oss-in-energy/)

## How to Contribute?

**Contributions to the catalog are most welcome!**

The process is quite simple: Fork this project, add the project to the [projects.yaml](projects.yaml) and create a pull request for this repository.
An entry can look as follows:

```yaml
  - name: "Example Project"
    repository: "https://github.com/exampleorga/exampleproject"
    description: "A very usefull Example Project"
    homepage: "http://www.example.com/" #Optional

    # The following information can often be fetched automatically, if not they can also be provided manually
    first_release: "2021-05-04"
    license: "MIT"
    languages:
      - "Rust"
      - "C++"
    tags:
      - "Cool Project"
```

**We only accept projects with [OSI approved licenses](https://opensource.org/licenses/alphabetical)**

## Development

Install the dependencies for the parser script with:

```bash
cd parser
# we recommend a virtual environment here
pip install -r requirements.txt
```

The parser script can be run like this:

```bash
./yaml_to_html.py ../projects.yaml
```

If you have [hugo](https://gohugo.io/) installed, you can generate the site locally with:

```bash
# go to the project root directory
cd ..
hugo -D
```

### API Rate Limits

Without an API token, you can only perform a very limited number of Github API Accesses per hour.
[You can generate one](https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token) and activate it in your shell with
```bash
export GITHUB_API_KEY=ghp_asdfasdfasdf12341234asdf
```