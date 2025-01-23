import unittest
import cv2
import json

from pubg_mortar_calculator.grid_detector import GridDetector

class TestGridDetector(unittest.TestCase):
    def setUp(self):
        with open('tests/test_samples/annotation.json', 'r') as file:
                    self.test_samples = json.load(file)
        
    def test_get_grid_gap(self):
        grid_detector = GridDetector(20, 40, 1700, 250, 3840)
        for sample in self.test_samples:
            image = cv2.imread(f'tests/test_samples/{sample['name']}')
            grid_detector.detect_lines(image)
            gap = grid_detector.get_grid_gap()
            self.assertAlmostEqual(sample['grid_gap'][0], gap[0], delta=3, msg=f'tests/test_samples/{sample['name']}')
            self.assertAlmostEqual(sample['grid_gap'][1], gap[1], delta=3, msg=f'tests/test_samples/{sample['name']}')

if __name__ == '__main__':
    unittest.main()