
from slugify import slugify
from podgen import Podcast
import hashlib
import pickle
import re
import gistyc
import dropbox
import rrc_rss.config
import rrc_rss.pastebin as pastebin

import logging
logger = logging.getLogger('RRC_RSS')

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

        # Add show category in name, e.g. Emisiuni-Texte-si-pretexte.xml
        filename = ''
        if hasattr(podcast, 'show_category'):
            filename += podcast.show_category + '-'
        filename += slugify(podcast.name).capitalize() + '.xml'
        return filename

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
                    logger.debug(f'Updating gist {filename}')
                    gist_api.update_gist(file_name=filename)
                else:
                    logger.debug(f'Creating gist {filename}')
                    gist_api.create_gist(filename)
        else:
            logger.warning('No Github token provided. Not pushing to Github gists.')



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
            logger.debug(f'Pastebin URL: {result}')


    def to_dropbox(self):

        if not self.dropbox_token:
            logger.warning('No Dropbox token provided. Not pushing to Dropbox.')
            return

        if not self.dropbox_refresh_token:
            logger.warning('No Dropbox refresh token provided. Not pushing to Dropbox.')
            return

        # Connect to Dropbox
        dbx = dropbox.Dropbox(
            oauth2_access_token=self.dropbox_token,
            oauth2_refresh_token=self.dropbox_refresh_token,
            app_key=self.dropbox_app_key,
            app_secret=self.dropbox_app_secret
        )

        # Read existing file content hashes
        try:
            with open(rrc_rss.config.config.cache.file_hashes, 'rb') as f:
                hashes = pickle.load(f)
                logger.info(f"Hashes loaded from {rrc_rss.config.config.cache.file_hashes}")
        except FileNotFoundError:
            hashes = {}

        for podcast in self.podcasts:

            # Define the file path
            file_path = f'{self.dropbox_folder}/{PodcastsUploader.filename(podcast)}'

            # Compute the file hash and compare with the old one
            # Remove the lastBuildDate tag before hashing, as this changes every time
            file_data = podcast.rss_str()
            file_data = re.sub(r"<lastBuildDate>.*?</lastBuildDate>", "<lastBuildDate></lastBuildDate>", file_data, flags=re.DOTALL)
            file_data = file_data.encode()
            file_hash = hashlib.md5(file_data).hexdigest()
            file_unchanged = file_path in hashes and hashes[file_path] == file_hash

            # Upload only if the file has changed
            if not file_unchanged:
                try:
                    dbx.files_upload(
                        podcast.rss_str().encode(),
                        file_path,
                        mode=dropbox.files.WriteMode("overwrite")
                    )
                except Exception as e:
                    logger.error(f"Error uploading {podcast.name} to Dropbox: {e}")

                logger.info(f"{podcast.name} uploaded to Dropbox at {file_path}")

                # Save the new hash
                hashes[file_path] = file_hash

            else:
                logger.debug(f"{podcast.name} unchanged, not uploaded to Dropbox")

        # Save the new hashes
        with open(rrc_rss.config.config.cache.file_hashes, 'wb') as f:
            pickle.dump(hashes, f)
            logger.info(f"Hashes saved to {rrc_rss.config.config.cache.file_hashes}")


