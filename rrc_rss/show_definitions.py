import os
import dotenv

from rrc_rss.base import RRCShow


dotenv.load_dotenv()
shows = []

shows.append(
    RRCShow(
        url='https://www.radioromaniacultural.ro/emisiuni/texte-si-pretexte/',
        xmlfile='texte_si_pretexte.xml',
        title='Texte si pretexte',
        description='Realizator: Valentin Protopopescu',
        max_episodes=10,
        gist_token=os.getenv('GIST_TOKEN')
        )
)
