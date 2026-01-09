import requests

URL = "https://www.songkick.com/metro-areas/26794-australia-sydney"
page = requests.get(URL)

print(page.text)