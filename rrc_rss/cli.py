"""CLI interface for rrc_rss project.

Be creative! do whatever you want!

- Install click or typer and create a CLI app
- Use builtin argparse
- Start a web application
- Import things from your .base module
"""

from rrc_rss.show_definitions import shows

from base import PodcastUploader
from rrc_rss.rrc import RRCShow

def main():  # pragma: no cover
    """
    The main function executes on commands:
    `python -m rrc_rss` and `$ rrc_rss `.

    This is your program's entry point.

    You can change this function to do whatever you want.
    Examples:
        * Run a test suite
        * Run a server
        * Do some other stuff
        * Run a command line application (Click, Typer, ArgParse)
        * List all available tasks
        * Run an application (Flask, FastAPI, Django, etc.)
    """

    # for show in shows:
    #     show.run()

    pu = PodcastUploader(
        RRCShow('https://www.radioromaniacultural.ro/emisiuni/texte-si-pretexte/').scrape(max_episodes=2)
    )
    pu.to_pastebin()
