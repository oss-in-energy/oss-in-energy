# OpenSource in Energy

A curated list of of open-source software for the energy sector

You can find the rendered table [-> here <-](https://oss-in-energy.github.io/oss-in-energy/)

## How to Contribute?

**Contributions to the list are most welcome!**
The process is quite simple: Fork this project, add the project to the [projects.yaml](projects.yaml) and create a pull request for this repository.
An entry can look as follows:

```yaml
  - name: "Example Project" # Mandatory
    repository: "https://github.com/exampleorga/exampleproject" # Mandatory
    description: "A very usefull Example Project" # Mandatory
    homepage: "http://www.example.com/" #Optional

    # The CI tries to get the following information automatically, but they can also be provided manually
    first_release: "2021-05-04"
    license: "MIT"
    languages:
      - "Rust"
      - "C++"
    tags:
      - "Cool Project"
```

## Development

### API Rate Limits

Without an API token, you can only perform a very limited number of Github API Accesses per hour.
[You can generate one](https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token) and activate it in your shell with
```bash
export GITHUB_API_KEY=ghp_asdfasdfasdf12341234asdf
```