# Initialization code. Placed in a separate Python package from the main
# app, this code allows the app created to be imported into any other
# package, module, or method.

import logging          # Import standard logging - for levels only

from python_cowbull_server.Configurator import Configurator
from flask import Flask

# Instantiate the Flask application as app
app = Flask(__name__)
c = Configurator()

print('')
print('-'*80)
print('The following environment variables may be set to dynamically')
print('configure the server. Alternately, these can be defined in a ')
print('file and passed using the env. var. COWBULL_CONFIG. Please ')
print('note, the file must be a JSON data object.')
print('')
print('Please note. Env. Var. names can be *ALL* lowercase or *ALL* uppercase.')

c.execute_load(app)

print('-'*80)
print('| Current configuration set:')
print('-'*80)
for name, val in c.dump_variables():
    outstr = "| {:20s} | {}".format(name, val)
    print(outstr)
    logging.debug(outstr)
print('-'*80)
print('')

if app.config["COWBULL_DRY_RUN"]:
    print("")
    print("Dry run env. var. is set. Exiting...")
    print("")
    exit(0)

error_handler = c.error_handler
error_handler.log(
    method="__init__",
    module="python_cowbull_server",
    message="Initialization complete.",
    logger=logging.info
)