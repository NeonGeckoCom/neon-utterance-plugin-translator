# # NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
# # All trademark and other rights reserved by their respective owners
# # Copyright 2008-2021 Neongecko.com Inc.
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

from ovos_plugin_manager.language import OVOSLangDetectionFactory, OVOSLangTranslationFactory
from ovos_utils.log import LOG

from neon_transformers import UtteranceTransformer
from neon_transformers.tasks import UtteranceTask


class UtteranceTranslator(UtteranceTransformer):
    task = UtteranceTask.TRANSLATION

    def __init__(self, name="utterance_translator", config=None, priority=5):
        super().__init__(name, priority, config)
        self.language_config = self.config.get("language") or {}
        self.supported_langs = self.language_config.get('supported_langs') or ['en']
        self.internal_lang = self.language_config.get("internal") or 'en-us' or self.supported_langs[0]
        self.lang_detector = OVOSLangDetectionFactory.create()
        self.translator = OVOSLangTranslationFactory.create()

    def transform(self, utterances, context=None):
        metadata = []
        was_translated = False
        for idx, ut in enumerate(utterances):
            try:
                original = ut
                detected_lang = self.lang_detector.detect(original)
                if context != None and context.get('lang') != '':
                    lang = context.get('lang')
                    if detected_lang != lang.split('-', 1)[0]:
                        LOG.warning(f"Specified lang: {lang} but detected {detected_lang}")
                    else:
                        LOG.debug(f"Detected language: {detected_lang}")
                else:
                    LOG.warning(f"No lang provided but detected {detected_lang}")
                    lang = detected_lang
                if lang.split('-', 1)[0] not in self.supported_langs:
                    LOG.warning(f"There is no: {lang} in supported languages. "
                                f"Utterance will be translated to {self.internal_lang}")
                    utterances[idx] = self.translator.translate(
                        original,
                        self.internal_lang,
                        lang)
                    was_translated = True
                    LOG.info(f"Translated utterance to: {utterances[idx]}")
                # add language metadata to context
                metadata += [{
                    "source_lang": lang,
                    "detected_lang": detected_lang,
                    "internal": self.internal_lang,
                    "was_translated": was_translated,
                    "raw_utterance": original,
                    "translated_utterance": utterances[idx]

                }]
            except Exception as e:
                LOG.error(e)
        # return translated utterances + data
        return utterances, {"translation_data": metadata}
