from omegaconf import OmegaConf

# Default configuration. This will be overwritten by the configuration file
config_defaults = {
    'shows': {
        'showlists': [],
        'shows': [],
        'combos': [],
    },
    'options': {
        'max_episodes': None,
        'min_episodes': 0,
    },
    'cache': {
        'enabled': False,
        'dir': 'data',
        'file_shows': None,
        'file_podcasts': None,
        'file_hashes': None,
    }
}

config = OmegaConf.create(config_defaults)
