import requests
import time
import io
from PIL import Image
from rembg import remove

TOKEN = "Your bale token from botfather"
BASE_URL = f"https://tapi.bale.ai/bot{TOKEN}"

def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"
    params = {"offset": offset} if offset else {}
    return requests.get(url, params=params).json()

def download_file(file_id):
    url = f"{BASE_URL}/getFile"
    result = requests.get(url, params={"file_id": file_id}).json()
    if result.get("ok"):
        download_url = f"https://tapi.bale.ai/file/bot{TOKEN}/{result['result']['file_path']}"
        return requests.get(download_url).content
    return None

def send_photo(chat_id, photo_file, caption=""):
    url = f"{BASE_URL}/sendPhoto"
    data = {"chat_id": chat_id, "caption": caption}
    return requests.post(url, data=data, files={"photo": photo_file}).json()

def process_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    output = remove(image)
    img_bytes = io.BytesIO()
    output.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes

def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    return requests.post(url, json=payload).json()

offset = None
while True:
    updates = get_updates(offset)
    if updates.get("ok"):
        for update in updates["result"]:
            offset = update["update_id"] + 1
            message = update.get("message")
            if not message:
                continue

            chat_id = message["chat"]["id"]
            if message.get("text", "").strip() == "/start":
                send_message(chat_id, "سلام! برای حذف پس‌زمینه، عکس بفرستید.")

            if "photo" in message:
                photos = message["photo"]
                send_message(chat_id, "✅ در حال پردازش تصویر...")
                best_photo = max(photos, key=lambda x: x.get("file_size", 0))

                image_data = download_file(best_photo["file_id"])
                if image_data:
                    try:
                        result_image = process_image(image_data)
                        send_photo(chat_id, result_image, caption="✅ پس‌زمینه عکس حذف شد!")
                    except Exception as e:
                        send_message(chat_id, "❌ خطایی در پردازش تصویر رخ داد!")
                        print("خطا در پردازش تصویر:", e)

    time.sleep(5)

