import pychromecast
import json
import schedule
import threading
import time
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext, ttk
from PIL import Image, ImageDraw
import pystray
from flask import Flask, send_file
import socket
import os


# CONFIGURATION
def get_local_ip():
    """Finds the actual local network IP (192.168.x.x) for Flask hosting."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)) 
        local_ip = s.getsockname()[0]  
        s.close()
        return local_ip
    except Exception as e:
        print(f"⚠️ Error getting local IP: {e}")
        return "127.0.0.1"  

LOCAL_IP = get_local_ip()
ADHAN_URL = f"http://{LOCAL_IP}:5000/adhan"
FAJR_ADHAN_URL = f"http://{LOCAL_IP}:5000/fajradhan"
PRAYER_TIMES_FILE = os.path.join(os.path.dirname(__file__), "prayer_times.json")
RUNNING = False
selected_device = None  

# FLASK SERVER TO SERVE ADHAN FILES
app = Flask(__name__)

@app.route('/adhan')
def serve_adhan():
    return send_file("adhan.mp3", mimetype="audio/mp3")

@app.route('/fajradhan')
def serve_fajr_adhan():
    return send_file("fajradhan.mp3", mimetype="audio/mp3")

def run_flask():
    """Runs the Flask server on the detected local IP."""
    app.run(host=LOCAL_IP, port=5000, debug=False, use_reloader=False)


# LOAD PRAYER TIMES
def load_prayer_times():
    try:
        with open(PRAYER_TIMES_FILE, "r") as file:
            data = json.load(file)
            log_message(f"📂 Loaded prayer times successfully: {len(data)} entries found.")
            return data
    except Exception as e:
        log_message(f"⚠️ Error loading prayer times: {e}")
        return []

# FIND & LIST ALL CASTING DEVICES
def get_cast_devices():
    """Finds all Chromecast devices on the network."""
    chromecasts, _ = pychromecast.get_chromecasts()
    return [cast.name for cast in chromecasts] if chromecasts else []

# CONNECT TO SELECTED DEVICE
def find_cast_device():
    """Connects to the selected Chromecast device."""
    global selected_device
    if not selected_device:
        log_message("❌ No Chromecast selected. Please select a device first.")
        return None

    chromecasts, _ = pychromecast.get_chromecasts()
    for cast in chromecasts:
        if cast.name == selected_device:
            cast.wait()
            return cast
    
    log_message(f"❌ Could not find '{selected_device}'. Ensure it's on & on WiFi.")
    return None

# PLAY ADHAN (DIFFERENT FOR FAJR)
def play_adhan(prayer):
    """Plays the Adhan on the selected Chromecast device."""
    cast = find_cast_device()
    if not cast:
        log_message(f"❌ Chromecast device '{selected_device}' not found or offline.")
        return

    mc = cast.media_controller
    adhan_url = FAJR_ADHAN_URL if prayer.lower() == "fajr" else ADHAN_URL

    log_message(f"🔊 Sending {'Fajr' if prayer.lower() == 'fajr' else 'Regular'} Adhan to {selected_device}...")

    try:
        log_message("⏳ Loading Adhan on Chromecast...")
        mc.play_media(adhan_url, "audio/mp3", autoplay=True)  

        log_message("⏳ Waiting for Chromecast to start playing...")
        time.sleep(5) 

        log_message(f"🎵 Chromecast Status: {mc.status.player_state}")

        if mc.status.player_state in ["IDLE", "UNKNOWN"]:
            log_message("⚠️ Chromecast is idle. Forcing playback...")
            mc.play()  
            time.sleep(2)  

        log_message(f"🎵 Final Status: {mc.status.player_state}")
        if mc.status.player_state == "PLAYING":
            log_message("✅ Adhan is now playing!")
        else:
            log_message(f"⚠️ Chromecast did not start playing. Final status: {mc.status.player_state}")

    except Exception as e:
        log_message(f"⚠️ Error playing Adhan: {e}")


# SCHEDULING ADHAN TIMES
def schedule_prayer_times():
    """Schedules Adhan for today's prayer times."""
    prayer_times = load_prayer_times()
    today_date = datetime.today().strftime("%d-%m-%Y")

    for entry in prayer_times:
        if entry["date"] == today_date:
            for prayer in ["fajr", "maghrib", "isha"]:
                if prayer in entry:
                    schedule.every().day.at(entry[prayer]).do(play_adhan, prayer)
                    log_message(f"✅ Scheduled {prayer.capitalize()} Adhan at {entry[prayer]}")
            return

    log_message(f"⚠️ No prayer times found for {today_date}. Check your JSON file.")

