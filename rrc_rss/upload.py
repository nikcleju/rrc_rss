
from slugify import slugify
from podgen import Podcast
import pickle
import gistyc
import dropbox
import rrc_rss.pastebin as pastebin

import logging
logging.basicConfig(level=logging.INFO)


class PodcastsUploader():

    def __init__(self,
                 podcasts,
                 gist_token=None,
                 pastebin_api_key=None,
                 pastebin_username=None,
                 pastebin_password=None,
                 dropbox_token=None,
                 dropbox_refresh_token=None,
                 dropbox_app_key=None,
                 dropbox_app_secret=None,
                 dropbox_folder=''):

        if not isinstance(podcasts, list) and not isinstance(podcasts, tuple):
            podcasts = [podcasts]

        self.podcasts = podcasts
        self.gist_token = gist_token
        self.pastebin_api_key = pastebin_api_key
        self.pastebin_username = pastebin_username
        self.pastebin_password = pastebin_password
        self.dropbox_token = dropbox_token
        self.dropbox_refresh_token = dropbox_refresh_token
        self.dropbox_app_key = dropbox_app_key
        self.dropbox_app_secret = dropbox_app_secret
        self.dropbox_folder = dropbox_folder


    @staticmethod
    def filename(podcast: Podcast):
        return slugify(podcast.name) + '.xml'

    def to_file(self, podcast: Podcast):
        for podcast in self.podcasts:
            podcast.rss_file(PodcastsUploader.filename(podcast))

    def to_gist(self):
        if self.gist_token:
            gist_api = gistyc.GISTyc(auth_token=self.gist_token)
            gists = gist_api.get_gists()

            for podcast in self.podcasts:

                filename = PodcastsUploader.filename(podcast)

                # Check if the gist is already present
                is_gist_present = False
                for gist in gists:
                    if filename in gist['files']:
                        is_gist_present = True
                        break

                if is_gist_present:
                    logging.info(f'Updating gist {filename}')
                    gist_api.update_gist(file_name=filename)
                else:
                    logging.info(f'Creating gist {filename}')
                    gist_api.create_gist(filename)
        else:
            logging.info('No Github token provided. Not pushing to Github gists.')



    def to_pastebin(self):

        api = pastebin.PasteBin(self.pastebin_api_key)
        api.api_user_key = api.create_user_key(self.pastebin_password, self.pastebin_password)

        for podcast in self.podcasts:
            result = api.paste(podcast.rss_str(),
                                guest=False,
                                name=podcast.name,
                                format='xml',
                                private='0',
                                expire='N')
            logging.info(f'Pastebin URL: {result}')


    def to_dropbox(self):

        if not self.dropbox_token:
            logging.info('No Dropbox token provided. Not pushing to Dropbox.')
            return

        if not self.dropbox_refresh_token:
            logging.info('No Dropbox refresh token provided. Not pushing to Dropbox.')
            return

        # Connect to Dropbox
        dbx = dropbox.Dropbox(
            oauth2_access_token=self.dropbox_token,
            oauth2_refresh_token=self.dropbox_refresh_token,
            app_key=self.dropbox_app_key,
            app_secret=self.dropbox_app_secret
        )

        for podcast in self.podcasts:

            # Define the file path
            file_path = f'{self.dropbox_folder}/{PodcastsUploader.filename(podcast)}'

            # Upload data
            try:
                dbx.files_upload(
                    podcast.rss_str().encode(), file_path, mode=dropbox.files.WriteMode("overwrite"))
            except Exception as e:
                logging.error(f"Error uploading {podcast.name} to Dropbox: {e}")

            logging.info(f"{podcast.name} written to Dropbox at {file_path}")

        # Save podcasts files so we can reload them next time
        pickle_file = 'podcasts.pkl'
        with open(pickle_file, 'wb') as f:
            pickle.dump(self.podcasts, f)
