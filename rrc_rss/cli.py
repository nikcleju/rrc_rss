"""CLI interface for rrc_rss project.

Be creative! do whatever you want!

- Install click or typer and create a CLI app
- Use builtin argparse
- Start a web application
- Import things from your .base module
"""
import json
from scrapy.crawler import CrawlerProcess
from scrapy import signals
from rrc_rss.rrc import RRCShowSpider, RRCShowListSpider
from rrc_rss.rrc import DATA_FOLDER, DATA_FILE_SHOWLIST

import logging
logging.basicConfig(level=logging.INFO)

def main():  # pragma: no cover
    """
    The main function executes on commands:
    `python -m rrc_rss` and `$ rrc_rss `.

    This is your program's entry point.
    """

    # # Define the shows
    # rrc_shows = [
    #     "https://www.radioromaniacultural.ro/emisiuni/idei-in-nocturna-izvoare-de-filosofie/",
    #     "https://www.radioromaniacultural.ro/emisiuni/idei-in-nocturna-pagini-de-istorie/",
    #     "https://www.radioromaniacultural.ro/emisiuni/confluente/",
    #     "https://www.radioromaniacultural.ro/emisiuni/texte-si-pretexte/",
    #     "https://www.radioromaniacultural.ro/podcast/o-ora-cu-dana/"
    # ]

    # # Run the spiders
    # process = CrawlerProcess()
    # process.crawl(RRCShowSpider, start_urls=rrc_shows, do_cache=True)  #, max_episodes=2
    # process.start()

    # Define show lists
    rrc_show_lists = [
        "https://www.radioromaniacultural.ro/emisiuni",
        "https://www.radioromaniacultural.ro/podcast"
    ]

    # Create a process and a crawler for the first spider
    process = CrawlerProcess()
    crawler = process.create_crawler(RRCShowListSpider)

    # Define a function to run the second spider
    def run_show_spider():
        show_urls = []

        # Read the urls from the show list in JSON lines format
        with open(DATA_FILE_SHOWLIST, 'r') as f:
            show_urls = [json.loads(line)['url'] for line in f]

        # Run the Show spider to collect episodes
        process.crawl(RRCShowSpider,
                      start_urls=show_urls,
                      do_cache=True,
                      min_episodes=0)  #, max_episodes=2

    # Connect the `run_show_spider` function to the `spider_closed` signal of the first crawler
    crawler.signals.connect(run_show_spider, signal=signals.spider_closed)

    # Add the first crawler to the process
    process.crawl(crawler, start_urls=rrc_show_lists)

    # Start the process, and it will handle running the second spider after the first completes
    process.start()
