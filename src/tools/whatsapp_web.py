from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os, time


def debug_ancestors(elem):
    for i in range(15):
        try:
            role = elem.get_attribute("role")
            tag = elem.tag_name
            classes = elem.get_attribute("class")
            print(f"Level {i}: {tag} - role={role}, class={classes}")
            elem = elem.find_element(By.XPATH, "./..")
        except Exception as e:
            print(f"DOM climb broke at level {i}: {e}")
            break


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
        print(f"Searching for chat: {target_name}")
        # Find all editable fields (likely only one or two)
        input_boxes = self.driver.find_elements(By.XPATH, "//div[@contenteditable='true']")
        search_box = None
        for box in input_boxes:
            aria = (box.get_attribute("aria-label") or "").lower()
            if "search" in aria:
                search_box = box
                break
        if not search_box:
            search_box = input_boxes[0]
        search_box.click()
        search_box.clear()
        time.sleep(0.5)
        search_box.send_keys(target_name)
        time.sleep(2)
        # Try to find all chat elements and find the best (longest matching) title
        chat_spans = self.driver.find_elements(By.XPATH, "//span[@title]")
        available_titles = [span.get_attribute("title") for span in chat_spans]
        print("Available WhatsApp contact titles:", available_titles)
        # Find best matching contact name (case-insensitive, contains or equals)
        matches = [t for t in available_titles if t.lower().startswith(target_name.lower()) or target_name.lower() in t.lower()]
        if not matches:
            raise Exception(f"No WhatsApp contact found matching '{target_name}'! Options: {available_titles}")
        chat = self.driver.find_element(By.XPATH, f"//span[@title='{matches[0]}']")
        chat.click()
        print(f"Chat '{matches[0]}' found and opened.")
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
        badges = self.driver.find_elements(By.XPATH, "//span[contains(@aria-label, 'unread message')]")
        print(f"Found {len(badges)} unread badges (new selector).")
        chats = []
        for badge in badges:
            try:
                parent = badge.find_element(
                    By.XPATH, "./ancestor::div[@role='listitem'][1]"
                )
                chats.append(parent)
                print("Found unread chat for click (via ancestor axis)!")
            except Exception as e:
                print("Could not find listitem ancestor via XPath axis:", e)
        return chats



    def read_latest_message_from_chat(self, chat_element):
        self.driver.execute_script("arguments[0].scrollIntoView(true);", chat_element)
        chat_element.click()
        print("Clicked unread chat. Waiting for messages to load...")
        time.sleep(2)  # Optionally reduce if performance is good

        # Wait for the chat header to appear (max 5s)
        try:
            header_span = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "header span[title]"))
            )
            contact_name = header_span.get_attribute("title")
        except Exception as e:
            print(f"Could not find chat header span: {e}")
            contact_name = "Unknown"

        last_msgs = self.driver.find_elements(By.CSS_SELECTOR, "div.message-in")
        if not last_msgs:
            print("No incoming message found!")
            return contact_name, ""
        last_msg = last_msgs[-1]
        text = last_msg.text
        print(f"Read message from: {contact_name} - '{text}'")
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
