import unittest
import cv2
import json
import os

from pubg_mortar_calculator.grid_detector import GridDetector, raiseGridDetector

class TestGridDetector(unittest.TestCase):
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
        
    def test_get_grid_gap(self):
        for sample in self.test_samples:
            print(f"Image: {sample['name']}.png Sample: {sample} ", end='')

            image = cv2.imread(f'tests/test_samples/{sample['name']}.png')

            self.grid_detector.detect_lines(image)
            gap = self.grid_detector.get_grid_gap()
            print(f"Grid Gap: {gap}")
            
            try:
                self.assertAlmostEqual(sample['grid_gap'], gap, delta=3, msg="Gap isn't correct")
            except AssertionError as e:
                raiseGridDetector(image)
                raise AssertionError(e)

if __name__ == '__main__':
    unittest.main()
    