# PUBG Mortar Calculator

A tool to calculate the range of a shot with mortar in PUBG. This app provides a GUI interface, integrates screen capturing, and supports AI-based minimap detection for faster calculations.

## Features

- Calculate the range of a mortar shot.
- Support simple elevation calculation,
- Works with multiple monitors.
- Minimap detection using YOLO.

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/IZomBiee/PUBG-Mortar-Calculator.git
cd PUBG-Mortar-Calculator
```

2. **Run with poetry:**
```bash
poetry install
poetry run pubg_mortar_calculator
```

3. **Install minimap detection model: (Optional)**
Download minimap detection model from this repository releases and add that .onnx file to assets folder. After that you can enable minimap detection in program gui.

## Using
1. Setup hotkeys for calculation.
2. Use both hotkeys to get map/minimap image and elevation image. (Elevation image must be from mortar first-person view on mark)
3. Enable visualization of grid and marks.
4. Play with settings!