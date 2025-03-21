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

from unittest import TestCase
from pydantic import ValidationError


class TestMessagebusModels(TestCase):
    def test_get_tts_data(self):
        from neon_data_models.models.api.messagebus import GetTtsData

        # Test valid data
        valid_data = {"text": "Hello world", "lang": "en-us"}
        tts_data = GetTtsData(**valid_data)
        self.assertIsInstance(tts_data, GetTtsData)
        self.assertEqual(tts_data.text, "Hello world")
        self.assertEqual(tts_data.lang, "en-us")

        # Test with utterance instead of text (backward compatibility)
        compat_data = {"utterance": "Hello world"}
        tts_data = GetTtsData(**compat_data)
        self.assertEqual(tts_data.text, "Hello world")
        self.assertEqual(tts_data.lang, "en-us")  # Default value

        # Test missing required fields
        with self.assertRaises(ValidationError):
            GetTtsData()

    def test_tts_response_data(self):
        from neon_data_models.models.api.messagebus import TtsResponse, TtsReponseData
        from neon_data_models.types import Gender

        # Test valid response data
        valid_response = {
            "sentence": "Hello world",
            "translated": False,
            "phonemes": "HH AH L OW W ER L D",
            "genders": ["female", "male"],
            "audio": {"female": "base64audio1", "male": "base64audio2"}
        }
        tts_response = TtsResponse(**valid_response)
        self.assertIsInstance(tts_response, TtsResponse)
        self.assertEqual(tts_response.sentence, "Hello world")
        self.assertEqual(tts_response.translated, False)
        self.assertEqual(tts_response.phonemes, "HH AH L OW W ER L D")
        self.assertEqual(tts_response.genders, ["female", "male"])
        self.assertEqual(tts_response.audio["female"], "base64audio1")
        self.assertEqual(tts_response.audio["male"], "base64audio2")

        # Test valid response data without phonemes
        valid_response_no_phonemes = {
            "sentence": "Hello world",
            "translated": False,
            "genders": ["female", "male"],
            "audio": {"female": "base64audio1", "male": "base64audio2"}
        }
        tts_response_no_phonemes = TtsResponse(**valid_response_no_phonemes)
        self.assertIsInstance(tts_response_no_phonemes, TtsResponse)
        self.assertEqual(tts_response_no_phonemes.sentence, "Hello world")
        self.assertEqual(tts_response_no_phonemes.translated, False)
        self.assertIsNone(tts_response_no_phonemes.phonemes)
        self.assertEqual(tts_response_no_phonemes.genders, ["female", "male"])
        self.assertEqual(tts_response_no_phonemes.audio["female"], "base64audio1")
        self.assertEqual(tts_response_no_phonemes.audio["male"], "base64audio2")

        # Test valid responses data
        valid_responses_data = {
            "responses": {
                "en-us": tts_response
            }
        }
        tts_responses = TtsReponseData(**valid_responses_data)
        self.assertIsInstance(tts_responses, TtsReponseData)
        self.assertEqual(tts_responses.responses["en-us"].sentence, "Hello world")
        self.assertEqual(tts_responses.responses["en-us"].genders, ["female", "male"])

        # Test missing required fields
        with self.assertRaises(ValidationError):
            TtsResponse(sentence="Hello", phonemes="HH AH L OW", translated=False)  # Missing genders and audio
        
        with self.assertRaises(ValidationError):
            TtsResponse(sentence="Hello", phonemes="HH AH L OW", translated=False, genders=["female"])  # Missing audio
        
        with self.assertRaises(ValidationError):
            TtsReponseData()  # Missing responses

    def test_get_stt_data(self):
        from neon_data_models.models.api.messagebus import GetSttData

        # Test valid data
        valid_data = {"audio_data": "base64encodedstring", "lang": "en-us"}
        stt_data = GetSttData(**valid_data)
        self.assertIsInstance(stt_data, GetSttData)
        self.assertEqual(stt_data.audio_data, "base64encodedstring")
        self.assertEqual(stt_data.lang, "en-us")

        # Test with message_body instead of audio_data (backward compatibility)
        compat_data = {"message_body": "base64encodedstring"}
        stt_data = GetSttData(**compat_data)
        self.assertEqual(stt_data.audio_data, "base64encodedstring")
        self.assertEqual(stt_data.lang, "en-us")  # Default value

        # Test missing required fields
        with self.assertRaises(ValidationError):
            GetSttData()

    def test_stt_response_data(self):
        from neon_data_models.models.api.messagebus import SttReponseData

        # Test valid data
        valid_data = {
            "transcripts": ["Hello world", "Hello word"],
            "parser_data": {"confidence": 0.95}
        }
        stt_response_data = SttReponseData(**valid_data)
        self.assertIsInstance(stt_response_data, SttReponseData)
        self.assertEqual(stt_response_data.transcripts[0], "Hello world")
        self.assertEqual(stt_response_data.parser_data["confidence"], 0.95)

        # Test missing required fields
        with self.assertRaises(ValidationError):
            SttReponseData(transcripts=["Hello world"])  # Missing parser_data
        
        with self.assertRaises(ValidationError):
            SttReponseData(parser_data={"confidence": 0.95})  # Missing transcripts

    def test_get_response_data(self):
        from neon_data_models.models.api.messagebus import GetResponseData

        # Test valid data
        valid_data = {"utterances": ["How are you?"], "lang": "en-us"}
        response_data = GetResponseData(**valid_data)
        self.assertIsInstance(response_data, GetResponseData)
        self.assertEqual(response_data.utterances, ["How are you?"])
        self.assertEqual(response_data.lang, "en-us")

        # Test with messageText instead of utterances (backward compatibility)
        compat_data = {"messageText": "How are you?"}
        response_data = GetResponseData(**compat_data)
        self.assertEqual(response_data.utterances, ["How are you?"])
        self.assertEqual(response_data.lang, "en-us")  # Default value

        # Test with empty utterances
        empty_data = {"utterances": []}
        response_data = GetResponseData(**empty_data)
        self.assertEqual(response_data.utterances, [])

    def test_neon_get_tts(self):
        from neon_data_models.models.api.messagebus import NeonGetTts, GetTtsData
        from neon_data_models.models.base.messagebus import BaseMessage

        # Test valid message
        message_id = "test_mid"
        data = GetTtsData(text="Hello world")
        valid_message = NeonGetTts(data=data, context={})
        self.assertIsInstance(valid_message, NeonGetTts)
        self.assertIsInstance(valid_message, BaseMessage)
        self.assertEqual(valid_message.data.text, "Hello world")
        self.assertEqual(valid_message.msg_type, "neon.get_tts")

        # Test missing required fields
        with self.assertRaises(ValidationError):
            NeonGetTts(message_id=message_id, context={})  # Missing data

    def test_neon_get_stt(self):
        from neon_data_models.models.api.messagebus import NeonGetStt, GetSttData
        from neon_data_models.models.base.messagebus import BaseMessage

        # Test valid message
        message_id = "test_mid"
        data = GetSttData(audio_data="base64encodedstring")
        valid_message = NeonGetStt(data=data, context={})
        self.assertIsInstance(valid_message, NeonGetStt)
        self.assertIsInstance(valid_message, BaseMessage)
        self.assertEqual(valid_message.data.audio_data, "base64encodedstring")
        self.assertEqual(valid_message.msg_type, "neon.get_stt")

        # Test missing required fields
        with self.assertRaises(ValidationError):
            NeonGetStt(message_id=message_id, context={})  # Missing data

    def test_neon_get_response(self):
        from neon_data_models.models.api.messagebus import NeonTextInput, GetResponseData
        from neon_data_models.models.base.messagebus import BaseMessage

        # Test valid message
        message_id = "test_mid"
        data = GetResponseData(utterances=["How are you?"])
        valid_message = NeonTextInput(data=data, context={})
        self.assertIsInstance(valid_message, NeonTextInput)
        self.assertIsInstance(valid_message, BaseMessage)
        self.assertEqual(valid_message.data.utterances, ["How are you?"])
        self.assertEqual(valid_message.msg_type, "recognizer_loop:utterance")

        # Test missing required fields
        with self.assertRaises(ValidationError):
            NeonTextInput(message_id=message_id, context={})  # Missing data

    def test_neon_stt_response(self):
        from neon_data_models.models.api.messagebus import NeonSttResponse, SttReponseData
        from neon_data_models.models.base.messagebus import BaseMessage

        # Test valid message
        message_id = "test_mid"
        data = SttReponseData(transcripts=["Hello world"], parser_data={"confidence": 0.95})
        valid_message = NeonSttResponse(data=data, context={})
        self.assertIsInstance(valid_message, NeonSttResponse)
        self.assertIsInstance(valid_message, BaseMessage)
        self.assertEqual(valid_message.data.transcripts[0], "Hello world")
        self.assertEqual(valid_message.msg_type, "neon.get_stt.response")

        # Test missing required fields
        with self.assertRaises(ValidationError):
            NeonSttResponse(message_id=message_id, context={})  # Missing data

    def test_neon_tts_response(self):
        from neon_data_models.models.api.messagebus import NeonTtsResponse, TtsReponseData, TtsResponse
        from neon_data_models.models.base.messagebus import BaseMessage

        # Test valid message
        message_id = "test_mid"
        response = TtsResponse(
            sentence="Hello world", 
            translated=False, 
            phonemes="HH EH L OW",
            genders=["female", "male"],
            audio={"female": "base64audio1", "male": "base64audio2"}
        )
        data = TtsReponseData(responses={"en-us": response})
        valid_message = NeonTtsResponse(data=data, context={})
        self.assertIsInstance(valid_message, NeonTtsResponse)
        self.assertIsInstance(valid_message, BaseMessage)
        self.assertEqual(valid_message.data.responses["en-us"].sentence, "Hello world")
        self.assertEqual(valid_message.data.responses["en-us"].genders, ["female", "male"])
        self.assertEqual(valid_message.data.responses["en-us"].audio["female"], "base64audio1")
        self.assertEqual(valid_message.msg_type, "neon.get_tts.response")

        # Test alternate msg_type
        alt_message = NeonTtsResponse(data=data, message_id=message_id, context={}, 
                                    msg_type="klat.response")
        self.assertEqual(alt_message.msg_type, "klat.response")

        # Test missing required fields
        with self.assertRaises(ValidationError):
            NeonTtsResponse(message_id=message_id, context={})  # Missing data

    def test_neon_audio_input(self):
        from neon_data_models.models.api.messagebus import NeonAudioInput, GetSttData
        from neon_data_models.models.base.messagebus import BaseMessage

        # Test valid message
        message_id = "test_mid"
        data = GetSttData(audio_data="base64encodedstring")
        valid_message = NeonAudioInput(data=data, context={})
        self.assertIsInstance(valid_message, NeonAudioInput)
        self.assertIsInstance(valid_message, BaseMessage)
        self.assertEqual(valid_message.data.audio_data, "base64encodedstring")
        self.assertEqual(valid_message.data.lang, "en-us")  # Default value
        self.assertEqual(valid_message.msg_type, "neon.audio_input")

        # Test with message_body instead of audio_data (backward compatibility)
        compat_data = GetSttData(message_body="different_base64string")
        compat_message = NeonAudioInput(data=compat_data, context={})
        self.assertEqual(compat_message.data.audio_data, "different_base64string")

        # Test missing required fields
        with self.assertRaises(ValidationError):
            NeonAudioInput(message_id=message_id, context={})  # Missing data
