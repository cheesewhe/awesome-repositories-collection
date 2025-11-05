# Raspberry Pi 5 Hailo-8 Pothole Detection System

**Repository:** https://github.com/lukekratz/raspberry-pi-5-hailo-8-pothole-detection-system

## 📋 Description

Official repository for automatic pothole detection, classification and sizing system. Uses machine vision and a YOLOv8 model accelerated by the Hailo-8 chip to detect, classify, and estimate the size of potholes in real time. The system runs on a Raspberry Pi 5 with the Hailo AI HAT+ and a Raspberry Pi AI Camera.

## 🎯 Key Features

- **Real-time pothole detection** using YOLOv8 model
- **Hardware acceleration** via Hailo-8 AI chip
- **Classification and sizing** of detected potholes
- **Raspberry Pi 5 optimized** for edge computing
- **GPS logging** capabilities for location tracking

## 🚀 Quick Start

### Install Hailo Drivers & SDK on Raspberry Pi 5

Follow the official guide to install the Hailo AI Software Suite for Raspberry Pi: [Hailo-RPi5-Examples](https://github.com/hailo-ai/hailo-rpi5-examples)

### Clone the Hailo Example Repository

```bash
git clone https://github.com/hailo-ai/hailo-rpi5-examples.git
cd hailo-rpi5-examples
```

### Clone this repository

```bash
cd ~/hailo-rpi5-examples/basic_pipelines/
git clone https://github.com/YOUR_USERNAME/pothole-detection-system.git
cd pothole-detection-system
```

### Run the detection pipeline

```bash
python3 pothole_detection.py --input rpi --hef-path ~/path-to-hef-file/Pothole-YOLOv8.hef
```

## 🛠️ Hardware Requirements

- Raspberry Pi 5
- Hailo AI HAT+ (AI accelerator)
- Raspberry Pi AI Camera

## 💡 Use Cases

- **Road maintenance** — Automated detection and reporting of road defects
- **Civil infrastructure monitoring** — Large-scale road condition assessment
- **Edge AI applications** — Real-time processing without cloud dependencies
- **IoT solutions** — Deployable detection systems for smart cities

## 📊 Project Structure

- `pothole_detection.py` — Main detection script
- `pothole_hailo_benchmark.py` — Performance benchmarking
- `log_gps_info.py` — GPS logging functionality
- Camera calibration files for accurate measurements

---

*Production-ready system for automatic pothole detection, classification and sizing using edge AI on Raspberry Pi 5 with Hailo-8 acceleration.*

