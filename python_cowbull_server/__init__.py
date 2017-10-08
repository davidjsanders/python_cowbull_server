# Initialization code. Placed in a separate Python package from the main
# app, this code allows the app created to be imported into any other
# package, module, or method.

import argparse
import logging          # Import standard logging - for levels only

from python_cowbull_server.Configurator import Configurator
from flask import Flask

#
# Step 1 - Check any command line arguments passed
#
parser = argparse.ArgumentParser()
parser.add_argument('--env',
                    dest='showenvvars',
                    default=False,
                    action='store_true',
                    help="Show the environment variables that can be set by this app")

args = parser.parse_args()

# Instantiate the Flask application as app
app = Flask(__name__)
c = Configurator()

# Decide if using ANSI or GUI
if args.showenvvars:
    print('')
    print('The following environment variables may be set to dynamically')
    print('configure the server. Alternately, these can be defined in a ')
    print('file and passed using the env. var. COWBULL_CONFIG.')
    print('')
    print('Please note. Env. Vars can be *ALL* lowercase or *ALL* uppercase.')
    print('')
    for name, desc in c.get_variables():
        print(name, '-->', desc)
    print('')
    exit(0)

c.execute_load(app)

error_handler = c.error_handler
error_handler.log(
    method="__init__",
    module="python_cowbull_server",
    message="Initialization complete.",
    logger=logging.info
)