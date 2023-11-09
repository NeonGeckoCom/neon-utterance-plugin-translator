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

from typing import Optional, List
from ovos_config import Configuration
from ovos_plugin_manager.language import (OVOSLangDetectionFactory,
                                          OVOSLangTranslationFactory)
from ovos_utils.log import LOG
from neon_transformers import UtteranceTransformer
from neon_transformers.tasks import UtteranceTask


class UtteranceTranslator(UtteranceTransformer):
    task = UtteranceTask.TRANSLATION

    def __init__(self, name: str = "neon_utterance_translator_plugin",
                 config: Optional[dict] = None, priority: int = 5):
        """
        Create an Utterance Transformer to handle translating inputs.
        @param name: name of the transformer; used to determine default config
        @param config: optional dict config for this plugin
        @param priority: priority value for this plugin (1-100 with lower values
            taking priority over higher values)
        """
        super().__init__(name, priority, config)
        self.language_config = Configuration().get("language")
        self.supported_langs = self.language_config.get('supported_langs') or \
            ['en']
        self.internal_lang = self.language_config.get("internal") or \
            self.supported_langs[0]
        LOG.debug("Initializing translator")
        self.translator = OVOSLangTranslationFactory.create(
            self.language_config)
        if self.config.get("enable_detector", True):
            self.lang_detector = OVOSLangDetectionFactory.create(
                self.language_config)
        else:
            self.lang_detector = None
            LOG.info("Detection module disabled in configuration")

    def transform(self, utterances: List[str], context: Optional[dict] = None) \
            -> (List[str], dict):
        """
        Transform and get context for input utterances.
        @param utterances: List of string utterances to evaluate
        @param context: Optional dict context associated with utterances
        @returns: list of transformed utterances, dict calculated context
        """
        metadata = []
        was_translated = False
        for idx, ut in enumerate(utterances):
            try:
                original = ut
                if self.lang_detector:
                    detected_lang = self.lang_detector.detect(original)
                else:
                    detected_lang = context.get('lang',
                                                self.internal_lang).split('-',
                                                                          1)[0]
                if context and context.get('lang'):
                    lang = context.get('lang')
                    if detected_lang != lang.split('-', 1)[0]:
                        LOG.warning(f"Specified lang: {lang} but detected "
                                    f"{detected_lang}")
                    else:
                        LOG.debug(f"Detected language: {detected_lang}")
                else:
                    LOG.warning(f"No lang provided. Detected {detected_lang}")
                    lang = detected_lang
                if lang.split('-', 1)[0] not in self.supported_langs:
                    LOG.warning(f"There is no: {lang} in supported languages "
                                f"{self.supported_langs}. Utterance will be "
                                f"translated to {self.internal_lang}")
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
