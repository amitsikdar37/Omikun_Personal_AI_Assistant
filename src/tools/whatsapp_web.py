from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os, time

class WhatsAppWeb:
    def __init__(self):
        chrome_options = Options()
        # Save profile OUTSIDE your project repo and VSCode directory!
        profile_path = os.path.expanduser("~/.omikun_whatsapp_profile")
        chrome_options.add_argument(f"--user-data-dir={profile_path}")

        # Robust flags for compatibility
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        # Create profile dir if not exists
        if not os.path.exists(profile_path):
            os.makedirs(profile_path)

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.driver.get("https://web.whatsapp.com")
        print("Scan the QR code if this is your first run...")
        time.sleep(20)  # User logs in

    def search_and_open_chat(self, target_name):
    # Sometimes WhatsApp Web no longer uses data-testid='chat-list-search'
    # Let's look for a top visible editable input
        time.sleep(1)
        input_boxes = self.driver.find_elements(By.XPATH, "//div[@contenteditable='true']")
        search_box = None
        for box in input_boxes:
            try:
                aria = box.get_attribute("aria-label") or ""
                # Looks for one that says "Search input" or just first one on left
                if "search" in aria.lower() or "search" in (box.get_attribute("data-tab") or ""):
                    search_box = box
                    break
            except Exception:
                continue
        # Fallback: just take the first (main) one
        if not search_box:
            search_box = input_boxes[0]
        search_box.click()
        search_box.clear()
        search_box.send_keys(target_name)
        time.sleep(2)
        # Find chat with exact title
        chat = self.driver.find_element(By.XPATH, f"//span[@title='{target_name}']")
        chat.click()
        time.sleep(1)


    def send_message_to_contact(self, contact, message):
        print(f"Trying to send to {contact}: {message}")
        self.search_and_open_chat(contact)
        time.sleep(1)  # Ensure chat is open before sending
        try:
            input_box = self.driver.find_element(By.XPATH, "//div[@contenteditable='true' and starts-with(@aria-label, 'Type to ')]")
        except Exception:
            boxes = self.driver.find_elements(By.XPATH, "//div[@contenteditable='true']")
            input_box = boxes[-1]
        input_box.click()
        input_box.send_keys(message + Keys.ENTER)
        print("Message sent in browser.")
        time.sleep(1)

    def get_unread_chats(self):
        # Locate the unread (new message) badge in chats
        chats = self.driver.find_elements(By.CSS_SELECTOR, "span[data-testid='icon-unread-count']")
        results = []
        for badge in chats:
            outer = badge.find_element(By.XPATH, "../../..")
            results.append(outer)
        return results

    def read_latest_message_from_chat(self, chat_element):
        chat_element.click()
        time.sleep(1)
        last_msg = self.driver.find_elements(By.CSS_SELECTOR, "div.message-in")[-1]
        text = last_msg.text
        contact_name = self.driver.find_element(By.CSS_SELECTOR, "header span[title]").get_attribute("title")
        return contact_name, text

    def send_message(self, text):
        time.sleep(1)
        try:
            input_box = self.driver.find_element(By.XPATH, "//div[@contenteditable='true' and starts-with(@aria-label, 'Type to ')]")
            input_box.click()
            input_box.clear()  # Safe to call, but not required, as it should be empty
            input_box.send_keys(text + Keys.ENTER)
            print("Message sent in browser.")
            time.sleep(1)
        except Exception as e:
            print("Failed to send message:", e)
            raise

    def auto_reply_loop(self, ai_callback, stop_check=lambda: False):
        print("Auto-reply mode on.")
        recent_ids = set()
        while not stop_check():
            unread_chats = self.get_unread_chats()
            for chat in unread_chats:
                sender, msg = self.read_latest_message_from_chat(chat)
                msg_id = (sender, msg)
                if msg_id in recent_ids:
                    continue
                reply = ai_callback(sender, msg)
                self.send_message(reply)
                recent_ids.add(msg_id)
            time.sleep(5)
        print("Auto-reply mode off.")

    def close(self):
        self.driver.quit()
