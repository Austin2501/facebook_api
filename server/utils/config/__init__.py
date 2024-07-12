import os
from pathlib import Path
from configparser import ConfigParser
import environment
# Determine the directory containing the script
this_dir = Path(__file__).resolve().parent

# Specify the path to the properties.ini file
conf_dir = this_dir / 'properties.ini'

# Create a ConfigParser instance
parser = ConfigParser()

# Read the properties.ini file
parser.read(conf_dir, encoding='utf8')

class Config:
    @staticmethod
    def read(section, property, default=None):
        return parser.get(section, property, fallback=default)

# Get the value of the 'env' key from the 'app' section
env_value = parser.get('app', 'env')

# Perform environment variable interpolation
env_value = os.path.expandvars(env_value)

# Specify the environment file to use
selected_env_file = environment.dev  # Change this to the desired environment

# Load environment variables from the selected file
with open(selected_env_file) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):  # Skip empty lines and comments
            key, value = line.split('=')
            key = key.strip()
            value = value.strip()
            os.environ[key] = value

# Set the 'env' environment variable
os.environ['ENV'] = env_value