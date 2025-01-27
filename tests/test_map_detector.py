import unittest
import cv2
import json
import os

from pubg_mortar_calculator.map_detector import MapDetector

class TestGridDetector(unittest.TestCase):
    def setUp(self):
        self.test_samples = []
        for file in os.listdir('tests/test_samples/'):
            if file.endswith('.json'):
                with open(f'tests/test_samples/{file}', 'r') as file:
                    self.test_samples.append(json.load(file))
        self.map_detector = MapDetector([3840, 2160])
        
    def test_get_grid_gap(self):
        for sample in self.test_samples:
            image = cv2.imread(f'tests/test_samples/{sample['image_name']}')
            self.assertEqual(self.map_detector.is_minimap(image), sample['minimap'], msg=f'tests/test_samples/{sample['image_name']}')

if __name__ == '__main__':
    unittest.main()
    