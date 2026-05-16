import urllib.request
from PIL import Image

url = "https://raw.githubusercontent.com/pygame/pygame/main/examples/data/alien1.png"
save_path = r"d:\TRI_TUE_NHAN_TAO\GAME_HAY\chien_truong\player.png"

try:
    urllib.request.urlretrieve(url, save_path)
    print("Download successful")
except Exception as e:
    print(f"Error: {e}")
