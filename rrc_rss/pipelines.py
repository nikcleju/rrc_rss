import os
import dotenv
import pickle

from podgen import Podcast, Episode, Media
from scrapy import Item, Field
from rrc_rss.upload import PodcastsUploader
import rrc_rss.config

import logging
logger = logging.getLogger('RRC_RSS')


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
    """
    A Scrapy pipeline to create a podcast from scraped items.

    The Scrapy spider yields ShowDescriptionItems and EpisodeItems.
    It is assumed that the ShowDescriptionItem is yielded first.

    The pipeline creates a Podcast object for each ShowDescriptionItem, and
    adds Episode objects to the Podcast.

    For Combo podcasts (e.g. multiple shows in one feed), the pipeline
    assembles the episodes from different shows in the same Podcast object,
    so this is handled here.
    """

    do_cache = False

    def create_or_update_podcast(self, name, description, website, explicit, **kwargs):
        """
        Create or update a podcast with the given metadata
        """
        if name not in self.podcasts:
            self.podcasts[name] = Podcast(
                name=name,
                description=description,
                website=website,
                explicit=explicit,
            )
        for key, value in kwargs.items():
            setattr(self.podcasts[name], key, value)


    def open_spider(self, spider):
        """
        Runs when the spider is opened.

        Load existing podcasts from cache file.
        """

        # Load existing podcasts from cache file
        if hasattr(spider, 'do_cache') and spider.do_cache:
            # if CreatePodcastPipeline.do_cache:
            try:
                with open(rrc_rss.config.config.cache.file_podcasts, 'rb') as f:
                    self.podcasts = pickle.load(f)
                    logger.info(f"Loaded {len(self.podcasts)} podcasts from {rrc_rss.config.config.cache.file_podcasts}")
            except FileNotFoundError:
                    self.podcasts = {}
        else:
            self.podcasts = {}

        # Create combo podcasts
        for combo in rrc_rss.config.config.shows.combos:
            self.create_or_update_podcast(
                name=combo.name,
                description=combo.description if hasattr(combo, 'description') else 'Combo podcast',
                website=str(combo.urls),
                explicit=False,
                show_category='Combo'
            )


    def process_item(self, item, spider):
        """
        Process a scraped item
        """

        # Received a ShowDescriptionItem, create a new podcast if it doesn't exist
        if isinstance(item, ShowDescriptionItem):
            self.create_or_update_podcast(
                name=item['title'],
                description=f"{item['author']}\n{item['program']}\n{item['description']}",
                website=item['website'],
                explicit=False,
                show_category=item['category']
            )

        # Received an EpisodeItem, add it to the corresponding podcast(s)
        elif isinstance(item, EpisodeItem):
            show_name = item['show_name']

            # Add it to its corresponding podcast
            if show_name in self.podcasts:

                # Skip if episode is already present, add it otherwise
                if any(existing_episode.title == item['title'] for existing_episode in self.podcasts[show_name].episodes):
                    logger.debug(f"Podcast \"{show_name}\": episode exists \"{item['title']}\"")
                else:
                    self.podcasts[show_name].add_episode(
                        Episode(
                            title=item['title'],
                            media=Media(item['audio_url'], type=item['audio_type']),
                            summary=item['description'],
                            publication_date=item['date']
                        )
                    )
                    logger.info(f"Podcast \"{show_name}\": added episode \"{item['title']}\"")
            else:
                logger.error(f"Podcast \"{show_name}\" not found")

            # Add it to combo podcasts that include this show
            show_website = self.podcasts[show_name].website
            for combo in rrc_rss.config.config.shows.combos:
                if show_website in combo.urls:

                    # Format episode title to include the show name
                    episode_title = f"{show_name}: {item['title']}"

                    # Skip if episode is already present, add it otherwise
                    if any(existing_episode.title == episode_title for existing_episode in self.podcasts[combo.name].episodes):
                        logger.debug(f"Podcast \"{combo.name}\": episode exists \"{episode_title}\"")
                    else:
                        self.podcasts[combo.name].add_episode(
                            Episode(
                                title=episode_title,
                                media=Media(item['audio_url'], type=item['audio_type']),
                                summary=item['description'],
                                publication_date=item['date']
                            )
                        )
                        logger.info(f"Podcast \"{combo.name}\": added episode \"{episode_title}\"")

        else:
            raise ValueError(f"Unknown item type: {type(item)}")

        return item


    def close_spider(self, spider):
        """
        Runs when the spider is closed.

        Uploads podcasts and saves them to a cache file.
        """

        # Save collected podcasts
        #if CreatePodcastPipeline.do_cache:
        if hasattr(spider, 'do_cache') and spider.do_cache:
            with open(rrc_rss.config.config.cache.file_podcasts, 'wb') as f:
                pickle.dump(self.podcasts, f)
                logger.info(f"Saved {len(self.podcasts)} podcasts to {rrc_rss.config.config.cache.file_podcasts}")

        # Upload collected podcasts
        PodcastsUploader(
            podcasts=list(self.podcasts.values()),
            dropbox_folder=os.getenv('DROPBOX_FOLDER'),
            dropbox_token=os.getenv('DROPBOX_ACCESS_TOKEN'),
            dropbox_refresh_token=os.getenv('DROPBOX_REFRESH_TOKEN'),
            dropbox_app_key=os.getenv('DROPBOX_APP_KEY'),
            dropbox_app_secret=os.getenv('DROPBOX_APP_SECRET')
        ).to_dropbox()


