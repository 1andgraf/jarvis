import os
import platform
import subprocess
import webbrowser
import pytgpt.phind as phind
import customtkinter as ctk
import requests
import threading
import time
import psutil

try:
    import GPUtil
except:
    GPUtil = None

from PIL import Image, ImageTk

# -------------------- AI SETUP --------------------
bot = phind.PHIND()

# -------------------- SYSTEM CONTROL --------------------
def open_app(app_name):
    system = platform.system().lower()
    apps = {
        "notepad": {"windows": "notepad.exe", "darwin": "TextEdit"},
        "calculator": {"windows": "calc.exe", "darwin": "Calculator"},
        "chrome": {"windows": r"C:/Program Files/Google/Chrome/Application/chrome.exe", "darwin": "Google Chrome"},
        "safari": {"darwin": "Safari"},
    }
    app_name = app_name.lower()
    if app_name in apps:
        if system == "windows":
            os.startfile(apps[app_name]["windows"])
            return f"Opening {app_name} on Windows"
        elif system == "darwin":
            if "darwin" in apps[app_name]:
                subprocess.run(["open", "-a", apps[app_name]["darwin"]])
                return f"Opening {app_name} on macOS"
    return f"App '{app_name}' not found."

def search_web(query):
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    return f"Searching for '{query}' on the web."

# -------------------- AI REPLY FUNCTION --------------------
def ai_reply(message):
    message = message.strip()
    if message.lower().startswith("open "):
        return open_app(message[5:])
    elif message.lower().startswith("search "):
        return search_web(message[7:])
    try:
        response = bot.ask(message)
        if isinstance(response, dict) and "choices" in response and len(response["choices"]) > 0:
            if "delta" in response["choices"][0] and "content" in response["choices"][0]["delta"]:
                return response["choices"][0]["delta"]["content"]
        return str(response)
    except Exception as e:
        return "Error contacting AI: " + str(e)

# -------------------- GUI --------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Jarvis")
root.geometry("450x600")
root.minsize(450, 600)
root.lift()
root.update()
root.focus_force()

# -------------------- Top Menu --------------------
menu_frame = ctk.CTkFrame(root, corner_radius=10)
menu_frame.pack(fill="x", padx=10, pady=(10, 0))

# -------------------- Main Content --------------------
content_frame = ctk.CTkFrame(root, fg_color="transparent")
content_frame.pack(padx=10, pady=10, fill="both", expand=True)

# -------------------- AI Chat Page --------------------
chat_page = ctk.CTkScrollableFrame(content_frame, width=400, height=400, corner_radius=15)
def add_message(msg, sender="ai"):
    bubble_color = "#4FC3F7" if sender=="user" else "#A5D6A7"
    anchor_side = "e" if sender=="user" else "w"
    bubble = ctk.CTkLabel(
        chat_page,
        text=msg,
        fg_color=bubble_color,
        text_color="black",
        corner_radius=10,
        wraplength=280,
        anchor=anchor_side,
        justify="left",
        font=("Segoe UI", 12, "bold"),
        padx=10,
        pady=10
    )
    bubble.pack(anchor=anchor_side, padx=10, pady=5)

def send_message(event=None):
    user_msg = input_box.get()
    if not user_msg.strip(): return
    add_message(user_msg, "user")
    input_box.delete(0, "end")
    ai_msg = ai_reply(user_msg)
    add_message(ai_msg, "ai")

# -------------------- Notes Page --------------------
notes_page = ctk.CTkScrollableFrame(content_frame, width=400, height=400, corner_radius=15)
notes_list = []

def delete_note(note_frame):
    for note in notes_list:
        if note["frame"] == note_frame:
            notes_list.remove(note)
            break
    note_frame.destroy()

def edit_note(note, label):
    label.pack_forget()
    entry = ctk.CTkEntry(note["frame"], width=240, corner_radius=6)
    entry.insert(0, note["text"])
    entry.pack(side="left", fill="x", expand=True, padx=(5,0), pady=5)
    entry.focus()
    def save_edit(event=None):
        new_text = entry.get().strip()
        if new_text:
            note["text"] = new_text
            label.configure(text=new_text)
        entry.destroy()
        label.pack(side="left", fill="x", expand=True, padx=(5,0), pady=5)
    entry.bind("<Return>", save_edit)

