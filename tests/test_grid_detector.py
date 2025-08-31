import cv2

from pubg_mortar_calculator.sample_loader import SampleLoader
from pubg_mortar_calculator.detectors import GridDetector, MapDetector
from pubg_mortar_calculator.settings_loader import SettingsLoader

grid_detector = GridDetector()
map_detector = MapDetector()
settings = SettingsLoader()

deltas = []

sample_loader = SampleLoader()
sample_loader.load()
for sample in sample_loader:
    correct_grid_gap = sample['data']['grid_gap']
    map_image = sample['map_image']

    detections = map_detector.detect(map_image)
    if len(detections):
        map_image = map_detector.cut_to_map(map_image)
        
    processed_map_image = grid_detector.get_canny_frame(
        map_image, settings.get('grid_detection_canny1_threshold_slider'),
        settings.get('grid_detection_canny2_threshold_slider')
    )

    grid_detector.detect_lines(processed_map_image,
        settings.get('grid_detection_line_threshold_slider')/100,
        settings.get('grid_detection_line_gap_slider')/100)
    
    gap = grid_detector.calculate_grid_gap(
        settings.get('grid_detection_gap_threshold_slider'))
    delta = abs(correct_grid_gap - gap)
    print(f'{sample['path']}: {correct_grid_gap} - {gap} = {delta}')
    deltas.append(delta)

print(f'Delta Max: {max(deltas)} Min: {min(deltas)} Avg: {sum(deltas)/len(deltas)}')