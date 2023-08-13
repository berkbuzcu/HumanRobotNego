import os
import pathlib
from dotenv import load_dotenv

PROJECT_DIR = pathlib.Path(__file__).parent
ROBOT_SERVER_DIR = PROJECT_DIR.parent / "robot_server"
DOMAINS_DIR = PROJECT_DIR.parent / "domains"
CONFIG_DIR = PROJECT_DIR / "config"
REQUIREMENTS_DIR = PROJECT_DIR.parent

load_dotenv(str(PROJECT_DIR / ".env"))

os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = f"{str(PROJECT_DIR)}/config/{os.environ.get('GOOGLE_SPEECH_JSON_FILE')}"