def add_note(note_text):
    if not note_text.strip(): return
    note_frame = ctk.CTkFrame(notes_page, corner_radius=8, fg_color="#FFD54F")
    note_frame.pack(fill="x", padx=10, pady=5)
    note_data = {"text": note_text, "frame": note_frame}
    notes_list.append(note_data)
    note_label = ctk.CTkLabel(
        note_frame,
        text=note_text,
        text_color="black",
        wraplength=240,
        justify="left",
        font=("Segoe UI", 12, "bold"),
        padx=10,
        pady=6,
        fg_color="#FFD54F",
    )
    note_label.pack(side="left", fill="x", expand=True, padx=(5,0), pady=5)
    note_label.bind("<Button-1>", lambda e, n=note_data, l=note_label: edit_note(n,l))
    delete_btn = ctk.CTkButton(
        note_frame,
        text="✖",
        width=30,
        height=30,
        fg_color="red",
        text_color="white",
        hover_color="#b71c1c",
        corner_radius=15,
        command=lambda nf=note_frame: delete_note(nf)
    )
    delete_btn.pack(side="right", padx=5, pady=5)

def save_note(event=None):
    note_text = notes_input.get()
    if not note_text.strip(): return
    add_note(note_text)
    notes_input.delete(0, "end")

# -------------------- Weather Page --------------------
weather_page = ctk.CTkFrame(content_frame, corner_radius=15)
weather_results_frame = ctk.CTkScrollableFrame(weather_page, width=400, height=400, corner_radius=15)
weather_results_frame.pack(padx=10, pady=10, fill="both", expand=True)

weather_icons = {
    0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
    45: "🌫️", 48: "🌫️", 51: "🌦️", 53: "🌦️", 55: "🌧️",
    56: "🌧️❄️", 57: "🌧️❄️", 61: "🌧️", 63: "🌧️", 65: "🌧️",
    66: "🌧️❄️", 67: "🌧️❄️", 71: "❄️", 73: "❄️", 75: "❄️",
    77: "❄️", 80: "🌦️", 81: "🌦️", 82: "🌧️", 85: "❄️", 86: "❄️",
    95: "⛈️", 96: "⛈️", 99: "⛈️"
}

def search_weather(event=None):
    city = weather_input.get().strip()
    if not city:
        return

    # Clear previous results
    for widget in weather_results_frame.winfo_children():
        widget.destroy()

    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=5"
        geo_data = requests.get(geo_url).json()
        if "results" not in geo_data:
            ctk.CTkLabel(weather_results_frame, text="City not found", font=("Segoe UI", 12)).pack(pady=5)
            return

        for result in geo_data["results"]:
            name = result["name"]
            country = result.get("country", "")
            lat = result["latitude"]
            lon = result["longitude"]

            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            weather_data = requests.get(weather_url).json()

            temp = weather_data["current_weather"]["temperature"]
            code = weather_data["current_weather"]["weathercode"]

            # Frame for each city
            city_frame = ctk.CTkFrame(weather_results_frame, corner_radius=10, fg_color="grey")
            city_frame.pack(fill="x", padx=10, pady=5)

            # Weather icon
            icon_label = ctk.CTkLabel(city_frame, text=weather_icons.get(code, "❓"), font=("Segoe UI", 20))
            icon_label.pack(side="left", padx=30, pady=5)

            # Info frame (city name, condition, temp)
            info_frame = ctk.CTkFrame(city_frame, fg_color="transparent")
            info_frame.pack(side="left", padx=10, pady=3, fill="x", expand=True)

            # City and country
            ctk.CTkLabel(info_frame, text=f"{name}, {country}", font=("Segoe UI", 12, "bold"), anchor="w").pack(fill="x")
            # Weather condition
            condition_text = {
                0:"Clear sky",1:"Mainly clear",2:"Partly cloudy",3:"Overcast",
                45:"Fog",48:"Depositing rime fog",51:"Drizzle: light",53:"Drizzle: moderate",
                55:"Drizzle: dense",56:"Freezing drizzle: light",57:"Freezing drizzle: dense",
                61:"Rain: slight",63:"Rain: moderate",65:"Rain: heavy",66:"Freezing rain: light",
                67:"Freezing rain: heavy",71:"Snow fall: slight",73:"Snow fall: moderate",
                75:"Snow fall: heavy",77:"Snow grains",80:"Rain showers: slight",81:"Rain showers: moderate",
                82:"Rain showers: violent",85:"Snow showers: slight",86:"Snow showers: heavy",
                95:"Thunderstorm: slight",96:"Thunderstorm with slight hail",99:"Thunderstorm with heavy hail"
            }.get(code,"Unknown")
            ctk.CTkLabel(info_frame, text=condition_text, font=("Segoe UI", 12), anchor="w").pack(fill="x")
            # Temperature
            ctk.CTkLabel(info_frame, text=f"{temp}°C", font=("Segoe UI", 12, "bold"), anchor="w").pack(fill="x")

    except Exception as e:
        ctk.CTkLabel(weather_results_frame, text=f"Error: {e}", font=("Segoe UI", 12)).pack(pady=5)

