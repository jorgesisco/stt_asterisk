import os
from dotenv import load_dotenv

load_dotenv()

ARI_URL = os.environ.get('ARI_URL')
ARI_USERNAME = os.environ.get('ARI_USERNAME')
ARI_PASSWORD = os.environ.get('ARI_PASSWORD')
APPLICATION = os.environ.get('APPLICATION')
