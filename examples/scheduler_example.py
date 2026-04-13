"""Scheduler example – run a periodic scrape job every N minutes."""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.scraper import WebScraper
from src.extractor import DataExtractor
from src.scheduler import Scheduler
from src.logger import setup_logger

logger = setup_logger("scheduler_example", log_file="logs/scheduler.log")

_scrape_count = 0


def scrape_job() -> None:
    """Scrape the Books to Scrape homepage and log the number of titles found."""
    global _scrape_count
    _scrape_count += 1
    logger.info("=== Scrape job #%d started ===", _scrape_count)

    scraper = WebScraper({"delay": 0.5, "retry_count": 2})
    try:
        soup = scraper.scrape_url("https://books.toscrape.com/")
        if soup is None:
            logger.error("Scrape job #%d: failed to fetch page.", _scrape_count)
            return

        extractor = DataExtractor(soup)
        titles = extractor.extract_by_css("article.product_pod h3 a", multiple=True)
        count = len(titles) if titles else 0
        logger.info("Scrape job #%d: found %d book titles.", _scrape_count, count)
        print(f"[Job #{_scrape_count}] Found {count} book titles.")
    except Exception as exc:
        logger.error("Scrape job #%d raised: %s", _scrape_count, exc)
    finally:
        scraper.close()


def main() -> None:
    """Start a scheduler that runs scrape_job every 2 minutes for a demo."""
    os.makedirs("logs", exist_ok=True)

    scheduler = Scheduler()

    # Run the job every 2 minutes (change as needed)
    job_id = scheduler.add_interval_job(scrape_job, minutes=2, job_id="book_scraper")
    logger.info("Scheduled job '%s' to run every 2 minutes.", job_id)
    print(f"Scheduler started. Job '{job_id}' will run every 2 minutes.")
    print("Press Ctrl+C to stop.\n")

    # Also schedule a daily cron job at 06:00
    cron_id = scheduler.add_cron_job(scrape_job, "0 6 * * *", job_id="book_scraper_daily")
    logger.info("Cron job '%s' scheduled at 06:00 daily.", cron_id)

    scheduler.start()

    # Run immediately once for the demo
    scrape_job()

    try:
        # Keep the process alive so the scheduler can fire
        while True:
            jobs = scheduler.get_jobs()
            print(f"\nActive jobs: {[j.id for j in jobs]}")
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received – stopping scheduler.")
    finally:
        scheduler.stop()
        logger.info("Scheduler stopped after %d total runs.", _scrape_count)
        print(f"Total scrape runs completed: {_scrape_count}")


if __name__ == "__main__":
    main()
