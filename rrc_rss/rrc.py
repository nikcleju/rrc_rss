import dateutil
import itertools
import math
import pytz

from datetime import datetime
from tqdm import tqdm

from requests_html import HTMLSession
from podgen import Podcast, Episode, Media
import gistyc

import logging
logging.basicConfig(level=logging.INFO)



def find_element_text(source, selector, **kwargs):
    """Helper function to find an element and return its text"""

    elem = source.find(selector, **kwargs)
    return elem.text if elem else None


class DateTimeParser():

    months = {
        'Ianuarie': 'January',
        'Februarie': 'February',
        'Martie': 'March',
        'Aprilie': 'April',
        'Mai': 'May',
        'Iunie': 'June',
        'Iulie': 'July',
        'August': 'August',
        'Septembrie': 'September',
        'Octombrie': 'October',
        'Noiembrie': 'November',
        'Decembrie': 'December'
    }

    def __init__(self):
        pass

    def parse(datetime_str):

        # date_split = datetime_str.split(', ')
        # date = date_split[0].strip()
        # time = date_split[1].strip()

        for month_ro, month_en in DateTimeParser.months.items():
            datetime_str = datetime_str.replace(month_ro, month_en)

        datetime_str.replace(', ', ' ')

        return dateutil.parser.parse(datetime_str).replace(tzinfo=pytz.UTC)  # TODO: replace UTC with local timezone


class RRCEpisode():

    def __init__(self, url):
        self.url = url

    def scrape(self, session=None):

        if session is None:
            session = HTMLSession()

        logging.debug(f'Scraping episode from {self.url}')
        page = session.get(self.url)
        page.html.render()

        # Find the title
        elem_articol = page.html.find('article.articol', first=True)
        title = find_element_text(elem_articol, 'h1', first=True)

        # Find the date
        datestr = find_element_text(page.html, 'p.articol__autor-data', first=True)
        date = DateTimeParser.parse(datestr) if datestr else datetime.now()

        # Find the article content
        content = find_element_text(page.html, '#__content', first=True)

        # Audio
        elem_audio = page.html.find('source', first=True)
        if elem_audio is None:
            return None
        audio = elem_audio.attrs['src']
        audio_type = elem_audio.attrs['type']
        if audio is None:
            return None

        # Create episode
        return Episode(
            title=title,
            media=Media(audio, type=audio_type),
            summary=content,
            publication_date=date
        )



class RRCShow():

    def __init__(self, url):

        self.url = url

    def scrape(self, max_episodes=None, session=None, file=''):
        """
        Scrape the episodes from the webpage
        """

        logging.info(f'Scraping episodes from {self.url}')

        if session is None:
            session = HTMLSession()

        if max_episodes is None:
            max_episodes = math.inf

        # Send a GET request to the webpage and render the Javascript
        page = session.get(self.url)
        page.html.render()

        # Get show title, author, program, description
        title = find_element_text(page.html, 'h1.cat-header__title', first=True)
        author = find_element_text(page.html, 'span.cat-header__descriere__realizator', first=True)
        program = find_element_text(page.html, 'span.cat-header__descriere__program', first=True)
        description = find_element_text(page.html, 'p.cat-header__descriere', first=True)

        # Create podcast
        podcast = Podcast(
            name=title,
            description=author + '\n' + program + '\n' + description,
            website=self.url,
            explicit=False
        )

        # Find all episodes and get their urls
        elem_episodes = page.html.find('div.news-item.news-item--with-audio')
        episode_urls = [elem_episode.find('a.link', first=True).attrs['href']
                              for elem_episode in elem_episodes]

        episode_count = 0
        for episode_url in tqdm(episode_urls, desc='Episodes'):

            if episode_count >= max_episodes:
                break

            episode = RRCEpisode(episode_url).scrape(session=session)
            podcast.add_episode(episode)
            episode_count += 1

        if file:
            if file == '':

                file = f'{title}.xml'
            podcast.rss_file(file)

        return podcast


class RRCShowListPage():

    def __init__(self, url):
        self.url = url

    def scrape(self, session=None):
        """
        Scrape the episodes from the webpage
        """

        if session is None:
            session = HTMLSession()

        logging.info(f'Scraping shows from {self.url}')

        # Send a GET request to the webpage and render the Javascript
        page = session.get(self.url)
        page.html.render()

        # Find all div elements with the specified class
        elem_shows = page.html.find('div.news-item')

        # Join all potential show links
        show_urls = itertools.chain(*[elem_show.absolute_links for elem_show in elem_shows])

        # Remove links to the main page link (e.g. 'https://www.radioromaniacultural.ro/emisiuni/')
        # TODO: make nicer
        show_urls = [show_url for show_url in show_urls if show_url != page.base_url]

        podcasts = []

        for show_url in tqdm(show_urls, desc='Shows'):
            show = RRCShow(show_url)
            podcast = show.scrape(session=session)
            podcasts.append(podcast)

        return podcasts


