from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

class WhatsAppWeb:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--user-data-dir=./chrome_profile")  # Save login
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        print("WhatsApp Web initialized")
    
    def login(self):
        """Open WhatsApp Web and wait for QR scan"""
        self.driver.get("https://web.whatsapp.com")
        print("Please scan QR code to login...")
        
        # Wait for main page to load (after QR scan)
        try:
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='chat-list']")))
            print("WhatsApp Web logged in successfully!")
            return True
        except:
            print("Login failed or timed out")
            return False
    
    def send_message(self, contact_name, message):
        """Send message to a contact"""
        try:
            # Search for contact
            search_box = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='chat-list-search']")))
            search_box.clear()
            search_box.send_keys(contact_name)
            time.sleep(2)
            
            # Click on first result
            contact = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='cell-frame-container']")))
            contact.click()
            
            # Type message
            message_box = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='conversation-compose-box-input']")))
            message_box.clear()
            message_box.send_keys(message)
            
            # Send message
            send_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='send']")
            send_button.click()
            
            print(f"Message sent to {contact_name}: {message}")
            return True
            
        except Exception as e:
            print(f"Failed to send message: {e}")
            return False
    
    def close(self):
        """Close browser"""
        self.driver.quit()
