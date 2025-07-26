import unittest
import cv2
import json
import os

from pubg_mortar_calculator.grid_detector import GridDetector

class TestGridDetector(unittest.TestCase):
    def setUp(self):
        self.test_samples = []
        for file in os.listdir('tests/test_samples/'):
            if file.endswith('.json'):
                with open(f'tests/test_samples/{file}', 'r') as file:
                    self.test_samples.append(json.load(file))
        with open('settings.json', 'r') as file:
            self.settings = json.load(file)

        self.grid_detector = GridDetector()
        
    def test_get_grid_gap(self):
        for sample in self.test_samples:
            print(f"Image: {sample['name']}.png Sample: {sample} ", end='')

            image = cv2.imread(f'tests/test_samples/{sample['name']}.png')

            self.grid_detector.detect_lines(self.grid_detector.get_canny_frame(image,
                self.settings["Canny 1 Threshold"], self.settings["Canny 2 Threshold"]),
                self.settings["Line Threshold"], self.settings["Line Gap"])
            gap = self.grid_detector.get_grid_gap(self.settings["Gap Threshold"])
            print(f"Grid Gap: {gap}")
            
            self.assertAlmostEqual(sample['grid_gap'], gap, delta=3, msg="Gap isn't correct")

if __name__ == '__main__':
    unittest.main()
    