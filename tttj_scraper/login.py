from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright
from rich import print


async def setup_browser_profile(
    profile_dir: Optional[str] = None,
    slow_mo_ms: int = 100,
) -> None:
    """Launch a browser for manual login to save cookies.
    
    Args:
        profile_dir: Path to store browser profile. Defaults to ./browser_data
        slow_mo_ms: Delay between actions in ms. Defaults to 100.
    """
    if not profile_dir:
        profile_dir = os.path.join(os.getcwd(), "browser_data")
    
    profile_dir = os.path.abspath(profile_dir)
    Path(profile_dir).mkdir(parents=True, exist_ok=True)

    print(f"[yellow]Browser profile will be saved to:[/yellow] {profile_dir}")
    print("\n[green]Please login to Google Maps in the browser window.[/green]")
    print("[green]The browser will close automatically after 5 minutes of inactivity.[/green]")
    print("[red]DO NOT close the browser window manually - let it timeout.[/red]")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=slow_mo_ms,
            args=['--start-maximized'],
            user_data_dir=profile_dir,
        )
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        
        # Go to Maps and wait for manual login
        await page.goto("https://www.google.com/maps", wait_until="networkidle")
        
        # Wait up to 5 minutes for manual interaction
        try:
            await page.wait_for_timeout(300000)  # 5 minutes
        except Exception:
            pass

        await browser.close()
        print("\n[green]Browser profile saved! You can now run the scraper.[/green]")


def main() -> None:
    asyncio.run(setup_browser_profile())


