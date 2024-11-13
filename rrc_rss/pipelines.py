import os
import dotenv
import pickle

from podgen import Podcast, Episode, Media
from scrapy import Item, Field
from rrc_rss.upload import PodcastsUploader

import logging
logging.basicConfig(level=logging.INFO)

dotenv.load_dotenv()

class ShowDescriptionItem(Item):
    title = Field()
    author = Field()
    program = Field()
    description = Field()
    category = Field()
    website = Field()

class EpisodeItem(Item):
    show_name = Field()
    title = Field()
    date = Field()
    audio_url = Field()
    audio_type = Field()
    description = Field()

class CreatePodcastPipeline:

    do_cache = False

    def open_spider(self, spider):
        # Load existing podcasts from cache file
        if CreatePodcastPipeline.do_cache:
            try:
                with open('podcasts.pkl', 'rb') as f:
                    self.podcasts = pickle.load(f)
            except FileNotFoundError:
                    self.podcasts = {}
        else:
            self.podcasts = {}

    def process_item(self, item, spider):

        # Create a new podcast
        if isinstance(item, ShowDescriptionItem):
            if item['title'] not in self.podcasts:
                self.podcasts[item['title']] = Podcast(
                    name=item['title'],
                    description=f"{item['author']}\n{item['program']}\n{item['description']}",
                    website=item['website'],
                    explicit=False
                )
                # Sneak the category attribute into the podcast object
                # Don't use built-in 'category' attribute, use a custom one
                self.podcasts[item['title']].show_category = item['category']

            else:
                logging.debug(f"Podcast {item['title']} already exists")

        # Add an episode to an existing podcast
        elif isinstance(item, EpisodeItem):
            show_name = item['show_name']
            if show_name in self.podcasts:

                # Check if episode is not already present
                episode_exists = False
                if any(episode.title == item['title'] for episode in self.podcasts[show_name].episodes):
                    logging.info(f"Episode {item['title']} already exists in podcast {show_name}")
                    episode_exists = True

                if not episode_exists:
                    self.podcasts[show_name].add_episode(
                        Episode(
                            title=item['title'],
                            media=Media(item['audio_url'], type=item['audio_type']),
                            summary=item['description'],
                            publication_date=item['date']
                        )
                    )
                else:
                    logging.debug(f"Episode {item['title']} already exists in podcast {show_name}")
            else:
                logging.warning(f"Podcast {show_name} not found")
        else:
            raise ValueError(f"Unknown item type: {type(item)}")

        return item


    def close_spider(self, spider):

        # Save collected podcasts
        if CreatePodcastPipeline.do_cache:
            with open('podcasts.pkl', 'wb') as f:
                pickle.dump(self.podcasts, f)

        # Upload collected podcasts
        PodcastsUploader(
            podcasts=list(self.podcasts.values()),
            dropbox_folder=os.getenv('DROPBOX_FOLDER'),
            dropbox_token=os.getenv('DROPBOX_ACCESS_TOKEN'),
            dropbox_refresh_token=os.getenv('DROPBOX_REFRESH_TOKEN'),
            dropbox_app_key=os.getenv('DROPBOX_APP_KEY'),
            dropbox_app_secret=os.getenv('DROPBOX_APP_SECRET')
        ).to_dropbox()


