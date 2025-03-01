# AdhanCast (Ramadan Edition)

A Windows GUI app to schedule and play Fajr, Maghrib, and Isha Adhan on Google Nest Mini/Chromecast during Ramadan. Future updates will include all prayer times but this version is simply aimed for Ramadan reminders.

## Features
- **Automated Adhan Scheduler**: Plays Fajr, Maghrib, and Isha Adhan daily.
- **Google Nest Mini Support**: Cast Adhan via Google Cast.
- **Flask Server Hosting**: Serves Adhan MP3 files locally.
- **Preloaded Prayer Times**: Uses `prayer_times.json` for prayer timings in Newfoundland.
- **Minimal Setup**: Install dependencies, run the EXE file, and click'Start Scheduling'!
- **System Tray Mode**: Runs silently in the Windows system tray even if you exit the window.

## Technologies Used
- **Python**: Core Language
- **Tkinter**: GUI creation
- **Flask**: Hosts Adhan MP3 files
- **pychromecast**: Casts Adhan
- **schedule**: Automates Adhan playback
- **pystray**: System tray functionality
- **PyInstaller**: Converts script to executable

## Installation & Setup
1. **Clone or Download the Repository**
    ```sh
    git clone https://github.com/ammar-15/AdhanCast.git
    cd AdhanCast
    ```

2. **Install Dependencies**
    Ensure Python (3.8+ recommended) is installed, then:
    ```sh
    pip install pychromecast flask schedule pystray pillow
    ```

3. **Ensure Required Files Exist**
    Make sure these files in the same directory as `adhan_gui.py`:
    - `adhan.mp3`: Adhan audio.
    - `fajradhan.mp3`: Fajr Adhan audio.
    - `prayer_times.json`: Preloaded Ramadan prayer times for Newfoundland.

    Example `prayer_times.json` format:
    ```json
    [
      {"date": "01-03-2025", "fajr": "05:17", "maghrib": "17:47", "isha": "19:12"},
      {"date": "02-03-2025", "fajr": "05:14", "maghrib": "17:48", "isha": "19:13"}
    ]
    ```

## Running the EXE Application
1. **Build the EXE**
    ```sh
    pyinstaller --noconsole --onefile --collect-submodules=zeroconf --add-data "adhan.mp3;." --add-data "fajradhan.mp3;." --add-data "prayer_times.json;." adhan_gui.py
    ```

2. **Open the EXE**
    - Navigate to the `dist/` folder inside the AdhanCast folder.
    - Open `adhan_gui.exe`.
    - Select your device and start the scheduler. You can exit out of the GUI window and also exit your IDE/Command Prompt.

## Troubleshooting
- **Chromecast Won’t Play Adhan**
    - Check Flask Hosting: Open `http://192.168.x.x:5000/adhan` in a browser.
    - Restart Google Nest Mini.
    - Allow Python in Windows Firewall.

- **EXE Doesn’t Work After Building**
    - Run the EXE from CMD:
    ```sh
    cd dist
    adhan_gui.exe
    ```
    - Manually copy `adhan.mp3`, `fajradhan.mp3`, and `prayer_times.json` to the same folder as `adhan_gui.exe`.

## Future Updates & Enhancements
- **Mac Version**: Develop a macOS-compatible version.
- **All Prayer Times**: Include all five daily prayers.
- **Multi-Device Casting**: Simultaneous playback on multiple devices.
- **Multi-City Support**: Select different cities and fetch correct prayer times.

## License
This project is open-source, free to use and open to contribution.

## Contact
For help, open an issue or contact me at https://www.linkedin.com/in/ammarfaruqui/
