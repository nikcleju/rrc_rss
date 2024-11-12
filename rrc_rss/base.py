import os
from abc import ABC
from slugify import slugify

from podgen import Podcast, Episode, Media
import dotenv
import gistyc
import pastebin

import logging
logging.basicConfig(level=logging.INFO)

dotenv.load_dotenv()


# class WebEpisode(ABC):
#     def scrape(self):
#         pass

# class WebPodcast(ABC):
#     def scrape(self):
#         pass

# class WebPodcastList(ABC):
#     def scrape(self):
#         pass


class PodcastUploader():

    def __init__(self, podcast):
        self.podcast = podcast

    @property
    def filename(self):
        return slugify(self.podcast.title) + '.xml'

    def to_file(self, podcast: Podcast):
        podcast.rss_file(self.filename)

    def to_gist(self, token):

        if token:
            gist_api = gistyc.GISTyc(auth_token=token)
            gists = gist_api.get_gists()

            # Check if the gist is already present
            is_gist_present = False
            for gist in gists:
                if self.filename in gist['files']:
                    is_gist_present = True
                    break

            if is_gist_present:
                logging.info(f'Updating gist {self.filename}')
                gist_api.update_gist(file_name=self.filename)
            else:
                logging.info(f'Creating gist {self.filename}')
                gist_api.create_gist(file_name=self.filename)
        else:
            logging.info('No Github token provided. Not pushing to Github gists.')



    def to_pastebin(self):

        api_key = os.getenv('PASTEBIN_API_KEY')
        username = os.getenv('PASTEBIN_USERNAME')
        password = os.getenv('PASTEBIN_PASSWORD')

        api = pastebin.PasteBin(api_key)
        api.api_user_key = api.create_user_key(username, password)

        result = api.paste(self.podcast.rss_str(),
                            #"aaaa",
                            guest=False,
                            name=self.podcast.name,
                            format='xml',
                            private='0',
                            expire='N')
        #logging.info(f'Pastebin URL: {result}')
        print(f'Pastebin URL: {result}')