class RRCShowOrig():

    def __init__(self, url, xmlfile, title,
                 description='',
                 max_episodes=10,
                 gist_token=None):

        self.url = url
        self.xmlfile = xmlfile
        self.title = title
        self.description = description
        self.max_episodes = max_episodes
        self.gist_token = gist_token

        self.episode_data = []

    def scrape(self, max_episodes=None):
        """
        Scrape the episodes from the webpage
        """

        session = HTMLSession()

        # Send a GET request to the webpage and render the Javascript
        print(f'Scraping episodes from {self.url}')
        response = session.get(self.url)
        response.html.render()

        # Find all div elements with the specified class
        items = response.html.find('div.news-item.news-item--with-audio')

        self.episode_data = []
        for item in tqdm(items, desc='Episodes'):

            if self.max_episodes is not None and len(self.episode_data) >= self.max_episodes:
                break

            # Find the sub-item with class 'news-item__title' within the news item
            elem_title = item.find('div.news-item__title', first=True)
            title = elem_title.text if elem_title else 'No title'

            if item.absolute_links:
                for item_page_url in item.absolute_links:

                    # Workaround: skip link to main page ('https://www.radioromaniacultural.ro/emisiuni/texte-si-pretexte/')
                    if item_page_url == item.base_url:
                        continue

                    # print(f'Scraping {item_page_url}')
                    item_page = session.get(item_page_url)
                    item_page.html.render()

                    # Find the date
                    elem_date = item_page.html.find('p.articol__autor-data', first=True)
                    if elem_date:
                        date = elem_date.text.split(',')[0]
                        date = date.\
                            replace('Ianuarie', 'January').\
                            replace('Februarie', 'February').\
                            replace('Martie', 'March').\
                            replace('Aprilie', 'April').\
                            replace('Mai', 'May').\
                            replace('Iunie', 'June').\
                            replace('Iulie', 'July').\
                            replace('August', 'August').\
                            replace('Septembrie', 'September').\
                            replace('Octombrie', 'October').\
                            replace('Noiembrie', 'November').\
                            replace('Decembrie', 'December')
                        date = dateutil.parser.parse(date).replace(tzinfo=pytz.UTC)
                    else:
                        date = datetime.now()

                    # Find the content
                    elem_content = item_page.html.find('#__content', first=True)
                    content = elem_content.text if elem_content else 'No content'

                    # Audio
                    elem_audio = item_page.html.find('source', first=True)
                    audio = elem_audio.attrs['src'] if elem_audio else None
                    audio_type = elem_audio.attrs['type'] if elem_audio else None
                    if elem_audio is None or audio is None:
                        continue

                    self.episode_data.append({
                        'title': title,
                        'date': date,
                        'content': content,
                        'audio': audio,
                        'audio_type': audio_type
                    })

                    if self.max_episodes is not None and len(self.episode_data) >= self.max_episodes:
                        break

    def _create_podcast_xml(self):
        """
        Create the podcast XML file
        """

        podcast = Podcast(
            name=self.title,
            description=self.description,
            website=self.url,
            explicit=False
        )

        for episode in self.episode_data:
            episode = Episode(
                title=episode['title'],
                media=Media(episode['audio'], type=episode['audio_type']),
                summary=episode['content'],
                publication_date=episode['date']
            )

            podcast.add_episode(episode)
            #print(f'{self.title}: {episode.title} , {episode.publication_date}')

        print(f'Writing podcast XML to {self.xmlfile}')
        podcast.rss_file(self.xmlfile)
        return podcast

    def _push_to_gist(self):
        """
        Push the podcast XML to a Github Gist
        """

        if self.gist_token:
            gist_api = gistyc.GISTyc(auth_token=self.gist_token)
            gists = gist_api.get_gists()

            # Check if the gist is already present
            is_gist_present = False
            for gist in gists:
                if self.xmlfile in gist['files']:
                    is_gist_present = True
                    break

            if is_gist_present:
                print(f'Updating gist {self.xmlfile}')
                gist_api.update_gist(file_name=self.xmlfile)
            else:
                print(f'Creating gist {self.xmlfile}')
                gist_api.create_gist(file_name=self.xmlfile)
        else:
            print('No Github token provided. Not pushing to Github gists.')

    def run(self):
        """
        Run the show
        """
        print("=========================================")
        print(f'Show: {self.title}')
        print("=========================================")
        self._scrape()
        self._create_podcast_xml()
        self._push_to_gist()

        return self

