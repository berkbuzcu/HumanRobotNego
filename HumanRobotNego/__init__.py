import os
import pathlib
from dotenv import load_dotenv

PROJECT_DIR = pathlib.Path(__file__).parent
ROBOT_SERVER_DIR = PROJECT_DIR.parent / "RobotServer"
DOMAINS_DIR = PROJECT_DIR / "HANT" / "Domains"

load_dotenv(str(PROJECT_DIR / ".env"))

os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = f"{str(PROJECT_DIR)}/config/{os.environ.get('GOOGLE_SPEECH_JSON_FILE')}"

