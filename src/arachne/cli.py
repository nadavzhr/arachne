"""Arachne Command Line Interface."""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer
from rich.console import Console
from rich.table import Table

from arachne.clients.http import create_client
from arachne.config.loader import load_all
from arachne.logging import configure_logging, timestamped_log_name
from arachne.services.jobs import JobService
from arachne.services.profiles import ProfileService
from arachne.services.scraper import ScraperService
from arachne.storage.json import JsonFileJobStorage

if TYPE_CHECKING:
    from arachne.config.loader import GlobalConfig, SourceConfig

app = typer.Typer(
    help="Arachne: A job scraping aggregator for tech company listings.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


def _bootstrap(
    config_dir: Path, debug: bool = False
) -> tuple[GlobalConfig, dict[str, SourceConfig]]:
    """Common setup for logging and config loading."""
    global_cfg, sources = load_all(config_dir)
    run_stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")

    level = "DEBUG" if debug else global_cfg.logging.level

    configure_logging(
        enabled=global_cfg.logging.enabled,
        directory=global_cfg.logging.directory,
        level=level,
        central_file=timestamped_log_name(global_cfg.logging.central_file, run_stamp),
        source_directory=str(Path(global_cfg.logging.source_directory) / run_stamp),
        console_enabled=debug,
    )

    return global_cfg, sources


@app.command()
def run(
    profile: Annotated[
        str, typer.Option("--profile", "-p", help="The name of the search profile to use.")
    ] = "default",
    sources: Annotated[
        list[str] | None,
        typer.Option(
            "--source", "-s", help="Specific source(s) to run. Can be used multiple times."
        ),
    ] = None,
    config: Annotated[
        Path, typer.Option("--config", "-c", help="Path to the configuration directory.")
    ] = Path("config"),
    debug: Annotated[
        bool, typer.Option("--debug", "-d", help="Enable debug logging to console.")
    ] = False,
) -> None:
    """Execute scraping for a specific profile and optional specific sources."""
    global_cfg, all_sources = _bootstrap(config, debug=debug)

    profiles_dir = Path("profiles")
    profile_service = ProfileService(profiles_dir)

    try:
        prof = profile_service.get_profile(profile)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from None

    # Filter sources if --source is provided
    if sources:
        sources_to_run = {}
        for name in sources:
            if name not in all_sources:
                msg = f"[yellow]Warning:[/yellow] Source '{name}' not found in configuration."
                console.print(msg)
                continue
            sources_to_run[name] = all_sources[name]

        if not sources_to_run:
            console.print("[red]Error:[/red] No valid sources selected.")
            raise typer.Exit(code=1)

        names_str = ", ".join(sources_to_run.keys())
        msg = f"🚀 [bold blue]Running {names_str}[/bold blue] (Profile: [cyan]{prof.name}[/cyan])"
    else:
        sources_to_run = all_sources
        msg = f"🚀 [bold blue]Running all sources[/bold blue] (Profile: [cyan]{prof.name}[/cyan])"

    console.print(msg)

    async def _run() -> None:
        storage = JsonFileJobStorage(Path(global_cfg.data_dir))
        async with create_client(global_cfg.timeout_seconds, global_cfg.user_agent) as client:
            scraper = ScraperService(
                storage=storage,
                client=client,
                concurrency=global_cfg.concurrency,
            )

            results = await scraper.run_profile(sources_to_run, prof)

            table = Table(title=f"Scraping Results: {prof.name}")
            table.add_column("Source", style="cyan")
            table.add_column("Status", style="bold")
            table.add_column("Found", justify="right")
            table.add_column("Filtered", justify="right")

            for name, result in results.items():
                if isinstance(result, BaseException):
                    table.add_row(name, "[red]FAILED[/red]", "-", "-")
                else:
                    status = (
                        "[green]OK[/green]"
                        if not result.normalization_error
                        else "[yellow]WARN[/yellow]"
                    )
                    table.add_row(
                        name,
                        status,
                        str(len(result.normalized)),
                        str(len(result.filtered)),
                    )

            console.print(table)

    asyncio.run(_run())


@app.command()
def profiles() -> None:
    """List all available search profiles."""
    profiles_dir = Path("profiles")
    service = ProfileService(profiles_dir)
    names = service.list_profiles()

    if not names:
        console.print("No profiles found in [bold]profiles/[/bold]")
        return

    table = Table(title="Available Profiles")
    table.add_column("Name", style="cyan")
    for name in names:
        table.add_row(name)
    console.print(table)


@app.command()
def jobs(
    source: Annotated[str | None, typer.Argument(help="Specific source to list jobs for.")] = None,
    config: Annotated[
        Path, typer.Option("--config", "-c", help="Path to config to find data_dir.")
    ] = Path("config"),
) -> None:
    """View summary of the latest scraped jobs."""
    global_cfg, _ = load_all(config)
    storage = JsonFileJobStorage(Path(global_cfg.data_dir))
    service = JobService(storage)

    # If no source provided, list all sources defined in config
    _, sources = load_all(config)
    source_names = [source] if source else list(sources.keys())

    all_jobs = service.get_all_jobs(source_names)

    if not all_jobs:
        console.print("[yellow]No jobs found in storage.[/yellow]")
        return

    table = Table(title=f"Latest Jobs ({len(all_jobs)})")
    table.add_column("Source", style="dim")
    table.add_column("Company", style="green")
    table.add_column("Title", style="bold")
    table.add_column("Location")
    table.add_column("URL", justify="center")

    for job in all_jobs[:20]:  # Limit to 20 for brevity
        # Create a terminal hyperlink if the terminal supports it
        link = f"[link={job.url}][blue]Open[/blue][/link]"
        table.add_row(job.source, job.company or "-", job.title, job.location or "-", link)

    if len(all_jobs) > 20:
        table.add_row("...", "...", f"and {len(all_jobs) - 20} more", "...", "...")

    console.print(table)


if __name__ == "__main__":
    app()