# BACKGROUND THREAD FOR SCHEDULER
def run_scheduler():
    global RUNNING
    schedule_prayer_times() 
    RUNNING = True
    log_message("✅ Running Adhan Scheduler...")

    while RUNNING:
        try:
            jobs = schedule.get_jobs()
            if not jobs:
                log_message("⚠️ No scheduled jobs found. Check your prayer_times.json file.")
            else:
                time.sleep(10)

            schedule.run_pending()
        except Exception as e:
            log_message(f"⚠️ Scheduler Error: {e}")


# START & STOP FUNCTIONS
def start_scheduler():
    """Starts the scheduled Adhan playback."""
    global scheduler_thread, RUNNING

    if RUNNING:
        log_message("⚠️ Scheduler is already running.")
        return

    log_message("🔄 Starting Adhan Scheduler...")

    RUNNING = True
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    log_message("🚀 Scheduler thread started successfully.")


def stop_scheduler():
    """Stops the scheduled Adhan playback."""
    global RUNNING
    log_message("⏸️ Stopping Adhan Scheduler...")
    RUNNING = False

# GUI: LOG MESSAGES
def log_message(msg):
    text_area.insert(tk.END, msg + "\n")
    text_area.see(tk.END)

# CREATE SYSTEM TRAY ICON
def create_icon():
    """Creates an icon for the system tray"""
    icon_size = (64, 64)
    image = Image.new('RGB', icon_size, (255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.ellipse((5, 5, 59, 59), fill=(0, 122, 204))
    return image

def restore_window(icon, item):
    """Restores the main window when clicked from the tray"""
    root.after(0, root.deiconify)

def exit_app(icon, item):
    """Stops everything and exits the app"""
    stop_scheduler()
    icon.stop()
    root.quit()

def minimize_to_tray():
    """Minimizes the app to system tray instead of closing"""
    root.withdraw()  
    log_message("🔽 Minimized to system tray. Right-click the tray icon to restore.")

def run_tray_icon():
    """Runs the system tray icon in a separate thread"""
    menu = (
        pystray.MenuItem("Open", restore_window),
        pystray.MenuItem("Start", lambda icon, item: start_scheduler()),
        pystray.MenuItem("Stop", lambda icon, item: stop_scheduler()),
        pystray.MenuItem("Exit", exit_app)
    )

    tray_icon = pystray.Icon("AdhanScheduler", create_icon(), menu=menu)
    tray_icon.run()

# GUI WINDOW
root = tk.Tk()
root.title("Adhan Scheduler")
root.geometry("400x350")

# Override Close Button (X) to Minimize Instead
root.protocol("WM_DELETE_WINDOW", minimize_to_tray)

# Dropdown for Selecting Google Home Device
devices = get_cast_devices()
device_label = tk.Label(root, text="Select Casting Device:", font=("Arial", 12))
device_label.pack(pady=5)
device_dropdown = ttk.Combobox(root, values=devices, state="readonly")
device_dropdown.pack(pady=5)
if devices:
    device_dropdown.current(0)  
    selected_device = devices[0]

def update_selected_device(event):
    """Updates the selected Chromecast device"""
    global selected_device
    selected_device = device_dropdown.get()
    log_message(f"📡 Selected Device: {selected_device}")

device_dropdown.bind("<<ComboboxSelected>>", update_selected_device)

# Start Button
start_button = tk.Button(root, text="Start Scheduler", command=start_scheduler, bg="green", fg="white", font=("Arial", 12))
start_button.pack(pady=10)

# Stop Button
stop_button = tk.Button(root, text="Stop Scheduler", command=stop_scheduler, bg="red", fg="white", font=("Arial", 12))
stop_button.pack(pady=5)

# Log Output
text_area = scrolledtext.ScrolledText(root, width=50, height=10)
text_area.pack(pady=10)

# START FLASK SERVER & SYSTEM TRAY ICON
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()
tray_thread = threading.Thread(target=run_tray_icon, daemon=True)
tray_thread.start()

# START GUI LOOP
root.mainloop()
