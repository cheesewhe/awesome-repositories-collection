# car-counter

**Repository:** https://github.com/serialdotai/car-counter

## 📋 Description

car-counter is a free open-source Python project for automatic vehicle counting in video streams using computer vision. Built on modern CV tools, specifically optimized for analyzing traffic camera feeds. Uses a combination of YOLOv8 (neural object detector) and SORT algorithm for tracking objects between frames.

## 🎯 Key Features

- **Object Detection**: Uses YOLOv8 model for detecting cars in each video frame.

- **Object Tracking**: Implements SORT (Simple Online and Realtime Tracking) algorithm to track specific vehicles between frames, avoiding double counting.

- **Vehicle Counting**: System counts vehicles that cross predefined lines marked on the video (e.g., entry/exit lines at intersections).

- **Visualization**: Outputs processed video with graphical overlays: vehicle count, visualization of virtual lines and movement directions.

- **Flexible Configuration**: Set line positions for counting, load masks (regions of interest) to focus on specific parts of the frame.

- **Result Output**: Final video with counted vehicles saved as result.mp4. Reports saved in logs.

## 📦 Requirements & Installation

- Ultralytics YOLO
- OpenCV (cv2)
- cvzone
- SORT

```bash
git clone https://github.com/serialdotai/car-counter.git
cd car-counter
pip install -r requirements.txt
# Copy yolov8l.pt (weights) to the appropriate directory
python main.py
```

Recommended: Python ≥3.8

## 🚀 Use Cases

- **Urban planners, transportation engineers** — Monitor road traffic
- **Traffic researchers** — Collect statistics for intersections and highways
- **City and regional administrations** — Automatic traffic analysis
- **CV developers** — Simple open-source tracker for getting started
- **IoT/Edge AI experiments** with video analytics

## 💡 Typical Scenarios

- Automated analysis of vehicle flow on city streets and intersections
- Traffic statistics collection and road congestion graphs
- Speed limit monitoring (average speed calculation)
- Quick prototype for CV integration in transportation projects

---

*car-counter is a minimalistic, practical open-source script for automating video analysis from traffic cameras. Excellent choice for object counting tasks when you need to quickly deploy Python-based analytics without heavy pipelines and frameworks.*