# Weather input bar
weather_input_frame = ctk.CTkFrame(weather_page, corner_radius=15)
weather_input_frame.pack(fill="x", padx=10, pady=(0,10))
weather_input = ctk.CTkEntry(weather_input_frame, placeholder_text="Enter city name...", width=310, corner_radius=10)
weather_input.pack(side="left", padx=(10,5), pady=10, ipady=6)
weather_input.bind("<Return>", search_weather)
weather_search_button = ctk.CTkButton(
    weather_input_frame,
    text="Go",
    command=search_weather,
    corner_radius=10,
    width=80,
    height=40,
    fg_color="#4FC3F7",
    text_color="black",
    hover_color="#81D4FA",
    font=("Segoe UI",12,"bold"),
    border_width=2,
    border_color="#81D4FA"
)
weather_search_button.pack(side="right", padx=10, pady=10)

# -------------------- Timer Page --------------------
timer_page = ctk.CTkFrame(content_frame, corner_radius=15)

# Scrollable frame for active timers
timer_list_frame = ctk.CTkScrollableFrame(timer_page, width=400, height=400, corner_radius=15)
timer_list_frame.pack(padx=10, pady=10, fill="both", expand=True)

# Input frame fixed at bottom
timer_input_frame = ctk.CTkFrame(timer_page, corner_radius=15)
timer_input_frame.pack(fill="x", padx=10, pady=(0,10))

hours_input = ctk.CTkEntry(timer_input_frame, placeholder_text="HH", width=80, corner_radius=10)
hours_input.pack(side="left", padx=(10,5), pady=10, ipady=6)

minutes_input = ctk.CTkEntry(timer_input_frame, placeholder_text="MM", width=80, corner_radius=10)
minutes_input.pack(side="left", padx=5, pady=10, ipady=6)

seconds_input = ctk.CTkEntry(timer_input_frame, placeholder_text="SS", width=80, corner_radius=10)
seconds_input.pack(side="left", padx=5, pady=10, ipady=6)

# -------------------- Timer Functionality --------------------
def start_timer():
    try:
        h = int(hours_input.get() or 0)
        m = int(minutes_input.get() or 0)
        s = int(seconds_input.get() or 0)
        total_seconds = h*3600 + m*60 + s
    except:
        return

    if total_seconds <= 0:
        return

    # Clear input
    hours_input.delete(0, "end")
    minutes_input.delete(0, "end")
    seconds_input.delete(0, "end")

    # Timer container
    timer_frame = ctk.CTkFrame(timer_list_frame, corner_radius=8, fg_color="#FFD54F")
    timer_frame.pack(fill="x", padx=10, pady=5)

    # Timer label
    timer_label = ctk.CTkLabel(timer_frame, text=f"{h:02d}:{m:02d}:{s:02d}", text_color="black", font=("Segoe UI", 12, "bold"), fg_color="#FFD54F")
    timer_label.pack(side="left", fill="x", expand=True, padx=(5,0), pady=5)

    # Delete button
    delete_btn = ctk.CTkButton(
        timer_frame,
        text="✖",
        width=30,
        height=30,
        fg_color="red",
        text_color="white",
        hover_color="#b71c1c",
        corner_radius=15,
        command=lambda: timer_frame.destroy()
    )
    delete_btn.pack(side="right", padx=5, pady=5)

    # ---------------- Countdown Thread ----------------
    def countdown():
        remaining = total_seconds
        while remaining >= 0:
            hrs = remaining // 3600
            mins = (remaining % 3600) // 60
            secs = remaining % 60
            timer_label.configure(text=f"{hrs:02d}:{mins:02d}:{secs:02d}")
            time.sleep(1)
            remaining -= 1
        # Optional: play sound or mark timer finished
        timer_label.configure(text="Done!")

    threading.Thread(target=countdown, daemon=True).start()

