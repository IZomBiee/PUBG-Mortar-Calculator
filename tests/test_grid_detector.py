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
        self.grid_detector = GridDetector(20, 40, 1700, 250, 3840)
        
    def test_get_grid_gap(self):
        for sample in self.test_samples:
            image = cv2.imread(f'tests/test_samples/{sample['image_name']}')
            self.grid_detector.detect_lines(image)
            gap = self.grid_detector.get_grid_gap()
            self.assertAlmostEqual(sample['grid_gap'][0], gap[0], delta=3, msg=f'tests/test_samples/{sample['image_name']}')
            self.assertAlmostEqual(sample['grid_gap'][1], gap[1], delta=3, msg=f'tests/test_samples/{sample['image_name']}')

if __name__ == '__main__':
    unittest.main()
    