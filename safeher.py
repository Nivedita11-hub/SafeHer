import tkinter as tk
import geocoder
from datetime import datetime
import webbrowser
import cv2
import sounddevice as sd
from scipy.io.wavfile import write
import requests
from requests.auth import HTTPBasicAuth

# ==============================
# SAFEHER SETTINGS
# ==============================

SECRET_CODE = "9999"

ACCOUNT_SID = "AC9d634eaf757ad881777745d47d0335aa"
AUTH_TOKEN = "c4e533e396b6b524ef3286c1a5148ca2"

TWILIO_NUMBER = "+13012351088"
TARGET_NUMBER = "+917558680079"

# ==============================
# SEND SMS USING TWILIO API
# ==============================

def send_sms(message):

    url = f"https://api.twilio.com/2010-04-01/Accounts/{ACCOUNT_SID}/Messages.json"

    data = {
        "From": TWILIO_NUMBER,
        "To": TARGET_NUMBER,
        "Body": message
    }

    response = requests.post(
        url,
        data=data,
        auth=HTTPBasicAuth(ACCOUNT_SID, AUTH_TOKEN)
    )

    print("SMS status:", response.status_code)


# ==============================
# RECORD AUDIO
# ==============================

def record_audio():

    duration = 5
    fs = 44100

    print("Recording audio evidence...")

    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()

    write("evidence_audio.wav", fs, recording)

    print("Audio saved")


# ==============================
# CAPTURE WEBCAM PHOTO
# ==============================

def capture_photo():

    cam = cv2.VideoCapture(0)

    ret, frame = cam.read()

    if ret:
        cv2.imwrite("evidence_photo.jpg", frame)
        print("Photo captured")

    cam.release()


# ==============================
# ALERT FUNCTION
# ==============================

def send_alert(trigger):

    print("ALERT TRIGGERED:", trigger)

    g = geocoder.ip('me')
    location = g.latlng

    if location is None:
        location = ["Unknown", "Unknown"]

    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lat = location[0]
    lon = location[1]

    maps_link = f"https://www.google.com/maps?q={lat},{lon}"

    # Evidence collection
    record_audio()
    capture_photo()

    alert_message = f"""
SAFEHER EMERGENCY ALERT

Trigger: {trigger}

Time: {time}

Location: {location}

Google Maps:
{maps_link}

User may be in danger.
"""

    print(alert_message)

    # Save log
    with open("alert_log.txt", "a") as f:
        f.write(alert_message + "\n")

    # Send SMS
    send_sms(alert_message)

    # Open Google Maps
    webbrowser.open(maps_link)


# ==============================
# CALCULATOR FUNCTIONS
# ==============================

expression = ""

def press(num):
    global expression
    expression += str(num)
    equation.set(expression)

def equal():

    global expression

    if expression == SECRET_CODE:
        open_dashboard()
        expression = ""
        equation.set("")
        return

    try:
        result = str(eval(expression))
        equation.set(result)
        expression = result
    except:
        equation.set("error")
        expression = ""

def clear():
    global expression
    expression = ""
    equation.set("")


# ==============================
# HIDDEN DASHBOARD
# ==============================

def open_dashboard():

    dash = tk.Toplevel(root)
    dash.title("SafeHer Dashboard")
    dash.geometry("320x200")

    tk.Label(dash,text="SafeHer Hidden Dashboard",font=("Arial",14)).pack(pady=15)

    tk.Button(
        dash,
        text="Trigger Emergency SOS",
        command=lambda:send_alert("Manual SOS"),
        height=2
    ).pack(pady=10)

    tk.Button(dash,text="Close",command=dash.destroy).pack()


# ==============================
# SHAKE TRIGGER
# ==============================

def shake_trigger(event):

    print("Shake detected")
    send_alert("Shake Gesture")


# ==============================
# CALCULATOR UI
# ==============================

root = tk.Tk()
root.title("Calculator")
root.geometry("300x400")

equation = tk.StringVar()

entry = tk.Entry(root,textvariable=equation,font=("Arial",20),bd=10)
entry.pack(fill="both")

buttons = [
('7','8','9','/'),
('4','5','6','*'),
('1','2','3','-'),
('0','.','=','+')
]

for row in buttons:

    frame = tk.Frame(root)
    frame.pack(expand=True,fill="both")

    for btn in row:

        action = lambda x=btn: press(x) if x!='=' else equal()

        tk.Button(frame,text=btn,font=("Arial",18),command=action).pack(
            side="left",expand=True,fill="both"
        )

tk.Button(root,text="C",font=("Arial",18),command=clear).pack(fill="both")

# Press S to simulate phone shake
root.bind('s',shake_trigger)

root.mainloop()


