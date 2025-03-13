# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2025 Neongecko.com Inc.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import sys
import unittest

from unittest.mock import Mock

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from neon_utterance_translator_plugin import UtteranceTranslator


class LangDetectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        mock_config = {
            'language': {"internal_lang": "en-us",
                         "supported_langs": ['en', 'pl', 'uk', 'fi', 'nl'],
                         "detection_module": "libretranslate_detection_plug",
                         "translation_module": "libretranslate_plug"}
        }
        import neon_utterance_translator_plugin
        neon_utterance_translator_plugin.Configuration = \
            Mock(return_value=mock_config)
        cls.detector = UtteranceTranslator()

    def test_detector_valid_en(self):
        detected_lang = self.detector.lang_detector.detect("hello there")
        self.assertEqual(detected_lang, "en")

    def test_detector_probs(self):
        scores = self.detector.lang_detector.detect_probs('hello')
        self.assertIsInstance(scores, list)


if __name__ == '__main__':
    unittest.main()
