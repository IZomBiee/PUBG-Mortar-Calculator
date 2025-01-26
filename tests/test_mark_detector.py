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
        self.mark_detector = MarkDetector('blue', 35)
        
    def test_get_cords(self):
        for sample in self.test_samples:
            image = cv2.imread(f'tests/test_samples/{sample['image_name']}')
            self.mark_detector.load_color(sample['color'])
            player_cord, mark_cord = self.mark_detector.get_cords(image)

            self.assertAlmostEqual(
                sample['player_cord'][0], player_cord[0] if player_cord[0] is not None else -1, delta=10,
                msg=(
                    f"Image: tests/test_samples/{sample['image_name']} "
                    f"Color: {sample['color']} Type: Player X"
                )
            )
            self.assertAlmostEqual(
                sample['player_cord'][1], player_cord[1] if player_cord[1] is not None else -1, delta=10,
                msg=(
                    f"Image: tests/test_samples/{sample['image_name']} "
                    f"Color: {sample['color']} Type: Player Y"
                )
            )

            self.assertAlmostEqual(
                sample['mark_cord'][0], mark_cord[0] if mark_cord[0] is not None else -1, delta=10,
                msg=(
                    f"Image: tests/test_samples/{sample['image_name']} "
                    f"Color: {sample['color']} Type: Mark X"
                )
            )
            self.assertAlmostEqual(
                sample['mark_cord'][1], mark_cord[1] if mark_cord[1] is not None else -1, delta=10,
                msg=(
                    f"Image: tests/test_samples/{sample['image_name']} "
                    f"Color: {sample['color']} Type: Mark Y"
                )
            )

if __name__ == '__main__':
    unittest.main()