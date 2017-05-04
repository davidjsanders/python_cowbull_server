import json
import logging
import os
from json.decoder import JSONDecodeError


def fetch_config(osvar=None):
    _osvar = osvar or "COWBULL_CONFIG"
    cowbull_config = os.getenv(_osvar, "/usr/local/etc/cowbull/cowbull-config.json")

    logging.debug("Creating default configuration")
    _config = {
        "default": True,
        "redis_host": "redis",
        "redis_port": 6379,
        "redis_db": 0
    }

    success = True
    try:
        logging.debug("Fetching configuration from {}".format(cowbull_config))
        f = open(cowbull_config, 'r')
    except FileNotFoundError as f:
        logging.error("Configuration file not found.")
        success = False

    if success:
        logging.debug("Processing JSON from {}".format(cowbull_config))
        try:
            _config = json.load(f)
            logging.debug("Config loaded from JSON: {}".format(_config))
        except JSONDecodeError as jde:
            logging.error("There was a problem with the JSON: {}".format(jde))
            logging.info("Reverting to default configuration.")
        except Exception as e:
            logging.error(repr(e))
        f.close()

    logging.debug("Config is {}".format(_config))
