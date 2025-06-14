## 🌡️ GrovePi+ Sensor Dashboard

A PyQt-based desktop application for Raspberry Pi designed to interface with GrovePi+ sensors. This project provides a responsive GUI for real-time monitoring and control of connected sensors including DHT temperature & humidity, digital buttons, relays, and more.

Repository: [https://github.com/gr4ytips/seeedstudio.git](https://github.com/gr4ytips/seeedstudio.git)

---

### 📌 Project Overview

This dashboard is tailored for **educational and prototyping** use on **Raspberry Pi 3B or 4B** running **Raspbian Stretch or Buster**, due to legacy support constraints of the Dexter Industries GrovePi+ library.

Using `PyQt5`, the app provides visual feedback from connected Grove sensors and control over outputs like relays. It's ideal for learning IoT basics, Raspberry Pi interfacing, and Python GUI development.

---

### 🧰 Features

- Real-time sensor display for DHT (temperature & humidity)
- Relay and buzzer control with simple button interface
- GPIO interaction for push-buttons and LEDs
- Analog visualization (light, sound, rotary)
- Distance measurement with ultrasonic sensor
- PyQt5 GUI optimized for low-resource Pi devices
- Uses the GrovePi library from Dexter Industries

---

### 🔧 Hardware Requirements

- Raspberry Pi 3B or 4B (Recommended)
- GrovePi+ board by seedstudio
- Grove Sensors:
  - DHT11/DHT22: **D2**
  - Digital Button: **D3**
  - Relay Module: **D4**
  - LED Bar: **D5**
  - Ultrasonic Ranger: **D7**
  - Buzzer: **D8**
  - Rotary Angle Sensor: **A0**
  - Sound Sensor: **A1**
  - Light Sensor: **A2**

---

### 💻 Software Requirements

- Raspbian Stretch or Buster OS ([Raspberry Pi OS Buster 2023-05-03](https://downloads.raspberrypi.com/raspios_oldstable_armhf/images/raspios_oldstable_armhf-2023-05-03/))
- Python 3.5+ (3.7 recommended on Buster)
- Dependencies:
  - `pyqt5` (older versions compatible with Python 3.5)
  - `grovepi` library from Dexter Industries

---

### ⚙️ Installation Instructions

1. **Update Your Raspberry Pi**
   ```bash
   sudo apt-get update && sudo apt-get upgrade
   ```

2. **Install GrovePi Library (Recommended Method)**
   Use the official Dexter script to install dependencies and firmware:
   ```bash
   curl -kL dexterindustries.com/update_grovepi | bash
   sudo reboot
   ```
   Alternatively, follow manual steps:
   ```bash
   git clone https://github.com/DexterInd/GrovePi.git
   cd GrovePi/Software/Python
   sudo python3 setup.py install
   ```
   For more info: [GrovePi Script README](https://github.com/DexterInd/GrovePi/blob/master/Script/README.md)

3. **Clone the Dashboard Repository**
   ```bash
   git clone https://github.com/gr4ytips/seeedstudio.git
   cd seeedstudio/GrovePiPlus
   ```

4. **Install Python GUI Dependencies**
   ```bash
   sudo apt-get install python3-pyqt5
   ```

5. **Run the App**
   ```bash
   python3 main.py
   ```

---

### 🚨 Disclaimer & Liability

> ⚠️ **WARNING**: This project is provided **for educational purposes only**. No warranties or guarantees are made regarding the accuracy, performance, or reliability of this software or hardware configurations. Improper use of hardware (e.g., relay modules) may pose **electrical risks**. Use at your own risk.

---

### 📄 License

This work is licensed under a  
[Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).

[![CC BY-NC 4.0](https://licensebuttons.net/l/by-nc/4.0/88x31.png)](https://creativecommons.org/licenses/by-nc/4.0/)

---

### 📢 Blog Article Summary

> **GrovePi+ Sensor Dashboard on Raspberry Pi: A Beginner's IoT GUI**
>
> Learn how to create a responsive GUI using PyQt5 to visualize and control Grove sensors connected to Raspberry Pi. This open-source dashboard, developed for educational use, bridges the gap between low-level GPIO handling and user-friendly interfaces. Ideal for classrooms, STEM workshops, or hobby projects.
