from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Optional

import typer
from rich import print

from .exporters import export_json, export_csv_reviews
from .login import setup_browser_profile
from .models import PlaceResult
from .scraper import GoogleMapsScraper


cli = typer.Typer(
    name="tttj-scraper",
    help="Google Maps place info and reviews scraper",
    add_completion=False,
)


@cli.command()
def login(
    profile_dir: str = typer.Option(
        None,
        help="Directory to store browser profile (default: ./browser_data)",
    ),
    slow_mo: int = typer.Option(
        100,
        help="Delay between actions in milliseconds",
    ),
):
    """Launch a browser for manual login to save cookies.
    
    The browser will stay open for 5 minutes to allow manual login,
    then close automatically. The profile will be saved and used
    for subsequent scraping runs.
    """
    asyncio.run(setup_browser_profile(profile_dir, slow_mo))


@cli.command()
def scrape(
    place_url: Optional[str] = typer.Option(None, help="Google Maps place URL"),
    query: Optional[str] = typer.Option(None, help="Search query (e.g., 'coffee')"),
    location: Optional[str] = typer.Option(None, help="Location to bias search (e.g., 'New York, NY')"),
    max_reviews: Optional[int] = typer.Option(None, help="Maximum number of reviews to fetch (default: all)"),
    headful: bool = typer.Option(False, help="Run browser non-headless for debugging"),
    out: str = typer.Option("out/place.json", help="Path to write JSON output"),
    csv: bool = typer.Option(False, help="Also export reviews as CSV"),
):
    """Scrape a place's info and reviews from Google Maps.
    
    Supports fetching by URL or search query + location. Reviews are sorted newest first.
    """

    if not place_url and not query:
        raise typer.BadParameter("Provide either --place-url or --query")

    async def _run() -> None:
        # Use saved browser profile if available
        profile_dir = os.path.abspath(os.path.join(os.getcwd(), "browser_data"))
        if not os.path.exists(profile_dir):
            print("[yellow]Warning: No browser profile found. Run 'login' command first to set up authentication.[/yellow]")
            profile_dir = None

        async with GoogleMapsScraper(
            headless=not headful,
            user_data_dir=profile_dir,
        ) as scraper:
            if place_url:
                result: PlaceResult = await scraper.get_place_by_url(place_url, max_reviews=max_reviews)
            else:
                result = await scraper.get_place_by_search(query=query or "", location=location, max_reviews=max_reviews)
        
        # Always export JSON
        export_json(result.model_dump(), out)
        print(f"[green]Wrote JSON:[/green] {out}")

        # Optionally export reviews CSV
        if csv and result.reviews:
            csv_path = str(Path(out).with_suffix(".csv"))
            export_csv_reviews([r.model_dump() for r in result.reviews], csv_path)
            print(f"[green]Wrote CSV:[/green] {csv_path}")

    asyncio.run(_run())


def main() -> None:
    typer.run(scrape)


if __name__ == "__main__":
    main()


