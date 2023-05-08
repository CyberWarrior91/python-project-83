### Hexlet tests and linter status:
[![Actions Status](https://github.com/CyberWarrior91/python-project-83/workflows/hexlet-check/badge.svg)](https://github.com/CyberWarrior91/python-project-83/actions)
[![Github Actions Status](https://github.com/hexlet-boilerplates/python-package/workflows/Python%20CI/badge.svg)](https://github.com/hexlet-boilerplates/python-package/actions)
<a href="https://codeclimate.com/github/CyberWarrior91/python-project-83/maintainability"><img src="https://api.codeclimate.com/v1/badges/f68ae08f4417ed9b5230/maintainability" /></a>

## Getting started

**Description:**

This is a Page Analyzer application. It analyzes URL and shows it's basic SEO info.
You can see how it works by clicking on this <a href="https://python-project-83-production-615a.up.railway.app/">link</a>

## Usage

#### Clone the repository using this command:
```git clone https://github.com/CyberWarrior91/python-project-83.git```

**Requirements:**
 
 This app works on Flask framework and uses Gunicorn as WSGI Web server, so you need to get them installed, as well as other dependencies:
 
* python = >=3.8.1
* gunicorn = ^20.1.0
* flask = ^2.2.3
* python-dotenv = ^1.0.0
* psycopg2-binary = ^2.9.6
* validators = ^0.20.0
* requests = ^2.30.0
* bs4 = ^0.0.1

In addition, you need to have your *DATABASE_URL* and *SECRET_KEY* environment variables specified for both development and production environment in order to this application to start

## Makefile

In order to use commands from Makefile, you need to have **poetry** installed

Firstly, check your current pip version and upgrade it, if needed:

```python -m pip --version```

```python -m pip install --upgrade pip```

Then install Poetry via this link:

[Poetry installation](https://python-poetry.org/docs/)

After successful installation, you need to initiate new poetry package using this command:

```poetry init```

### Makefile commands:

```make install``` install poetry packages

```make dev``` starts the app on the local server in the development environment

```make start``` start the app in the production environment
