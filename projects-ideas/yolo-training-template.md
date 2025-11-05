# YOLO Training Template

**Repository:** https://github.com/mfranzon/yolo-training-template

## 📋 Description

Ready-to-use template for training YOLO models on any Kaggle datasets in just a few hours (example: road pothole detection). Requires only about 100 lines of Python code! Can train even on a regular laptop (~1 hour training).

Includes scripts, notebook examples, documentation, and dataset lists.

## 🎯 Unique Features

- **Extremely low entry barrier** — Even beginners can build a working CV application prototype in one day.

- **Automatic labeling submodule** using GroundingDINO — allows creating annotated datasets without manual work!

- **Support for typical scenarios**: road pothole detection, signs, faces, animals, license plates, medical images, etc.

## 🚀 Why It Stands Out

- All main stages (download, auto-labeling, training, inference) in one simple framework.

- Minimal "glue code" — entire pipeline executable in one notebook.

- Perfect for rapid prototyping, hackathons, practical ML startup "on a laptop in a day".

## 📹 Demonstration

Real-time detection of potholes (potholes) on roads from car video — bounding boxes with confidence. Practically production-ready prototype for road companies, IoT cameras, public civil applications.

## 💡 Conclusion

Mini-template in Python for training and running YOLO on your own datasets, with auto-labeling module. Main value — radical simplicity and universality: anyone can learn to make their own CV inferences in just a few hours without deep ML knowledge or GPU servers.

## 📦 Files Structure

- `scripts/main.py`: Command-line script for training YOLO on a Kaggle dataset.
- `scripts/inference.py`: Command-line script for running inference with a trained model.
- `notebooks/yolo_template.ipynb`: Notebook template to run train a YOLO model and test it.
- `docs/CONTRIBUTING.md`: Contributing guidelines.
- `example_datasets.md`: List of example Kaggle datasets for testing.

## 🛠️ Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. For training: Run `python scripts/main.py --dataset <kaggle-handle> --nc <num-classes> --names <class-names>`
3. For inference: Run `python scripts/inference.py --model <model-path> --input <image/video/webcam>`

---

*Template repository with tips and templates to train YOLO models for any kind of computer vision application.*

