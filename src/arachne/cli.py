"""Arachne Command Line Interface."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Annotated

import pydantic
import typer
from rich.console import Console
from rich.table import Table

from arachne.clients.http import create_client
from arachne.config.loader import GlobalConfig, SpiderConfig, load_all
from arachne.config.profile import SearchProfile
from arachne.logging import configure_logging, timestamped_log_name
from arachne.services.jobs import JobService
from arachne.services.profiles import ProfileService
from arachne.services.scraper import ScraperService
from arachne.storage.db import Database

app = typer.Typer(
    help="Arachne: A job scraping aggregator for tech company listings.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind the UI server to."),
    ui_port: int = typer.Option(5173, "--ui-port", "-u", help="Port for the Vite dev server."),
) -> None:
    """Start the Arachne UI dev server."""
    import subprocess

    console.print("[bold green]🕷️ Starting Arachne UI...[/bold green]")
    console.print(f"  UI:  http://{host}:{ui_port}/")

    try:
        # Start UI server
        ui_cmd = ["npm", "run", "dev", "--", "--port", str(ui_port), "--host", host]
        ui_process = subprocess.Popen(ui_cmd, cwd=str(Path("ui").absolute()))

        ui_process.wait()
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down services...[/yellow]")
        ui_process.terminate()


def _bootstrap(
    config_dir: Path, debug: bool = False
) -> tuple[GlobalConfig, dict[str, SpiderConfig]]:
    """Common setup for logging and configuration loading.

    Args:
        config_dir: Path to the directory containing global.yaml and spiders.yaml.
        debug: Whether to force log levels to DEBUG and enable console output.

    Returns:
        tuple[GlobalConfig, dict[str, SpiderConfig]]: Loaded global and spider configurations.
    """
    global_cfg, spiders = load_all(config_dir)
    run_stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")

    level = "DEBUG" if debug else global_cfg.logging.level

    configure_logging(
        enabled=global_cfg.logging.enabled,
        directory=global_cfg.logging.directory,
        level=level,
        central_file=timestamped_log_name(global_cfg.logging.central_file, run_stamp),
        spider_directory=str(Path(global_cfg.logging.spider_directory) / run_stamp),
        console_enabled=debug,
    )

    return global_cfg, spiders


def _do_export(
    prof: SearchProfile,
    global_cfg: GlobalConfig,
    all_spiders: dict[str, SpiderConfig],
    output: Path,
    analytics_output: Path,
    config_output: Path,
) -> None:
    """Internal helper to execute the export logic."""
    data_path = Path(global_cfg.data_dir)
    db = Database(data_path / "arachne.db")
    service = JobService(db)

    spider_names = list(all_spiders.keys())
    all_jobs = service.get_all_jobs(spider_names)

    # 1. Export Jobs
    if not all_jobs:
        console.print("[yellow]No jobs found to export.[/yellow]")
    else:
        data = [job.model_dump(mode="json") for job in all_jobs]
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(data, indent=2), encoding="utf-8")
        console.print(f"[green]Successfully exported {len(data)} jobs to {output}[/green]")

    # 2. Export Analytics
    analytics = service.get_analytics(spider_names)
    analytics_output.parent.mkdir(parents=True, exist_ok=True)
    analytics_output.write_text(json.dumps(analytics, indent=2), encoding="utf-8")
    console.print(f"[green]Successfully exported analytics to {analytics_output}[/green]")

    # 3. Export System Config
    system_config = {
        "engine": global_cfg.model_dump(mode="json"),
        "profile": prof.model_dump(mode="json"),
        "spiders": {name: cfg.model_dump(mode="json") for name, cfg in all_spiders.items()},
    }
    config_output.parent.mkdir(parents=True, exist_ok=True)
    config_output.write_text(json.dumps(system_config, indent=2), encoding="utf-8")
    console.print(f"[green]Successfully exported system configuration to {config_output}[/green]")


@app.command()
def run(
    profile: Annotated[
        str, typer.Option("--profile", "-p", help="The name of the search profile to use.")
    ] = "default",
    spiders: Annotated[
        list[str] | None,
        typer.Option(
            "--spider", "-s", help="Specific spider(s) to run. Can be used multiple times."
        ),
    ] = None,
    config: Annotated[
        Path, typer.Option("--config", "-c", help="Path to the configuration directory.")
    ] = Path("config"),
    debug: Annotated[
        bool, typer.Option("--debug", "-d", help="Enable debug logging to console.")
    ] = False,
    auto_export: Annotated[
        bool, typer.Option("--export/--no-export", help="Automatically export data after run.")
    ] = True,
) -> None:
    """Execute scraping for a specific profile and optional specific spiders.

    This command orchestrates the entire scraping pipeline: it loads configuration,
    initializes the scraping service, dispatches concurrent spider tasks, and
    displays a summary of the results.
    """
    try:
        global_cfg, all_spiders = _bootstrap(config, debug=debug)
    except pydantic.ValidationError as e:
        console.print("[red]Error: Invalid configuration found.[/red]")
        for err in e.errors():
            loc = " -> ".join(str(x) for x in err["loc"])
            console.print(f"  [bold]{loc}:[/bold] {err['msg']} (Got: {err['input']})")
        raise typer.Exit(code=1) from None

    profiles_dir = Path("profiles")
    profile_service = ProfileService(profiles_dir)

    try:
        prof = profile_service.get_profile(profile)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from None

    # Filter spiders if --spider is provided
    if spiders:
        spiders_to_run = {}
        for name in spiders:
            if name not in all_spiders:
                msg = f"[yellow]Warning:[/yellow] Spider '{name}' not found in configuration."
                console.print(msg)
                continue
            spiders_to_run[name] = all_spiders[name]

        if not spiders_to_run:
            console.print("[red]Error:[/red] No valid spiders selected.")
            raise typer.Exit(code=1)

        names_str = ", ".join(spiders_to_run.keys())
        msg = f"🚀 [bold blue]Running {names_str}[/bold blue] (Profile: [cyan]{prof.name}[/cyan])"
    else:
        spiders_to_run = all_spiders
        msg = f"🚀 [bold blue]Running all spiders[/bold blue] (Profile: [cyan]{prof.name}[/cyan])"

    console.print(msg)

    async def _run() -> None:
        data_path = Path(global_cfg.data_dir)
        db = Database(data_path / "arachne.db")

        try:
            async with create_client(
                global_cfg.timeout_seconds,
                global_cfg.user_agent,
                request_concurrency=global_cfg.request_concurrency,
            ) as client:
                scraper = ScraperService(
                    db=db,
                    client=client,
                    concurrency=global_cfg.concurrency,
                    debug=debug,
                    data_dir=str(data_path),
                )

                await scraper.run_profile(spiders_to_run, prof)

                # Summary Table
                table = Table(title=f"Scraping Results: {prof.name}")
                table.add_column("Spider", style="cyan")
                table.add_column("Status", style="bold")
                table.add_column("Found", justify="right")
                table.add_column("Filtered", justify="right")

                latest_runs = db.get_latest_spider_runs(limit=len(spiders_to_run))
                for run_data in reversed(latest_runs):
                    status = run_data["status"]
                    status_style = "[green]OK[/green]" if status == "success" else "[red]FAIL[/red]"
                    if status == "partial_failure":
                        status_style = "[yellow]WARN[/yellow]"

                    table.add_row(
                        run_data["spider"],
                        status_style,
                        str(run_data["found_count"]),
                        str(run_data["filtered_count"]),
                    )

                console.print(table)

                if auto_export:
                    console.print("\n[bold]🔄 Executing automatic export...[/bold]")
                    _do_export(
                        prof=prof,
                        global_cfg=global_cfg,
                        all_spiders=all_spiders,
                        output=data_path / "jobs.json",
                        analytics_output=data_path / "analytics.json",
                        config_output=data_path / "system_config.json",
                    )

        except (asyncio.CancelledError, KeyboardInterrupt):
            console.print("\n[yellow]⚠️ Interrupt received. Cleaning up...[/yellow]")
        except Exception as exc:
            console.print(f"[red]Fatal Error:[/red] {exc}")
            if debug:
                raise

    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        pass


@app.command()
def export(
    profile: Annotated[
        str, typer.Option("--profile", "-p", help="The name of the search profile to export.")
    ] = "default",
    output: Annotated[
        Path, typer.Option("--output", "-o", help="Path to write the jobs JSON file.")
    ] = Path("data/jobs.json"),
    analytics_output: Annotated[
        Path,
        typer.Option("--analytics-output", "-a", help="Path to write the analytics JSON file."),
    ] = Path("data/analytics.json"),
    config_output: Annotated[
        Path,
        typer.Option("--config-output", "-k", help="Path to write the system config JSON file."),
    ] = Path("data/system_config.json"),
    config: Annotated[
        Path, typer.Option("--config", "-c", help="Path to the configuration directory.")
    ] = Path("config"),
) -> None:
    """Export all jobs, analytics, and system configuration from SQLite to JSON files."""
    global_cfg, all_spiders = load_all(config)

    profiles_dir = Path("profiles")
    profile_service = ProfileService(profiles_dir)

    try:
        prof = profile_service.get_profile(profile)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from None

    _do_export(prof, global_cfg, all_spiders, output, analytics_output, config_output)


if __name__ == "__main__":
    app()
