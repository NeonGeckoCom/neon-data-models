# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2024 Neongecko.com Inc.
# BSD-3
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
from datetime import datetime, timedelta
from unittest import TestCase
from pydantic import ValidationError

from neon_data_models.enum import AlertType
from neon_data_models.models.api.mq import UserDbRequest


class TestNodeV1(TestCase):
    def test_node_audio_input(self):
        from neon_data_models.models.api.node_v1 import NodeAudioInput
        valid_data = {"audio_data": "abc123", "lang": "en-us"}

        # Invalid msg_type
        with self.assertRaises(ValidationError):
            NodeAudioInput(msg_type="bad_message_type",
                           data=valid_data, context={})

        # Missing context
        with self.assertRaises(ValidationError):
            NodeAudioInput(data=valid_data)

        # Valid with or without `msg_type` explicitly passed
        self.assertEqual(NodeAudioInput(msg_type="neon.audio_input",
                                        data=valid_data, context={}),
                         NodeAudioInput(data=valid_data, context={}))

    def test_node_text_input(self):
        from neon_data_models.models.api.node_v1 import NodeTextInput
        valid_data = {"utterances": ["abc123"], "lang": "en-us"}

        # Invalid msg_type
        with self.assertRaises(ValidationError):
            NodeTextInput(msg_type="bad_message_type",
                           data=valid_data, context={})

        # Missing context
        with self.assertRaises(ValidationError):
            NodeTextInput(data=valid_data)

        # Valid with or without `msg_type` explicitly passed
        self.assertEqual(NodeTextInput(msg_type="recognizer_loop:utterance",
                                        data=valid_data, context={}),
                         NodeTextInput(data=valid_data, context={}))

    def test_node_get_stt(self):
        from neon_data_models.models.api.node_v1 import NodeGetStt
        valid_data = {"audio_data": "abc123", "lang": "en-us"}

        # Invalid msg_type
        with self.assertRaises(ValidationError):
            NodeGetStt(msg_type="bad_message_type",
                          data=valid_data, context={})

        # Missing context
        with self.assertRaises(ValidationError):
            NodeGetStt(data=valid_data)

        # Valid with or without `msg_type` explicitly passed
        self.assertEqual(NodeGetStt(msg_type="neon.get_stt",
                                       data=valid_data, context={}),
                         NodeGetStt(data=valid_data, context={}))

    def test_node_get_tts(self):
        from neon_data_models.models.api.node_v1 import NodeGetTts
        valid_data = {"text": "abc123", "lang": "en-us"}

        # Invalid msg_type
        with self.assertRaises(ValidationError):
            NodeGetTts(msg_type="bad_message_type",
                          data=valid_data, context={})

        # Missing context
        with self.assertRaises(ValidationError):
            NodeGetTts(data=valid_data)

        # Valid with or without `msg_type` explicitly passed
        self.assertEqual(NodeGetTts(msg_type="neon.get_tts",
                                       data=valid_data, context={}),
                         NodeGetTts(data=valid_data, context={}))

    def test_node_klat_response(self):
        from neon_data_models.models.api.node_v1 import NodeKlatResponse
        valid_data = {"en-us": {"sentence": "test",
                                "audio": {"male": None, "female": None}}}

        invalid_gender = {"en-us": {"sentence": "test",
                                    "audio": {"FAIL": None, "female": None}}}

        invalid_data = {"en-us": "audio_file"}

        # Invalid msg_type
        with self.assertRaises(ValidationError):
            NodeKlatResponse(msg_type="bad_message_type",
                             data=valid_data, context={})

        # Missing context
        with self.assertRaises(ValidationError):
            NodeKlatResponse(data=valid_data)

        # Invalid data
        with self.assertRaises(ValidationError):
            NodeKlatResponse(data=invalid_gender, context={})
        with self.assertRaises(ValidationError):
            NodeKlatResponse(data=invalid_data, context={})

        # Valid with or without `msg_type` explicitly passed
        self.assertEqual(NodeKlatResponse(msg_type="klat.response",
                                       data=valid_data, context={}),
                         NodeKlatResponse(data=valid_data, context={}))

    def test_node_audio_input_response(self):
        from neon_data_models.models.api.node_v1 import NodeAudioInputResponse
        valid_data = {"parser_data": {}, "transcripts": [""],
                      "skills_recv": True}

        # Invalid msg_type
        with self.assertRaises(ValidationError):
            NodeAudioInputResponse(msg_type="bad_message_type",
                          data=valid_data, context={})

        # Missing context
        with self.assertRaises(ValidationError):
            NodeAudioInputResponse(data=valid_data)

        # Valid with or without `msg_type` explicitly passed
        self.assertEqual(NodeAudioInputResponse(
            msg_type="neon.audio_input.response",
                                       data=valid_data, context={}),
                         NodeAudioInputResponse(data=valid_data, context={}))

    def test_node_get_stt_response(self):
        from neon_data_models.models.api.node_v1 import NodeGetSttResponse
        valid_data = {"parser_data": {}, "transcripts": [""],
                      "skills_recv": True}

        # Invalid msg_type
        with self.assertRaises(ValidationError):
            NodeGetSttResponse(msg_type="bad_message_type",
                          data=valid_data, context={})

        # Missing context
        with self.assertRaises(ValidationError):
            NodeGetSttResponse(data=valid_data)

        # Valid with or without `msg_type` explicitly passed
        self.assertEqual(NodeGetSttResponse(
            msg_type="neon.get_stt.response",
                                       data=valid_data, context={}),
                         NodeGetSttResponse(data=valid_data, context={}))

    def test_node_get_tts_response(self):
        from neon_data_models.models.api.node_v1 import NodeGetTtsResponse
        valid_data = {"en-us": {"sentence": "test",
                                "audio": {"male": None, "female": None}}}

        invalid_gender = {"en-us": {"sentence": "test",
                                    "audio": {"FAIL": None, "female": None}}}

        invalid_data = {"en-us": "audio_file"}

        # Invalid msg_type
        with self.assertRaises(ValidationError):
            NodeGetTtsResponse(msg_type="bad_message_type",
                             data=valid_data, context={})

        # Missing context
        with self.assertRaises(ValidationError):
            NodeGetTtsResponse(data=valid_data)

        # Invalid data
        with self.assertRaises(ValidationError):
            NodeGetTtsResponse(data=invalid_gender, context={})
        with self.assertRaises(ValidationError):
            NodeGetTtsResponse(data=invalid_data, context={})

        # Valid with or without `msg_type` explicitly passed
        self.assertEqual(NodeGetTtsResponse(msg_type="neon.get_tts.response",
                                       data=valid_data, context={}),
                         NodeGetTtsResponse(data=valid_data, context={}))

    def test_core_ww_detected(self):
        from neon_data_models.models.api.node_v1 import CoreWWDetected
        valid_data = {"wake_word": "hey_neon"}

        # Invalid msg_type
        with self.assertRaises(ValidationError):
            CoreWWDetected(msg_type="bad_message_type",
                          data=valid_data, context={})

        # Missing context
        with self.assertRaises(ValidationError):
            CoreWWDetected(data=valid_data)

        # Valid with or without `msg_type` explicitly passed
        self.assertEqual(CoreWWDetected(msg_type="neon.ww_detected",
                                       data=valid_data, context={}),
                         CoreWWDetected(data=valid_data, context={}))

    def test_core_intent_failure(self):
        from neon_data_models.models.api.node_v1 import CoreIntentFailure
        valid_data = {}

        # Invalid msg_type
        with self.assertRaises(ValidationError):
            CoreIntentFailure(msg_type="bad_message_type",
                          data=valid_data, context={})

        # Missing context
        with self.assertRaises(ValidationError):
            CoreIntentFailure(data=valid_data)

        # Valid with or without `msg_type` explicitly passed
        self.assertEqual(CoreIntentFailure(msg_type="complete_intent_failure",
                                       data=valid_data, context={}),
                         CoreIntentFailure(data=valid_data, context={}))

    def test_core_error_response(self):
        from neon_data_models.models.api.node_v1 import CoreErrorResponse
        valid_data = {"error": "test error", "data": {"testing": True}}

        # Invalid msg_type
        with self.assertRaises(ValidationError):
            CoreErrorResponse(msg_type="bad_message_type",
                          data=valid_data, context={})

        # Missing context
        with self.assertRaises(ValidationError):
            CoreErrorResponse(data=valid_data)

        # Valid with or without `msg_type` explicitly passed
        self.assertEqual(CoreErrorResponse(msg_type="klat.error",
                                       data=valid_data, context={}),
                         CoreErrorResponse(data=valid_data, context={}))

        # Valid with default data
        self.assertIsInstance(CoreErrorResponse(data={}, context={}),
                              CoreErrorResponse)

    def test_core_clear_data(self):
        from neon_data_models.models.api.node_v1 import CoreClearData
        from neon_data_models.enum import UserData
        valid_data = {"username": "test_user",
                      "data_to_remove": [UserData.ALL_DATA]}
        valid_data_int = {"username": "test_user",
                          "data_to_remove": [UserData.ALL_DATA.value]}

        # Invalid msg_type
        with self.assertRaises(ValidationError):
            CoreClearData(msg_type="bad_message_type",
                              data=valid_data, context={})

        # Missing context
        with self.assertRaises(ValidationError):
            CoreClearData(data=valid_data)

        # Valid with or without `msg_type` explicitly passed
        self.assertEqual(CoreClearData(msg_type="neon.clear_data",
                                           data=valid_data, context={}),
                         CoreClearData(data=valid_data, context={}))

        # Valid with int cast to enum
        self.assertEqual(CoreClearData(data=valid_data, context={}),
                         CoreClearData(data=valid_data_int, context={}))

    def test_core_alert_expired(self):
        from neon_data_models.models.api.node_v1 import CoreAlertExpired
        alert_expiration = datetime.utcnow() + timedelta(minutes=30)
        expiration_iso = alert_expiration.isoformat()

        frequency_delta = timedelta(days=1)
        frequency_seconds = frequency_delta.total_seconds()

        base_alert = {"alert_type": AlertType.ALARM,
                      "priority": 7,
                      "repeat_days": None,
                      "end_repeat": None,
                      "alert_name": "Test Alert",
                      "context": {}}
        datetime_alert = {**base_alert,
                          **{"next_expiration_time": alert_expiration,
                             "repeat_frequency": frequency_delta}}
        iso_alert = {**base_alert, **{"next_expiration_time": expiration_iso,
                                      "repeat_frequency": frequency_seconds}}

        # Invalid msg_type
        with self.assertRaises(ValidationError):
            CoreAlertExpired(msg_type="bad_message_type",
                              data=datetime_alert, context={})

        # Missing context
        with self.assertRaises(ValidationError):
            CoreAlertExpired(data=datetime_alert)

        # Valid with or without `msg_type` explicitly passed
        self.assertEqual(CoreAlertExpired(msg_type="neon.alert_expired",
                                           data=datetime_alert, context={}),
                         CoreAlertExpired(data=datetime_alert, context={}))

        # Validate cast from timestamp/epoch to datetime/timedelta
        self.assertEqual(CoreAlertExpired(data=datetime_alert, context={}),
                         CoreAlertExpired(data=iso_alert, context={}))
