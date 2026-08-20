import unittest

from command_engine import detect_intent


class CommandEngineTests(unittest.TestCase):
    def test_open_app(self):
        intent = detect_intent("please launch chrome")
        self.assertEqual(intent.name, "open_app")
        self.assertEqual(intent.argument, "chrome")

    def test_youtube_search_wins_over_generic_search(self):
        intent = detect_intent("search youtube for python tutorials")
        self.assertEqual(intent.name, "youtube_search")
        self.assertEqual(intent.argument, "python tutorials")

    def test_google_search(self):
        intent = detect_intent("google for react three fiber")
        self.assertEqual(intent.name, "web_search")
        self.assertEqual(intent.argument, "react three fiber")

    def test_folder(self):
        intent = detect_intent("show my downloads")
        self.assertEqual(intent.name, "open_folder")
        self.assertEqual(intent.argument, "downloads")

    def test_media_and_volume(self):
        self.assertEqual(detect_intent("next track").argument, "next")
        self.assertEqual(detect_intent("turn volume down").argument, "down")

    def test_power_requires_confirmation(self):
        intent = detect_intent("restart my computer")
        self.assertEqual(intent.name, "power")
        self.assertTrue(intent.requires_confirmation)

    def test_create_folder_requires_confirmation(self):
        intent = detect_intent("create a folder called AI Projects")
        self.assertEqual(intent.name, "create_folder")
        self.assertEqual(intent.argument, "ai projects")
        self.assertTrue(intent.requires_confirmation)

    def test_unknown_goes_to_ai(self):
        self.assertIsNone(detect_intent("explain quantum computing"))


if __name__ == "__main__":
    unittest.main()
