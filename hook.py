import os
import sys
from dotenv import load_dotenv

if hasattr(sys, '_MEIPASS'):
    env_path = os.path.join(sys._MEIPASS, '.env')
    load_dotenv(env_path)