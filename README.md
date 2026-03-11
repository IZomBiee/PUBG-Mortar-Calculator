# PUBG Mortar Calculator

A tool to calculate the range of a shot for mortar in PUBG.

## Features

- [X] Quick calculation of planar distance between marks
- [X] Quick calculation of firing range of a mortar
- [X] Quick сalculation of planar distance using mini-map
- [X] GUI
- [X] Overlay
- [X] Dictor
- [ ] Calculating the distance of an airdrop 
- [ ] Realtime calculation

## Preview

### GUI Preview (v4.0.0)
![GUI Preview](assets/app_preview.jpg)

### Ingame Minimap Preview
![Ingame Minimap Preview](assets/ingame_minimap_preview.gif)

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

## Using
1. Setup hotkeys for calculation.
2. Use both hotkeys to get map/minimap image and elevation image. (Elevation image must be from mortar first-person view on mark)
3. Enable visualization of grid and marks.
4. Play with settings!

## Things to know
- The minimap detection is not ideal so it can detect something different or not detect anything. It will be improved in feature but it mostly work fine. So if you have time use full map which is more precise and stable.
- The mark detection system using dump algorithm, it detect circle with the max radious in range. Because of that it can detect something different but with precise tunning it work in most cases.
- Don't work with HDR or other things that change color like color blind mode or gpu driver tweaks.
- The bot is not designed for fullscreen mode, better use borderless, which doesn't impact performance. But if you will - overlay will not work and if image is stretcht grid detection will give incorect results.
- If debug mode enabled than all calculation results and images can be checked in last.log and loaded in program if needed to check what cause problem.
- If you use it, please write what is wrong and what can be improved. I will try to fix it.