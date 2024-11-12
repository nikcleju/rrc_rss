"""CLI interface for rrc_rss project.

Be creative! do whatever you want!

- Install click or typer and create a CLI app
- Use builtin argparse
- Start a web application
- Import things from your .base module
"""

import dotenv
from scrapy.crawler import CrawlerProcess

from rrc_rss.rrc import RRCShowSpider

dotenv.load_dotenv()



def main():  # pragma: no cover
    """
    The main function executes on commands:
    `python -m rrc_rss` and `$ rrc_rss `.

    This is your program's entry point.
    """

    # Define the shows
    rrc_shows = [
        "https://www.radioromaniacultural.ro/emisiuni/idei-in-nocturna-izvoare-de-filosofie/",
        "https://www.radioromaniacultural.ro/emisiuni/idei-in-nocturna-pagini-de-istorie/",
        "https://www.radioromaniacultural.ro/emisiuni/confluente/",
        "https://www.radioromaniacultural.ro/emisiuni/texte-si-pretexte/",
        "https://www.radioromaniacultural.ro/podcast/o-ora-cu-dana/"
    ]

    # Run the spiders
    process = CrawlerProcess()
    process.crawl(RRCShowSpider, start_urls=rrc_shows)  #, max_episodes=2
    process.start()
