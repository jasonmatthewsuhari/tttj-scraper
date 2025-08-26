import asyncio
import os
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright
from rich import print
from rich.prompt import Confirm

async def scrape_maps(
    search_url: str,
    max_reviews: Optional[int] = None,
    profile_dir: Optional[str] = None,
    headless: bool = False,
) -> None:
    """Interactive Google Maps scraper that handles login and data collection.
    
    Args:
        search_url: Full Google Maps search URL (e.g., https://www.google.com/maps/search/starbucks/...)
    """
    
    # Set up profile directory
    if not profile_dir:
        profile_dir = os.path.join(os.getcwd(), "browser_data")
    profile_dir = os.path.abspath(profile_dir)
    Path(profile_dir).mkdir(parents=True, exist_ok=True)

    print(f"\n[yellow]Browser profile will be saved to:[/yellow] {profile_dir}")
    print("\n[green]1. A Chrome window will open[/green]")
    print("[green]2. Please log in to Google Maps if needed[/green]")
    print("[green]3. Once logged in, close the browser window[/green]")
    print("[green]4. The scraper will then start automatically[/green]\n")

    input("Press Enter to continue...")

    async with async_playwright() as p:
        # First launch browser for login
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=False,
            args=[
                '--start-maximized',
                '--disable-blink-features=AutomationControlled',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            ],
            viewport={"width": 1920, "height": 1080},
            ignore_default_args=['--enable-automation']
        )
        page = await browser.new_page()
        
        # Go to Maps and wait for manual login
        await page.goto("https://www.google.com/maps", wait_until="networkidle")
        print("\n[yellow]Browser window opened. Please log in if needed.[/yellow]")
        print("[yellow]Close the browser window when you're done.[/yellow]\n")

        try:
            while True:
                try:
                    await page.wait_for_timeout(1000)
                except Exception:
                    break
        except Exception:
            pass

        try:
            await browser.close()  # This closes all pages and the context
        except Exception:
            pass

        print("\n[green]Login phase complete! Starting scraper...[/green]\n")

        # Now launch scraping browser
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=headless,
            args=[
                '--start-maximized',
                '--disable-blink-features=AutomationControlled',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            ],
            viewport={"width": 1920, "height": 1080},
            ignore_default_args=['--enable-automation']
        )
        page = await browser.new_page()

        # Go directly to search results
        print("\n[yellow]Loading search results...[/yellow]")
        await page.goto(search_url, wait_until="networkidle")
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(2000)  # Give time for results to load
        
        # Wait for and click the first result
        first_result = page.locator('a.hfpxzc').first
        await first_result.wait_for(state="visible", timeout=10000)
        await first_result.click()
        
        # Wait for place page to load
        await page.wait_for_load_state("networkidle")

        # Wait for title to be visible
        await page.wait_for_selector("h1.DUwDvf, h1[role='heading']", state="visible", timeout=30000)
        await page.wait_for_timeout(1000)

        # Extract basic info
        name = await page.locator("h1.DUwDvf, h1[role='heading']").text_content()
        print(f"[green]Found place:[/green] {name}")

        # Click "More reviews" button
        more_reviews_button = page.locator('button:has-text("More reviews")')
        if await more_reviews_button.count() > 0:
            await more_reviews_button.click()
            await page.wait_for_timeout(1000)

        # Sort by newest
        sort_button = page.locator("button[aria-label*='Sort reviews']")
        if await sort_button.count() > 0:
            await sort_button.click()
            await page.wait_for_timeout(500)
            newest_option = page.locator("span:text-is('Newest')")
            if await newest_option.count() > 0:
                await newest_option.click()
                await page.wait_for_timeout(1000)

        reviews = []
        while True:
            # Extract visible reviews
            review_elements = page.locator("div[data-review-id*='Ch']")
            count = await review_elements.count()
            
            for i in range(count):
                try:
                    review_el = review_elements.nth(i)
                    
                    # Skip if already processed
                    review_id = await review_el.get_attribute("data-review-id")
                    if any(r.get("review_id") == review_id for r in reviews):
                        continue
                        
                    # Click "More" button if present
                    more_button = review_el.locator('button.w8nwRe')
                    if await more_button.count() > 0:
                        await more_button.click()
                        await page.wait_for_timeout(500)

                    # Rating
                    rating_el = review_el.locator("span[aria-label*='stars']")
                    rating = None
                    if await rating_el.count() > 0:
                        rating_text = await rating_el.get_attribute("aria-label")
                        if rating_text:
                            try:
                                rating = float(rating_text.split()[0])
                            except (ValueError, IndexError):
                                pass

                    # Review text
                    text_el = review_el.locator("span[class*='text']")
                    text = await text_el.text_content() if await text_el.count() > 0 else None

                    # Date
                    date_el = review_el.locator("span:has-text('ago')")
                    date = await date_el.text_content() if await date_el.count() > 0 else None

                    # Reviewer name
                    reviewer_el = review_el.locator("div.d4r55")
                    reviewer_name = await reviewer_el.text_content() if await reviewer_el.count() > 0 else None

                    reviews.append({
                        "review_id": review_id,
                        "rating": rating,
                        "text": text.strip() if text else None,
                        "date": date.strip() if date else None,
                        "reviewer_name": reviewer_name.strip() if reviewer_name else None,
                    })

                    print(f"[green]Scraped review {len(reviews)}[/green] from {reviewer_name}")

                    if max_reviews and len(reviews) >= max_reviews:
                        print(f"\n[yellow]Reached max reviews limit ({max_reviews})[/yellow]")
                        break

                except Exception as e:
                    print(f"[red]Error parsing review:[/red] {e}")
                    continue

            if max_reviews and len(reviews) >= max_reviews:
                break

            # Scroll to load more
            try:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(1000)
                
                # Check if we've reached the end
                new_count = await review_elements.count()
                if new_count <= count:
                    print("\n[yellow]No more reviews to load[/yellow]")
                    break
                
            except Exception:
                break

        # Save results
        out_dir = Path("out")
        out_dir.mkdir(exist_ok=True)

        # Save JSON
        json_path = out_dir / "reviews.json"
        import json
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(reviews, f, ensure_ascii=False, indent=2)
        print(f"\n[green]Saved {len(reviews)} reviews to[/green] {json_path}")

        # Save CSV
        csv_path = out_dir / "reviews.csv"
        import pandas as pd
        df = pd.DataFrame(reviews)
        df.to_csv(csv_path, index=False, encoding="utf-8")
        print(f"[green]Saved CSV to[/green] {csv_path}")

def main():
    print("\n[bold]Google Maps Review Scraper[/bold]")
    print("\nThis script will:")
    print("1. Open Chrome for you to log in")
    print("2. Save your login state")
    print("3. Load search results")
    print("4. Scrape all reviews")
    print("5. Save results as JSON and CSV\n")

    # Default search URL for Starbucks locations in Singapore
    DEFAULT_URL = "https://www.google.com/maps/search/starbucks/@1.2988321,103.7848682,17z/data=!3m1!4b1?entry=ttu"
    
    search_url = input(f"Enter Maps search URL (or press Enter for default Starbucks search): ").strip()
    if not search_url:
        search_url = DEFAULT_URL
        print("[yellow]Using default Starbucks search URL[/yellow]")

    max_reviews = None
    if max_str := input("\nMax reviews to scrape (or press Enter for all): ").strip():
        try:
            max_reviews = int(max_str)
        except ValueError:
            print("[yellow]Invalid number, will scrape all reviews[/yellow]")

    asyncio.run(scrape_maps(search_url, max_reviews=max_reviews))

if __name__ == "__main__":
    main()
