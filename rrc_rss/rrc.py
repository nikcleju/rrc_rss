import dateutil
import pytz
import scrapy
import pickle
from slugify import slugify
from datetime import datetime
import logging
logging.basicConfig(level=logging.INFO)

from rrc_rss.pipelines import ShowDescriptionItem, EpisodeItem

class DateTimeParser:

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

    @staticmethod
    def parse(datetime_str):
        for month_ro, month_en in DateTimeParser.months.items():
            datetime_str = datetime_str.replace(month_ro, month_en)
        datetime_str = datetime_str.replace(', ', ' ')
        return dateutil.parser.parse(datetime_str).replace(tzinfo=pytz.UTC)


class RRCShowSpider(scrapy.Spider):
    name = 'show_spider'

    custom_settings = {
        'ITEM_PIPELINES': {
            'rrc_rss.pipelines.CreatePodcastPipeline': 300
        }
    }

    def __init__(self, max_episodes=None, do_cache=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_episodes = max_episodes
        self.do_cache = do_cache

    def parse(self, response):
        title = response.css('h1.cat-header__title::text').get(default='').strip()
        author = response.css('span.cat-header__descriere__realizator::text').get(default='').strip()
        program = response.css('span.cat-header__descriere__program strong::text').get(default='')
        description = response.css('p.cat-header__descriere::text').get(default='')

        # Send first the podcast description item
        yield ShowDescriptionItem(
            title=title,
            author=author,
            program=program,
            description=description,
            website=response.url)

        # Get episode urls
        episode_urls = response.css('div.news-item.news-item--with-audio a.link::attr(href)').getall()
        if self.max_episodes:
            episode_urls = episode_urls[:self.max_episodes]

        # Load episode urls from pickle file
        old_episode_urls = []
        if self.do_cache:
            pkl_filename = 'cache/' + slugify(title) + '.pkl'
            try:
                with open(pkl_filename, 'rb') as f:
                    old_episode_urls = pickle.load(f)
            except FileNotFoundError:
                pass

        # Keep only the new episodes
        new_episode_urls = list(set(episode_urls) - set(old_episode_urls))

        # Follow new episode urls
        for url in new_episode_urls:
            if url not in old_episode_urls:
                yield response.follow(url, callback=self.parse_episode, cb_kwargs={'show_name': title})

        # Save episode urls to pickle file
        if self.do_cache:
            with open(pkl_filename, 'wb') as f:
                pickle.dump(episode_urls, f)

    def parse_episode(self, response, show_name):

        title = response.css('article.articol h1::text').get(default='').strip()
        datestr = response.css('p.articol__autor-data::text').get(default='').strip()
        date = DateTimeParser.parse(datestr) if datestr else datetime.now()
        paragraphs = response.css('#__content p').xpath('string(.)').getall()
        description = '\n'.join(paragraphs)

        audio_elem = response.css('source').attrib
        audio_url = audio_elem.get('src')
        audio_type = audio_elem.get('type')

        if audio_url:
            yield EpisodeItem(
                show_name=show_name,
                title=title,
                date=date,
                audio_url=audio_url,
                audio_type=audio_type,
                description=description
            )


class RRCShowListSpider(scrapy.Spider):
    name = 'shows_list_spider'

    def __init__(self, min_episodes=0, do_cache=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.min_episodes = min_episodes
        self.do_cache = do_cache

    def parse(self, response):
        show_urls = response.css('div.news-item a.link::attr(href)').getall()
        for url in show_urls:
            yield response.follow(url, callback=RRCShowSpider.parse)

    def parse_show(self, response):
        show_spider = RRCShowSpider(url=response.url, max_episodes=self.min_episodes)
        show = next(show_spider.parse(response))
        if show and len(show.episodes) >= self.min_episodes:
            self.podcasts.append(show)
        return self.podcasts


