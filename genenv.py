import socket # for getting the name of the machine
import os
from configparser import ConfigParser # for reading the .ini file

# create ConfigParser instance for reading .ini file
local_config = ConfigParser()
local_config.read('local.ini') 

# decide which section to use based on the following priority 
# 1. section assigned by ENV > 2. the section that correspond to the machine > 3. default section
if os.environ.get('ENV', ''):
    # if the ENV is assigned, use the corresponging section
    section = local_config[os.environ.get('ENV', '')]
else:
    section = local_config['DEFAULT']

# convert the content of selected section to .env file
env_content = ''
for sec in section:
    env_content += '{}={}\n'.format(sec.upper(), section[sec]) 

# write the content to .env file
with open('.env', 'w', encoding='utf8') as env:
    env.write(env_content)

