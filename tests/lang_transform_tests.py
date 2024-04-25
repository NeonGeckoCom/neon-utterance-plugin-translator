# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2021 Neongecko.com Inc.
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
from ovos_bus_client.message import Message
from libretranslate_neon_plugin import LibreTranslatePlugin

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from neon_utterance_translator_plugin import UtteranceTranslator


class LangTransformTests(unittest.TestCase):
    mock_config = {
        'language': {"internal_lang": "en-us",
                     "supported_langs": ['en', 'pl', 'uk', 'fi', 'nl'],
                     "detection_module": "libretranslate_detection_plug",
                     "translation_module": "libretranslate_plug"}
    }

    @classmethod
    def setUpClass(cls) -> None:
        import neon_utterance_translator_plugin
        neon_utterance_translator_plugin.Configuration = \
            Mock(return_value=cls.mock_config)
        cls.transformer = UtteranceTranslator(config={"enable_detector": True})

    def test_init(self):
        self.assertEqual(self.transformer.language_config,
                         self.mock_config['language'])
        self.assertIsNone(self.transformer.lang_detector)
        self.assertIsInstance(self.transformer.translator, LibreTranslatePlugin)

    def test_supported_lang_handling(self):
        # internal language (en)
        message = Message('test', {'utterance': ['message',
                                                 'to translate'],
                                   'context': {'lang': 'en-us'}})

        utterances = message.data.get('utterance')

        utterances, data = self.transformer.transform(utterances)
        result_list = []

        print(utterances)
        # message.context = merge_dict(message.context, data)

        for res in data['translation_data']:
            result = res["raw_utterance"]
            result_list.append(result)
            self.assertEqual(res["was_translated"], False)
        self.assertEqual(utterances, result_list)

        # supported language (pl)
        message = Message('test', {'utterance': ['wiadomość',
                                                 'przetłumaczyć'],
                                   'context': {'lang': 'pl-pl'}})

        utterances = message.data.get('utterance')
        context = message.data.get('context')

        utterances, data = self.transformer.transform(utterances,
                                                      context=context)
        result_list = []

        for res in data['translation_data']:
            result = res["raw_utterance"]
            result_list.append(result)
            self.assertEqual(res["was_translated"], False)
        self.assertEqual(utterances, result_list)

    def test_unsupported_lang_handling(self):
        # ru-ru should be translated to en-us
        message = Message('test', {'utterance': ['Это русский'],
                                   'context': {'lang': 'ru-ru'}})

        utterances = message.data.get('utterance')
        context = message.data.get('context')

        utterances, data = self.transformer.transform(utterances,
                                                      context=context)
        expected_translation = ["It's Russian"]
        result_list = []

        for res in data['translation_data']:
            result = res["translated_utterance"]
            result_list.append(result)
            self.assertEqual(res["was_translated"], True)
        self.assertEqual(expected_translation, result_list)


if __name__ == '__main__':
    unittest.main()
