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

import json
import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from neon_utterance_translator_plugin import UtteranceTranslator
from mycroft_bus_client import Message


class LangTransformTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.transformer = UtteranceTranslator()

    def test_existing_lang_handling_en(self):
        message = Message('test', {'utterance': ['message', 'to translate'],
                                   'context': {'lang': 'en-us', 'supported_langs': ['en', 'pl', 'uk', 'fi', 'nl']}})

        utterances = message.data.get('utterance')
        context = message.data.get('context')

        utterances, data = self.transformer.transform(utterances, context=context)
        result_list = []

        for res in data['translation_data']:
            result = res["raw_utterance"]
            result_list.append(result)
            self.assertEqual(res["was_translated"], False)
        self.assertEqual(utterances, result_list)

    def test_existing_lang_handling_pl(self):
        message = Message('test', {'utterance': ['wiadomość', 'przetłumaczyć'],
                                   'context': {'lang': 'pl-pl', 'supported_langs': ['en', 'pl', 'uk', 'fi', 'nl']}})

        utterances = message.data.get('utterance')
        context = message.data.get('context')

        utterances, data = self.transformer.transform(utterances, context=context)
        result_list = []

        for res in data['translation_data']:
            result = res["raw_utterance"]
            result_list.append(result)
            self.assertEqual(res["was_translated"], False)
        self.assertEqual(utterances, result_list)

    def test_non_existing_lang_handling_cz(self):
        message = Message('test', {'utterance': ['Это русский'],
                                   'context': {'lang': 'ru-ru', 'supported_langs': ['en', 'pl', 'uk', 'fi', 'nl']}})

        utterances = message.data.get('utterance')
        context = message.data.get('context')

        utterances, data = self.transformer.transform(utterances, context=context)
        expected_translation = ["It's Russian"]
        result_list = []

        for res in data['translation_data']:
            result = res["translated_utterance"]
            result_list.append(result)
            self.assertEqual(res["was_translated"], True)
        self.assertEqual(expected_translation, result_list)


if __name__ == '__main__':
    unittest.main()
