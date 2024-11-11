from datetime import datetime
import dateutil
import pytz

from requests_html import HTMLSession
from podgen import Podcast, Episode, Media
import gistyc

class RRCShow():

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

    def _scrape(self):

        session = HTMLSession()

        # Send a GET request to the webpage and render the Javascript
        print(f'Scraping {self.url}')
        response = session.get(self.url)
        response.html.render()

        # Find all div elements with the specified class
        items = response.html.find('div.news-item.news-item--with-audio')

        self.episode_data = []
        for item in items:

            if len(self.episode_data) >= self.max_episodes:
                break

            # Find the sub-item with class 'news-item__title' within the news item
            elem_title = item.find('div.news-item__title', first=True)
            title = elem_title.text if elem_title else 'No title'

            if item.absolute_links:
                for item_page_url in item.absolute_links:

                    # Workaround: skip link to main page ('https://www.radioromaniacultural.ro/emisiuni/texte-si-pretexte/')
                    if item_page_url == item.base_url:
                        continue

                    print(f'Scraping {item_page_url}')
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

                    if len(self.episode_data) >= self.max_episodes:
                        break

    def _create_podcast_xml(self):
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
            print(f'{self.title}: {episode.title} , {episode.publication_date}')

        podcast.rss_file(self.xmlfile)
        return podcast

    def _push_to_gist(self):
        if self.gist_token:
            gist_api = gistyc.GISTyc(auth_token=self.gist_token)
            gist_api.create_gist(file_name=self.xmlfile)
        else:
            print('No Github token provided. Not pushing to Github gists.')

    def run(self):
        self._scrape()
        self._create_podcast_xml()
        self._push_to_gist()

        return self