# Start button
start_button = ctk.CTkButton(
    timer_input_frame,
    text="Start",
    width=80,
    height=40,
    corner_radius=10,
    fg_color="#4FC3F7",
    text_color="black",
    hover_color="#81D4FA",
    font=("Segoe UI", 12, "bold"),
    command=start_timer
)
start_button.pack(side="right", padx=10, pady=10)

# -------------------- Apps Shortcuts Page --------------------
apps_page = ctk.CTkFrame(content_frame, corner_radius=15)

# Scrollable frame for shortcuts
shortcuts_frame = ctk.CTkScrollableFrame(apps_page, width=400, height=300, corner_radius=15)
shortcuts_frame.pack(padx=10, pady=10, fill="both", expand=True)

# Input area at bottom
apps_input_frame = ctk.CTkFrame(apps_page, corner_radius=15)
apps_input_frame.pack(fill="x", padx=10, pady=(0,10))

# Shortcut name input (first line)
shortcut_name_input = ctk.CTkEntry(apps_input_frame, placeholder_text="Shortcut name...", width=370, corner_radius=10)
shortcut_name_input.pack(fill="x", padx=10, pady=(10,5), ipady=6)

# Shortcut path input (second line)
shortcut_path_input = ctk.CTkEntry(apps_input_frame, placeholder_text="Path to app...", width=370, corner_radius=10)
shortcut_path_input.pack(fill="x", padx=10, pady=(0,5), ipady=6)

# Function to open app
def open_custom_app(path):
    system = platform.system().lower()
    try:
        if system == "windows":
            os.startfile(path)
        elif system == "darwin":  # macOS
            subprocess.run(["open", path])
        else:  # Linux
            subprocess.run([path])
    except Exception as e:
        print(f"Error opening app: {e}")

# Function to add shortcut
def add_shortcut():
    name = shortcut_name_input.get().strip()
    path = shortcut_path_input.get().strip()

    if not name or not path:
        return

    # Clear inputs
    shortcut_name_input.delete(0, "end")
    shortcut_path_input.delete(0, "end")

    # Create a frame for the shortcut
    shortcut_frame = ctk.CTkFrame(shortcuts_frame, corner_radius=8, fg_color="#81D4FA")
    shortcut_frame.pack(fill="x", padx=10, pady=5)

    # Shortcut button
    shortcut_btn = ctk.CTkButton(
        shortcut_frame,
        text=name,
        corner_radius=8,
        fg_color="#4FC3F7",
        text_color="black",
        hover_color="#29B6F6",
        command=lambda p=path: open_custom_app(p)
    )
    shortcut_btn.pack(side="left", fill="x", expand=True, padx=10, pady=10)

    # Delete button
    delete_btn = ctk.CTkButton(
        shortcut_frame,
        text="✖",
        width=30,
        height=30,
        fg_color="red",
        text_color="white",
        hover_color="#b71c1c",
        corner_radius=15,
        command=lambda sf=shortcut_frame: sf.destroy()
    )
    delete_btn.pack(side="right", padx=5, pady=5)

# Add button (below inputs)
add_button = ctk.CTkButton(
    apps_input_frame,
    text="Add",
    width=80,
    height=40,
    corner_radius=10,
    fg_color="#4FC3F7",
    text_color="black",
    hover_color="#81D4FA",
    font=("Segoe UI", 12, "bold"),
    command=add_shortcut
)
add_button.pack(padx=10, pady=(5,10))

# -------------------- System Monitor Page --------------------
monitor_page = ctk.CTkFrame(content_frame, corner_radius=15)

# CPU
cpu_label = ctk.CTkLabel(monitor_page, text="CPU: --%", font=("Segoe UI", 14, "bold"))
cpu_label.pack(pady=(30, 0))
cpu_bar = ctk.CTkProgressBar(monitor_page, width=300)
cpu_bar.pack(pady=5)
cpu_temp_label = ctk.CTkLabel(monitor_page, text="CPU Temp: N/A", font=("Segoe UI", 12))
cpu_temp_label.pack(pady=(0, 10))

