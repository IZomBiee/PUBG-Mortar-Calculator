import unittest
from src.pubg_mortar_calculator import SampleManager, detectors, SettingsLoader as SL

settings = SL()

class TestGridDetector(unittest.TestCase):
    def setUp(self):
        self.sample_manager = SampleManager()
        self.detector = detectors.GridDetector()

    def test_grid_gap(self):
        for sample in self.sample_manager:
            if not sample.verified: continue
            canny_image = self.detector.get_canny_frame(sample.get_minimap_image(),
                                                        settings.get("grid_detection_canny1_threshold_slider"),
                                                        settings.get("grid_detection_canny2_threshold_slider"))

            self.detector.detect_lines(canny_image, settings.get("grid_detection_line_threshold_slider")/100,
                                       settings.get("grid_detection_line_gap_slider")/100)

            gap = self.detector.calculate_grid_gap(settings.get("grid_detection_gap_threshold_slider"))
            self.assertAlmostEqual(sample.grid_gap, gap, msg=f'{sample.name}')

if __name__ == "__main__":
    unittest.main()