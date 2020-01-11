import os

from config import conf
from logger import log
from cmdClient import cmdClient

# Get the real location
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


client = cmdClient()
client.load_dir(os.path.join(__location__, 'commands'))

log("Initial setup complete, logging in", context='SETUP')
client.run(conf['TOKEN'])
