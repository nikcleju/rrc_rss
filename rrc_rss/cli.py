"""CLI interface for rrc_rss project.

Be creative! do whatever you want!

- Install click or typer and create a CLI app
- Use builtin argparse
- Start a web application
- Import things from your .base module
"""

import argparse
import json
from omegaconf import OmegaConf
import scrapy
from scrapy.crawler import CrawlerProcess
from rrc_rss.rrc import RRCShowSpider, RRCShowListSpider
import rrc_rss.config
from rrc_rss.config import config_defaults

# Set up our specific logger
import logging
logger = logging.getLogger('RRC_RSS')
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)



def main():  # pragma: no cover
    """
    The main function executes on commands:
    `python -m rrc_rss` and `$ rrc_rss `.

    This is your program's entry point.
    """

    logger.info('Starting Radio Romania Cultural RSS generator')

    # Parse the command line arguments
    parser = argparse.ArgumentParser(description='Scrape Radio Romania Cultural shows and episodes')
    parser.add_argument('-c', '--config', type=str, default='config/config.yml', help='Path to the configuration file')
    args = parser.parse_args()

    # Merge with default configuration, set the global config object
    rrc_rss.config.config = OmegaConf.merge(
        OmegaConf.create(config_defaults),
        OmegaConf.load(args.config)
    )
    config = rrc_rss.config.config

    # Create a process and a crawler for the first spider
    process = CrawlerProcess(
        settings={
            'LOG_LEVEL': logging.WARNING,
            'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7'   # Disable a deprecated warning
            }
    )
    crawler = process.create_crawler(RRCShowListSpider)

    # Define a function to run the second spider
    def run_show_spider():
        show_urls = []

        # Read the urls from the show list in JSON lines format
        with open(config.cache.file_shows, 'r') as f:
            show_urls = [json.loads(line)['url'] for line in f]

        # Add the individual shows URL from the configuration
        show_urls.extend(config.shows.shows)

        # Add the combo shows URL from the configuration
        for combo in config.shows.combos:
            show_urls.extend(combo.urls)

        # Eliminate duplicates from the list
        show_urls = list(set(show_urls))

        # Run the Show spider to collect episodes from all the shows
        process.crawl(RRCShowSpider,
                      start_urls=show_urls,
                      do_cache=config.cache.enabled,
                      max_episodes=config.options.max_episodes,
                      min_episodes=config.options.min_episodes,
                      )

    # Connect the `run_show_spider` function to the `spider_closed` signal of the first crawler
    crawler.signals.connect(run_show_spider, signal=scrapy.signals.spider_closed)

    # Add the first crawler to the process
    process.crawl(crawler, start_urls=config.shows.showlists)

    # Start the process, and it will handle running the second spider after the first completes
    process.start()
    logger.info('Finished Radio Romania Cultural RSS generator')
