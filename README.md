# Web Crawler Application

## Overview
This application consists of three distinct docker containers working together:
A web crawler, a MongoDB database, and a REST API that provides access to the gathered information.

Upon initialization, the following sequence occurs:
1. The three containers are initialized and launched simultaneously.
2. The crawler begins extracting product catalog data from "https://urparts.com",
   storing all discovered items in the MongoDB database.
3. The FastAPI service becomes immediately accessible, though it will return partial
   results until the crawler completes its operation.

## Directory Organization
The application is divided into two main components:

```
dnl-web-scraper/
    api/ # FastAPI application code
        Dockerfile
        ...
    scraper/ # Web crawler implementation
        Dockerfile
        ...
    README.md # Setup and usage instructions
    docker-compose.yaml
    ...
```

- api: Contains the REST API implementation in Python.
- scraper: Houses the web crawler functionality in Python.
- docker-compose.yaml: Configuration file for orchestrating the multi-container setup.


## Development Instructions

The project uses `uv` for dependency management. Dependencies are defined in `pyproject.toml` using groups:

```toml
[project]
name = "my_project"
version = "0.1.0"
dependencies = []  # Keep this empty if all dependencies are in groups

[tool.uv.dependencies]
common = [
    "fastapi",
    "uvicorn",
]

app1 = [
    "sqlalchemy",
    "psycopg2",
]

app2 = [
    "pymongo",
    "redis",
]
```

### Installing `uv`

To install the `uv` package, you can use the following command:

```sh
# Using pipx
pipx install uv

# Or on macOS with Homebrew
brew install uv

# Or on Linux with curl (installs to ~/.cargo/bin/uv)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify installation with:
```sh
uv --version
```

### Adding a Package to a Specific Group
To add a package to a specific dependency group, use:

```sh
uv add --group api package_name
```

For example, to add `requests` to `scraper`:
```sh
uv add --group scraper requests
```

## Deployment Instructions

### 1. Generate `requirements.txt` for Each App
To install dependencies in Docker, we generate `requirements.txt` files for each app.

```sh
uv pip compile --group common api > requirements-api.txt
uv pip compile --group common scraper > requirements-scraper.txt
```

Optional: To regenerate `requirements.txt` with invoke in one go, make sure you have
`uv` installed with at least `invoke` from the lockfile (follow Development Instructions):

```sh
uv run invoke generate-reqs
```

Then build and run the containers as needed.

### 2. Start the apps with `docker-compose`

To launch the application (in the background), execute the following command:

`docker compose up -d` or `docker-compose up -d --build` (in case dependencies change, this forces a rebuild)

Once running, you can access the API endpoint at http://127.0.0.1:8000.
