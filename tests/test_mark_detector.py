import unittest
import cv2
import json
import os

from pubg_mortar_calculator.mark_detector import MarkDetector

class TestMarkDetector(unittest.TestCase):
    def setUp(self):
        self.test_samples = []
        for file in os.listdir('tests/test_samples/'):
            if file.endswith('.json'):
                with open(f'tests/test_samples/{file}', 'r') as file:
                    self.test_samples.append(json.load(file))
        self.mark_detector = MarkDetector()
        
    def test_get_cords(self):
        for sample in self.test_samples:
            print(f"Image: {sample['name']}.png Sample: {sample} ", end='')

            image = cv2.imread(f'tests/test_samples/{sample['name']}.png')

            player_cord, mark_cord = self.mark_detector.get_mark_positions(
                self.mark_detector.get_hsv_mask(image, sample['color']), 35)
            print(f"Player Position: {player_cord} Mark Position: {mark_cord}")

            self.assertAlmostEqual(sample['player_position'][0], player_cord[0], delta=5, msg=f"Player position X isn't correct")
            self.assertAlmostEqual(sample['player_position'][1], player_cord[1], delta=5, msg=f"Player position Y isn't correct")
            self.assertAlmostEqual(sample['mark_position'][0], mark_cord[0], delta=5, msg=f"Mark position X isn't correct")
            self.assertAlmostEqual(sample['mark_position'][1], mark_cord[1], delta=5, msg=f"Mark position Y isn't correct")


if __name__ == '__main__':
    unittest.main()
    