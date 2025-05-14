import requests
from bs4 import BeautifulSoup

def get_play_store_icon(package_name):
    url = f"https://play.google.com/store/apps/details?id={package_name}&hl=en&gl=us"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    icon_tag = soup.find("img", {"alt": True})
    if icon_tag and "src" in icon_tag.attrs:
        return icon_tag["src"]
    return None

icon_url = get_play_store_icon("com.google_drive")
print("Icon URL:", icon_url)

