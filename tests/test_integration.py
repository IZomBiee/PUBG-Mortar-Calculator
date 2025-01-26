import unittest
import cv2
import json
import os

from pubg_mortar_calculator.utils import *
from pubg_mortar_calculator.grid_detector import GridDetector
from pubg_mortar_calculator.mark_detector import MarkDetector

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.test_samples = []
        for file in os.listdir('tests/test_samples/'):
            if file.endswith('.json'):
                with open(f'tests/test_samples/{file}', 'r') as file:
                    self.test_samples.append(json.load(file))
        self.grid_detector = GridDetector(20, 40, 1700, 160, 3840)
        self.mark_detector = MarkDetector('orange', 35)
    
    def test_distance(self):
        for sample in self.test_samples:
            image = cv2.imread(f'tests/test_samples/{sample['image_name']}')
            self.grid_detector.detect_lines(image)
            self.mark_detector.load_color(sample['color'])
            gap = self.grid_detector.get_grid_gap()
            player_cord, mark_cord = self.mark_detector.get_cords(image) 

            correct_distance = GridDetector.get_distance(sample['player_cord'], sample['mark_cord'], sample['grid_gap'])
            distance = GridDetector.get_distance(player_cord, mark_cord, gap)
            self.assertAlmostEqual(correct_distance, distance, delta=20, msg=(
                 f'Image: tests/test_samples/{sample['image_name']} Distance: {correct_distance} Calculated Distance: {distance} '
                 f'Player Cord: {sample['player_cord']} Calculated Player Cord: {player_cord} '
                 f'Mark Cord: {sample['mark_cord']} Calculated Mark Cord: {mark_cord} '
                 f'Grid Gap: {sample['grid_gap']} Calculated Grid Gap: {gap} '))

if __name__ == '__main__':
    unittest.main()