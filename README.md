# 🚗 AI Driver Monitoring System
### An Intelligent AI-Powered Driver Safety and Behaviour Monitoring Platform

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-Backend-black?logo=flask" />
  <img src="https://img.shields.io/badge/OpenCV-Computer%20Vision-green?logo=opencv" />
  <img src="https://img.shields.io/badge/MediaPipe-Face%20Landmarks-blue" />
  <img src="https://img.shields.io/badge/YOLO-Object%20Detection-purple" />
</p>

---

## 📌 Overview

The **AI Driver Monitoring System** is an intelligent driver safety application that uses Artificial Intelligence, Computer Vision and Deep Learning to monitor driver behaviour and identify potentially unsafe driving activities in real time.

The system focuses on detecting driver drowsiness, distraction, yawning and mobile phone usage to help improve road safety and reduce the risk of accidents.

By combining facial landmark analysis and object detection techniques, the application aims to provide an intelligent monitoring solution for safer driving.

## ✨ Key Features

- 😴 **Drowsiness Detection** – Identifies signs of driver fatigue and sleepiness.
- 👁️ **Eye Monitoring** – Analyses facial landmarks and eye-related behaviour.
- 🥱 **Yawning Detection** – Identifies yawning as a possible indicator of fatigue.
- 📱 **Mobile Phone Detection** – Detects mobile phone usage while driving.
- 🚘 **Distraction Monitoring** – Identifies potentially distracting driver behaviour.
- 🔔 **Alert Mechanism** – Provides warnings when unsafe behaviour is detected.
- 📊 **Dashboard Interface** – Provides an interface for monitoring and accessing application features.
- 🔐 **User Authentication** – Supports user registration and login.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application development |
| Flask | Backend framework |
| OpenCV | Image processing and computer vision |
| MediaPipe | Facial landmark detection |
| YOLO | Real-time object detection |
| NumPy | Numerical computations |
| Flask-CORS | Cross-origin resource sharing |
| Twilio | Notification integration |
| HTML, CSS, JavaScript | Frontend development |

## 🧠 System Workflow

1. **Video Input:** Captures the driver's activity through a camera.
2. **Frame Processing:** Processes video frames using OpenCV.
3. **Facial Analysis:** Uses MediaPipe facial landmarks to analyse driver behaviour.
4. **Object Detection:** Uses YOLO-based detection for identifying relevant objects.
5. **Behaviour Monitoring:** Analyses driver activity for signs of fatigue and distraction.
6. **Alert Generation:** Provides warnings when potentially unsafe behaviour is identified.
7. **Dashboard Display:** Presents the monitoring interface to the user.

## 🏗️ Project Architecture

The project is organised into three main components:

- **Frontend:** Provides the user interface, authentication pages and monitoring dashboard.
- **Backend:** Handles application logic, server-side processing and communication.
- **Models:** Contains the trained AI models and supporting detection resources.

## 📁 Repository Structure

```text
AI-Driver-Monitoring-System/
│
├── backend/
│   └── Backend source code
│
├── frontend/
│   └── Frontend source code
│
├── models/
│   └── AI detection models
│
├── README.md
│
└── requirements.txt
```

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.x
- Git
- Webcam or camera access
- A modern web browser

### Step 1: Clone the Repository

```bash
git clone https://github.com/kavya05-ks/AI-Driver-Monitoring-System.git
```

### Step 2: Navigate to the Project

```bash
cd AI-Driver-Monitoring-System
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure the Application

Configure the required environment variables, camera permissions and notification credentials, if applicable.

### Step 5: Run the Application

Start the backend and frontend using their respective application entry points.

Refer to the source files for the exact execution commands.

## 🎯 Applications

- Intelligent transportation systems
- Driver safety monitoring
- Drowsiness and fatigue detection
- Real-time vehicle safety applications
- Accident prevention research

## 🔮 Future Enhancements

- Improved detection accuracy in different lighting conditions.
- Advanced driver behaviour analysis.
- Enhanced real-time notification mechanisms.
- Cloud-based monitoring and analytics.
- Integration with intelligent vehicle safety systems.

## 👩‍💻 Author

**Kavya**

AI Driver Monitoring System

---

<p align="center">
  <b>Building Safer Roads Through Artificial Intelligence.</b>
</p>

<p align="center">
  ⭐ If you find this project interesting, consider giving this repository a star!
</p>
