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
        with open('settings.json', 'r') as file:
            settings = json.load(file)

        self.grid_detector = GridDetector(settings["canny1_threshold"], settings["canny2_threshold"],
                                        settings["line_threshold"], settings["line_gap"], settings["merge_threshold"])
        self.mark_detector = MarkDetector([3840, 2160])
    
    def test_distance(self):
        for sample in self.test_samples:
            print(f"Image: {sample['name']}.png Sample: {sample}")

            image = cv2.imread(f'tests/test_samples/{sample['name']}.png')
            self.grid_detector.detect_lines(image)
            self.mark_detector.load_color(sample['color'])
            gap = self.grid_detector.get_grid_gap()
            player_cord, mark_cord = self.mark_detector.get_cords(image) 

            correct_distance = GridDetector.get_distance(sample['player_position'], sample['mark_position'], sample['grid_gap'])
            distance = GridDetector.get_distance(player_cord, mark_cord, gap)
            self.assertAlmostEqual(correct_distance, distance, delta=10, msg=(
                 f'Image: tests/test_samples/{sample['name']} Distance: {correct_distance} Calculated Distance: {distance}\n'
                 f'Player Cord: {sample['player_position']} Calculated Player Cord: {player_cord}\n'
                 f'Mark Cord: {sample['mark_position']} Calculated Mark Cord: {mark_cord}\n'
                 f'Grid Gap: {sample['grid_gap']} Calculated Grid Gap: {gap}\n'
                 f'Color: {sample['color']}\n'))

if __name__ == '__main__':
    unittest.main()