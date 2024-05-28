import json
from classes import SystemConfiguration

# Read the JSON configuration file
with open('config.json', 'r') as file:
    config_data = json.load(file)

# Read the JSON configuration file
with open('config.json', 'r') as file:
    config_data = json.load(file)

# Create an instance of the Configuration class
config = SystemConfiguration(config_data)