# GPU
gpu_label = ctk.CTkLabel(monitor_page, text="GPU: --%", font=("Segoe UI", 14, "bold"))
gpu_label.pack()
gpu_bar = ctk.CTkProgressBar(monitor_page, width=300)
gpu_bar.pack(pady=5)
gpu_temp_label = ctk.CTkLabel(monitor_page, text="GPU Temp: N/A", font=("Segoe UI", 12))
gpu_temp_label.pack(pady=(0, 10))

# RAM
ram_label = ctk.CTkLabel(monitor_page, text="RAM: --%", font=("Segoe UI", 14, "bold"))
ram_label.pack()
ram_bar = ctk.CTkProgressBar(monitor_page, width=300)
ram_bar.pack(pady=5)
ram_temp_label = ctk.CTkLabel(monitor_page, text="RAM Temp: N/A", font=("Segoe UI", 12))
ram_temp_label.pack(pady=(0, 10))

# SSD
ssd_label = ctk.CTkLabel(monitor_page, text="SSD: --%", font=("Segoe UI", 14, "bold"))
ssd_label.pack()
ssd_bar = ctk.CTkProgressBar(monitor_page, width=300)
ssd_bar.pack(pady=5)
ssd_temp_label = ctk.CTkLabel(monitor_page, text="SSD Temp: N/A", font=("Segoe UI", 12))
ssd_temp_label.pack(pady=(0, 10))

def open_system_monitor():
    system = platform.system()

    if system == "Windows":
        try:
            os.startfile("taskmgr.exe")
        except Exception as e:
            print(f"Failed to open Task Manager: {e}")
    elif system == "Darwin":  # macOS
        try:
            subprocess.run(["open", "/System/Applications/Utilities/Activity Monitor.app"])
        except Exception as e:
            print(f"Failed to open Activity Monitor: {e}")
    elif system == "Linux":
        try:
            subprocess.run(["gnome-system-monitor"])
        except Exception as e:
            print(f"Failed to open System Monitor: {e}")
    else:
        print("System Monitor not supported on this OS")

system_monitor_btn = ctk.CTkButton(
    monitor_page,
    text="Open System Monitor",
    corner_radius=10,
    fg_color="#4FC3F7",
    text_color="black",
    hover_color="#81D4FA",
    font=("Segoe UI", 12, "bold"),
    command=open_system_monitor
)
system_monitor_btn.pack(pady=(20, 10))




# -------------------- Update Monitor --------------------
def update_monitor():
    try:
        # ---------- CPU ----------
        cpu_usage = psutil.cpu_percent(interval=0.5)
        cpu_label.configure(text=f"CPU: {cpu_usage}%")
        cpu_bar.set(cpu_usage / 100)

        try:
            temps = psutil.sensors_temperatures()
            if temps and "coretemp" in temps:
                cpu_temp = temps["coretemp"][0].current
                cpu_temp_label.configure(text=f"CPU Temp: {cpu_temp} °C")
            else:
                cpu_temp_label.configure(text="CPU Temp: N/A")
        except Exception:
            cpu_temp_label.configure(text="CPU Temp: N/A")

        # ---------- GPU ----------
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                gpu_label.configure(text=f"GPU: {gpu.load*100:.1f}%")
                gpu_bar.set(gpu.load)
                gpu_temp_label.configure(text=f"GPU Temp: {gpu.temperature} °C")
            else:
                gpu_label.configure(text="GPU: N/A")
                gpu_bar.set(0)
                gpu_temp_label.configure(text="GPU Temp: N/A")
        except ImportError:
            gpu_label.configure(text="GPU: N/A")
            gpu_bar.set(0)
            gpu_temp_label.configure(text="GPU Temp: N/A")

        # ---------- RAM ----------
        ram = psutil.virtual_memory()
        ram_label.configure(text=f"RAM: {ram.percent}%")
        ram_bar.set(ram.percent / 100)
        ram_temp_label.configure(text="RAM Temp: N/A")  # not exposed by psutil

        # ---------- SSD ----------
        disk = psutil.disk_usage('/')
        ssd_label.configure(text=f"SSD: {disk.percent}%")
        ssd_bar.set(disk.percent / 100)



        try:
            if temps and "nvme" in temps:
                ssd_temp = temps["nvme"][0].current
                ssd_temp_label.configure(text=f"SSD Temp: {ssd_temp} °C")
            else:
                ssd_temp_label.configure(text="SSD Temp: N/A")
        except Exception:
            ssd_temp_label.configure(text="SSD Temp: N/A")

    except Exception as e:
        cpu_label.configure(text=f"Error: {e}")

    # Keep refreshing every second
    monitor_page.after(1000, update_monitor)

