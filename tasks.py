from invoke import Context, task


@task
def run_lint(ctx: Context) -> None:
    """Run ruff to check and format the codebase."""
    ctx.run("uv run ruff format .")
    ctx.run("uv run ruff check . --fix")


@task
def run_tests(ctx: Context) -> None:
    """Run all tests with coverage."""
    ctx.run("uv run pytest --cov")
    # ctx.run("uv run coverage report -m")


@task(pre=[run_lint, run_tests])
def run_all(ctx: Context) -> None:
    """Run both linting and tests."""
    run_lint(ctx)
    run_tests(ctx)


@task
def generate_reqs(ctx: Context) -> None:
    """
    Generate separate requirements.txt files for each application using uv.
    """
    ctx.run(
        "uv export --only-group common --only-group api > api/requirements-api.txt",
        pty=True,
    )
    print("✅ requirements-api.txt generated.")

    ctx.run(
        "uv export --only-group common --only-group scraper"
        " > scraper/requirements-scraper.txt",
        pty=True,
    )
    print("✅ requirements-scraper.txt generated.")

    print("🎉 All requirements files have been successfully generated.")
