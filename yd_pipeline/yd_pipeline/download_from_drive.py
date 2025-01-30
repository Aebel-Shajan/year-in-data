import gdown
from dotenv import load_dotenv
import os


def download_data_from_drive(share_url: str):
    """
    Downloads zip files from google drive using a shared link.
    """
    output = 'data/input'
    gdown.download_folder(
        url=share_url, 
        output=output,
        quiet=False,
        use_cookies=False
    )

if __name__ == "__main__":
    load_dotenv()
    download_data_from_drive(share_url=os.getenv("DRIVE_SHARE_URL"))