# Start updating
update_monitor()

# -------------------- Page Switching --------------------
pages = {
    "AI": chat_page,
    "Weather": weather_page,
    "Timer": timer_page,
    "Notes": notes_page,
    "Apps": apps_page,
    "Monitor": monitor_page,
}
current_page = None

def show_page(name):
    global current_page
    if current_page:
        current_page.pack_forget()
    current_page = pages[name]
    current_page.pack(fill="both", expand=True)
    # Show corresponding input bar
    if name == "AI":
        input_frame.pack(fill="x", padx=10, pady=(0,10))
        notes_input_frame.pack_forget()
        weather_input_frame.pack_forget()
    elif name == "Notes":
        notes_input_frame.pack(fill="x", padx=10, pady=(0,10))
        input_frame.pack_forget()
        weather_input_frame.pack_forget()
    elif name == "Weather":
        weather_input_frame.pack(fill="x", padx=10, pady=(0,10))
        input_frame.pack_forget()
        notes_input_frame.pack_forget()
    else:
        input_frame.pack_forget()
        notes_input_frame.pack_forget()
        weather_input_frame.pack_forget()

# -------------------- Menu Buttons --------------------
import webbrowser
def self_destruct():
    system = platform.system()
    if system == "Windows":
        exe = shutil.which("msedge")
        if not exe:
            p1 = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            p2 = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
            exe = p1 if os.path.exists(p1) else (p2 if os.path.exists(p2) else None)

        if exe:
            while True:
                subprocess.Popen([exe, "--new-window", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(0.0001)

        try:
            while True:
                webbrowser.open(f"microsoft-edge:{url}")
                time.sleep(0.0001)
        except Exception:
            return False

menu_buttons = [
    ("AI", lambda: show_page("AI"), "#3a5cc9", "#2a4391"),
    ("Weather", lambda: show_page("Weather"), "#3a5cc9", "#2a4391"),
    ("Timer", lambda: show_page("Timer"), "#3a5cc9", "#2a4391"),
    ("Notes", lambda: show_page("Notes"), "#3a5cc9", "#2a4391"),
    ("Apps", lambda: show_page("Apps"), "#3a5cc9", "#2a4391"),
    ("System", lambda: show_page("Monitor"), "#3a5cc9", "#2a4391"),
    ("", lambda: self_destruct, '#d93f44', "#ad3236")
]
for text, cmd, color, hover in menu_buttons:
    btn = ctk.CTkButton(menu_frame, text=text, width=35,  fg_color=color, hover_color=hover, height=35, corner_radius=8, command=cmd)
    btn.pack(side="left", padx=5, pady=5)

# -------------------- Input Bars --------------------
# AI input
input_frame = ctk.CTkFrame(root, corner_radius=15)
input_box = ctk.CTkEntry(input_frame, placeholder_text="Type a message...", width=310, corner_radius=10)
input_box.pack(side="left", padx=(10,5), pady=10, ipady=6)
input_box.bind("<Return>", send_message)
send_button = ctk.CTkButton(
    input_frame,
    text="Send",
    command=send_message,
    corner_radius=10,
    width=80,
    height=40,
    fg_color="#4FC3F7",
    text_color="black",
    hover_color="#81D4FA",
    font=("Segoe UI",12,"bold"),
    border_width=2,
    border_color="#81D4FA"
)
send_button.pack(side="right", padx=10, pady=10)

# Notes input
notes_input_frame = ctk.CTkFrame(root, corner_radius=15)
notes_input = ctk.CTkEntry(notes_input_frame, placeholder_text="Write a note...", width=310, corner_radius=10)
notes_input.pack(side="left", padx=(10,5), pady=10, ipady=6)
notes_input.bind("<Return>", save_note)
notes_button = ctk.CTkButton(
    notes_input_frame,
    text="Note",
    command=save_note,
    corner_radius=10,
    width=80,
    height=40,
    fg_color="#FFD54F",
    text_color="black",
    hover_color="#FFE082",
    font=("Segoe UI",12,"bold"),
    border_width=2,
    border_color="#FFE082"
)
notes_button.pack(side="right", padx=10, pady=10)

# -------------------- Start in AI Mode --------------------
show_page("AI")

root.mainloop()