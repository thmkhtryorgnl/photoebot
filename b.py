import requests
import time
import io
from PIL import Image
from rembg import remove

TOKEN = "2005645682:9KcdD3ItRLVGrQAHfoA5I3G9hcGoMOVj1JADyFon"
BASE_URL = f"https://tapi.bale.ai/bot{TOKEN}"


def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"
    params = {}
    if offset:
        params["offset"] = offset
    response = requests.get(url, params=params)
    return response.json()


def download_file(file_id):
    url = f"{BASE_URL}/getFile"
    params = {"file_id": file_id}
    resp = requests.get(url, params=params)
    result = resp.json()
    if result.get("ok"):
        file_path = result["result"]["file_path"]
        download_url = f"https://tapi.bale.ai/file/bot{TOKEN}/{file_path}"
        file_resp = requests.get(download_url)
        if file_resp.status_code == 200:
            return file_resp.content
    return None


def send_photo(chat_id, photo_file, caption=""):
    url = f"{BASE_URL}/sendPhoto"
    data = {"chat_id": chat_id, "caption": caption}
    files = {"photo": photo_file}
    response = requests.post(url, data=data, files=files)
    return response.json()


def process_image(image_bytes):
    # باز کردن تصویر از بایت
    input_image = Image.open(io.BytesIO(image_bytes))
    # تنظیم اندازه عکس برای کاهش مصرف حافظه (مثلاً حداکثر عرض/ارتفاع 800 پیکسل)
    # حذف پس‌زمینه با rembg
    output_image = remove(input_image)
    img_byte_arr = io.BytesIO()
    output_image.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    return img_byte_arr


def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    response = requests.post(url, json=payload)
    return response.json()


offset = None
while True:
    updates = get_updates(offset)
    if updates.get("ok"):
        for update in updates.get("result", []):
            offset = update["update_id"] + 1
            message = update.get("message")
            if message:
                text = message.get("text", "")
            if text.strip == "/start":
                chat_id = message["chat"]["id"]
                send_message(chat_id, "سلام! برای حذف پسزمینه عکس بفرستید.")
            if not message:
                continue
            chat_id = message["chat"]["id"]
            if "photo" in message:
                photo_list = message["photo"]
                target_photo = sorted(
                    photo_list, key=lambda x: x.get("file_size", 0), reverse=True
                )[0]
                file_id = target_photo["file_id"]
                image_data = download_file(file_id)
                if image_data:
                    try:
                        processed_image = process_image(image_data)
                        response = send_photo(
                            chat_id, processed_image, caption="پس‌زمینه عکس حذف شده است"
                        )
                        print("ارسال عکس با موفقیت:", response)
                    except Exception as e:
                        print("خطا در پردازش عکس:", e)
    time.sleep(2)
