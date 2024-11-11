
<!-- # Python Project Template

A low dependency and really simple to start project template for Python Projects.

See also
- [Flask-Project-Template](https://github.com/rochacbruno/flask-project-template/) for a full feature Flask project including database, API, admin interface, etc.
- [FastAPI-Project-Template](https://github.com/rochacbruno/fastapi-project-template/) The base to start an openapi project featuring: SQLModel, Typer, FastAPI, JWT Token Auth, Interactive Shell, Management Commands.

### HOW TO USE THIS TEMPLATE

> **DO NOT FORK** this is meant to be used from **[Use this template](https://github.com/rochacbruno/python-project-template/generate)** feature.

1. Click on **[Use this template](https://github.com/rochacbruno/python-project-template/generate)**
3. Give a name to your project
   (e.g. `my_awesome_project` recommendation is to use all lowercase and underscores separation for repo names.)
3. Wait until the first run of CI finishes
   (Github Actions will process the template and commit to your new repo)
4. If you want [codecov](https://about.codecov.io/sign-up/) Reports and Automatic Release to [PyPI](https://pypi.org)
  On the new repository `settings->secrets` add your `PYPI_API_TOKEN` and `CODECOV_TOKEN` (get the tokens on respective websites)
4. Read the file [CONTRIBUTING.md](CONTRIBUTING.md)
5. Then clone your new project and happy coding!

> **NOTE**: **WAIT** until first CI run on github actions before cloning your new project.

### What is included on this template?

- 🖼️ Templates for starting multiple application types:
  * **Basic low dependency** Python program (default) [use this template](https://github.com/rochacbruno/python-project-template/generate)
  * **Flask** with database, admin interface, restapi and authentication [use this template](https://github.com/rochacbruno/flask-project-template/generate).
  **or Run `make init` after cloning to generate a new project based on a template.**
- 📦 A basic [setup.py](setup.py) file to provide installation, packaging and distribution for your project.
  Template uses setuptools because it's the de-facto standard for Python packages, you can run `make switch-to-poetry` later if you want.
- 🤖 A [Makefile](Makefile) with the most useful commands to install, test, lint, format and release your project.
- 📃 Documentation structure using [mkdocs](http://www.mkdocs.org)
- 💬 Auto generation of change log using **gitchangelog** to keep a HISTORY.md file automatically based on your commit history on every release.
- 🐋 A simple [Containerfile](Containerfile) to build a container image for your project.
  `Containerfile` is a more open standard for building container images than Dockerfile, you can use buildah or docker with this file.
- 🧪 Testing structure using [pytest](https://docs.pytest.org/en/latest/)
- ✅ Code linting using [flake8](https://flake8.pycqa.org/en/latest/)
- 📊 Code coverage reports using [codecov](https://about.codecov.io/sign-up/)
- 🛳️ Automatic release to [PyPI](https://pypi.org) using [twine](https://twine.readthedocs.io/en/latest/) and github actions.
- 🎯 Entry points to execute your program using `python -m <rrc_rss>` or `$ rrc_rss` with basic CLI argument parsing.
- 🔄 Continuous integration using [Github Actions](.github/workflows/) with jobs to lint, test and release your project on Linux, Mac and Windows environments.

> Curious about architectural decisions on this template? read [ABOUT_THIS_TEMPLATE.md](ABOUT_THIS_TEMPLATE.md)
> If you want to contribute to this template please open an [issue](https://github.com/rochacbruno/python-project-template/issues) or fork and send a PULL REQUEST.

[❤️ Sponsor this project](https://github.com/sponsors/rochacbruno/) -->

<!--  DELETE THE LINES ABOVE THIS AND WRITE YOUR PROJECT README BELOW -->

---
# RSS feeds for RRC shows (RRC_RSS)

[![codecov](https://codecov.io/gh/nikcleju/rrc_rss/branch/main/graph/badge.svg?token=rrc_rss_token_here)](https://codecov.io/gh/nikcleju/rrc_rss)
[![CI](https://github.com/nikcleju/rrc_rss/actions/workflows/main.yml/badge.svg)](https://github.com/nikcleju/rrc_rss/actions/workflows/main.yml)

Scraps the RRC Emisiuni webpage and creates a RSS feed for each show.

## Install it from PyPI

```bash
pip install rrc_rss
```

## Usage

```bash
$ python -m rrc_rss
#or
$ rrc_rss
```

## Podcasts

Podcast XML files are uploaded to Github Gists.

- [Idei în nocturnă - Izvoare de filozofie](https://gist.githubusercontent.com/nikcleju/6ec549decf33e80ba73705395aa07dfd/raw/xml_idei_in_nocturna_izvoare_de_filosofie.xml)
- [Idei în nocturnă - Pagini de istorie](https://gist.githubusercontent.com/nikcleju/40bfe574904083f529c92be0f20b7fd2/raw/xml_idei_in_nocturna_pagini_de_istorie.xml)
- [Texte și pretexte](https://gist.githubusercontent.com/nikcleju/5c1b96588c51261ad6ef72d315a750ab/raw/xml_texte_si_pretexte.xml)
- [Confluențe](https://gist.githubusercontent.com/nikcleju/47fa89fa73ead88bb2b92357ed1585f6/raw/xml_confluente.xml)
- [O oră cu Dana](https://gist.githubusercontent.com/nikcleju/eb862e337a3ed92697292e99043f3bcb/raw/xml_o_ora_cu_dana.xml)

<!-- ## Development

Read the [CONTRIBUTING.md](CONTRIBUTING.md) file. -->
