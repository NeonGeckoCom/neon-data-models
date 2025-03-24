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
        
        # Test default values for male and female fields
        self.assertIsNone(tts_response.male)
        self.assertIsNone(tts_response.female)

        # Test with explicit male and female fields
        valid_response_with_gender_paths = {
            "sentence": "Hello world",
            "translated": False,
            "genders": ["female", "male"],
            "audio": {"female": "base64audio1", "male": "base64audio2"},
            "male": "/path/to/male.wav",
            "female": "/path/to/female.wav"
        }
        tts_response_with_gender_paths = TtsResponse(**valid_response_with_gender_paths)
        self.assertEqual(tts_response_with_gender_paths.male, "/path/to/male.wav")
        self.assertEqual(tts_response_with_gender_paths.female, "/path/to/female.wav")
        
        # Test with different content in audio dict vs direct fields
        mixed_response = {
            "sentence": "Hello world",
            "translated": False,
            "genders": ["female", "male"],
            "audio": {"female": "base64audio1", "male": "base64audio2"},
            "male": "/path/to/different_male.wav",
            "female": "/path/to/different_female.wav"
        }
        mixed_tts_response = TtsResponse(**mixed_response)
        self.assertEqual(mixed_tts_response.audio["male"], "base64audio2")
        self.assertEqual(mixed_tts_response.male, "/path/to/different_male.wav")
        self.assertEqual(mixed_tts_response.audio["female"], "base64audio1")
        self.assertEqual(mixed_tts_response.female, "/path/to/different_female.wav")

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
        
        # Test ensure_audio_destination validator
        empty_dest_context = {"destination": []}
        message_empty_dest = NeonGetTts(data=data, context=empty_dest_context)
        self.assertIn("audio", message_empty_dest.context.destination)
        
        other_dest_context = {"destination": ["skills", "audio"]}
        message_other_dest = NeonGetTts(data=data, context=other_dest_context)
        self.assertIn("audio", message_other_dest.context.destination)
        self.assertIn("skills", message_other_dest.context.destination)
        
        audio_dest_context = {"destination": ["audio"]}
        message_audio_dest = NeonGetTts(data=data, context=audio_dest_context)
        self.assertEqual(message_audio_dest.context.destination, ["audio"])

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
        
        # Test ensure_audio_destination validator
        empty_dest_context = {"destination": []}
        message_empty_dest = NeonGetStt(data=data, context=empty_dest_context)
        self.assertIn("audio", message_empty_dest.context.destination)
        
        other_dest_context = {"destination": ["skills", "audio"]}
        message_other_dest = NeonGetStt(data=data, context=other_dest_context)
        self.assertIn("audio", message_other_dest.context.destination)
        self.assertIn("skills", message_other_dest.context.destination)
        
        audio_dest_context = {"destination": ["audio"]}
        message_audio_dest = NeonGetStt(data=data, context=audio_dest_context)
        self.assertEqual(message_audio_dest.context.destination, ["audio"])

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
        
        # Test ensure_skills_destination validator
        empty_dest_context = {"destination": []}
        message_empty_dest = NeonTextInput(data=data, context=empty_dest_context)
        self.assertIn("skills", message_empty_dest.context.destination)
        
        other_dest_context = {"destination": ["audio"]}
        message_other_dest = NeonTextInput(data=data, context=other_dest_context)
        self.assertIn("skills", message_other_dest.context.destination)
        self.assertIn("audio", message_other_dest.context.destination)
        
        skills_dest_context = {"destination": ["skills"]}
        message_skills_dest = NeonTextInput(data=data, context=skills_dest_context)
        self.assertEqual(message_skills_dest.context.destination, ["skills"])

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
        
        # Test ensure_audio_destination validator
        empty_dest_context = {"destination": []}
        message_empty_dest = NeonAudioInput(data=data, context=empty_dest_context)
        self.assertIn("audio", message_empty_dest.context.destination)
        
        other_dest_context = {"destination": ["skills", "audio"]}
        message_other_dest = NeonAudioInput(data=data, context=other_dest_context)
        self.assertIn("audio", message_other_dest.context.destination)
        self.assertIn("skills", message_other_dest.context.destination)
        
        audio_dest_context = {"destination": ["audio"]}
        message_audio_dest = NeonAudioInput(data=data, context=audio_dest_context)
        self.assertEqual(message_audio_dest.context.destination, ["audio"])

        # Test with message_body instead of audio_data (backward compatibility)
        compat_data = GetSttData(message_body="different_base64string")
        compat_message = NeonAudioInput(data=compat_data, context={})
        self.assertEqual(compat_message.data.audio_data, "different_base64string")

        # Test missing required fields
        with self.assertRaises(ValidationError):
            NeonAudioInput(message_id=message_id, context={})  # Missing data

    def test_neon_languages_data(self):
        from neon_data_models.models.api.messagebus import NeonLanguagesData

        # Test valid data
        valid_data = {
            "stt": ["en-us", "es-es", "fr-fr"],
            "tts": ["en-us", "es-es"],
            "skills": ["en-us"]
        }
        languages_data = NeonLanguagesData(**valid_data)
        self.assertIsInstance(languages_data, NeonLanguagesData)
        self.assertEqual(languages_data.stt, ["en-us", "es-es", "fr-fr"])
        self.assertEqual(languages_data.tts, ["en-us", "es-es"])
        self.assertEqual(languages_data.skills, ["en-us"])

        # Test missing required fields
        with self.assertRaises(ValidationError):
            NeonLanguagesData(stt=["en-us"], tts=["en-us"])  # Missing skills

        with self.assertRaises(ValidationError):
            NeonLanguagesData(stt=["en-us"], skills=["en-us"])  # Missing tts

        with self.assertRaises(ValidationError):
            NeonLanguagesData(tts=["en-us"], skills=["en-us"])  # Missing stt

    def test_neon_get_languages(self):
        from neon_data_models.models.api.messagebus import NeonGetLanguages
        from neon_data_models.models.base.messagebus import BaseMessage

        # Test valid message
        valid_message = NeonGetLanguages(data={}, context={})
        self.assertIsInstance(valid_message, NeonGetLanguages)
        self.assertIsInstance(valid_message, BaseMessage)
        self.assertEqual(valid_message.msg_type, "neon.languages.get")

        # Test with invalid msg_type
        with self.assertRaises(ValidationError):
            message_with_id = NeonGetLanguages(msg_type="test_mid",
                                               data={}, context={})

    def test_neon_languages_response(self):
        from neon_data_models.models.api.messagebus import NeonLanguagesResponse, NeonLanguagesData
        from neon_data_models.models.base.messagebus import BaseMessage

        # Test valid message
        languages_data = NeonLanguagesData(
            stt=["en-us", "es-es"],
            tts=["en-us", "fr-fr"],
            skills=["en-us"]
        )
        valid_message = NeonLanguagesResponse(data=languages_data, context={})
        self.assertIsInstance(valid_message, NeonLanguagesResponse)
        self.assertIsInstance(valid_message, BaseMessage)
        self.assertEqual(valid_message.msg_type, "neon.languages.get.response")
        self.assertEqual(valid_message.data.stt, ["en-us", "es-es"])
        self.assertEqual(valid_message.data.tts, ["en-us", "fr-fr"])
        self.assertEqual(valid_message.data.skills, ["en-us"])

        # Test missing required fields
        with self.assertRaises(ValidationError):
            NeonLanguagesResponse(context={})  # Missing data

    def test_tts_speaker(self):
        from neon_data_models.models.api.messagebus import TtsSpeaker
        
        # Test valid data
        valid_data = {"name": "Neon", "language": "en-us", "gender": "female", "voice": "cmu-slt"}
        speaker = TtsSpeaker(**valid_data)
        self.assertIsInstance(speaker, TtsSpeaker)
        self.assertEqual(speaker.name, "Neon")
        self.assertEqual(speaker.language, "en-us")
        self.assertEqual(speaker.gender, "female")
        self.assertEqual(speaker.voice, "cmu-slt")
        
        # Test default values
        minimal_data = {"name": "Test"}
        speaker = TtsSpeaker(**minimal_data)
        self.assertEqual(speaker.language, "en-us")
        self.assertEqual(speaker.gender, "female")
        self.assertIsNone(speaker.voice)
        
        # Test deprecated speaker field
        deprecated_data = {"speaker": "Deprecated"}
        speaker = TtsSpeaker(**deprecated_data)
        self.assertEqual(speaker.name, "Deprecated")
        self.assertEqual(speaker.speaker, "Deprecated")
        
        # Test mixed name and speaker fields (name should take precedence)
        mixed_data = {"name": "Primary", "speaker": "Secondary"}
        speaker = TtsSpeaker(**mixed_data)
        self.assertEqual(speaker.name, "Primary")
        self.assertEqual(speaker.speaker, "Secondary")
        
        # Test invalid gender
        with self.assertRaises(ValidationError):
            TtsSpeaker(name="Test", gender="invalid_gender")
    
    def test_get_tts_data_validation_edge_cases(self):
        from neon_data_models.models.api.messagebus import GetTtsData
        
        # Test empty text
        empty_text = {"text": ""}
        tts_data = GetTtsData(**empty_text)
        self.assertEqual(tts_data.text, "")
        
        # Test with both text and utterance (text should take precedence)
        dual_fields = {"text": "Primary text", "utterance": "Secondary text"}
        tts_data = GetTtsData(**dual_fields)
        self.assertEqual(tts_data.text, "Primary text")
        
        # Test with custom language
        custom_lang = {"text": "Hello", "lang": "fr-fr"}
        tts_data = GetTtsData(**custom_lang)
        self.assertEqual(tts_data.lang, "fr-fr")
        
        # Test with invalid language format (should accept but not validate format)
        invalid_lang = {"text": "Hello", "lang": "invalid_lang"}
        tts_data = GetTtsData(**invalid_lang)
        self.assertEqual(tts_data.lang, "invalid_lang")
    
    def test_get_stt_data_validation_edge_cases(self):
        from neon_data_models.models.api.messagebus import GetSttData
        
        # Test empty audio data
        empty_audio = {"audio_data": ""}
        stt_data = GetSttData(**empty_audio)
        self.assertEqual(stt_data.audio_data, "")
        
        # Test with both audio_data and message_body (audio_data should take precedence)
        dual_fields = {"audio_data": "Primary audio", "message_body": "Secondary audio"}
        stt_data = GetSttData(**dual_fields)
        self.assertEqual(stt_data.audio_data, "Primary audio")
        
        # Test with custom language
        custom_lang = {"audio_data": "data", "lang": "de-de"}
        stt_data = GetSttData(**custom_lang)
        self.assertEqual(stt_data.lang, "de-de")
    
    def test_tts_response_edge_cases(self):
        from neon_data_models.models.api.messagebus import TtsResponse
        
        # Test with minimum valid data
        min_valid_data = {
            "sentence": "Test",
            "translated": True,
            "genders": ["female"],
            "audio": {"female": "audio_data"}
        }
        response = TtsResponse(**min_valid_data)
        self.assertEqual(response.sentence, "Test")
        self.assertTrue(response.translated)
        self.assertEqual(response.genders, ["female"])
        self.assertEqual(response.audio["female"], "audio_data")
        
        # Test with invalid gender in genders field
        with self.assertRaises(ValidationError):
            TtsResponse(
                sentence="Test",
                translated=False,
                genders=["invalid_gender"],
                audio={"female": "audio_data"}
            )
        
        # Test with mismatch between genders and audio keys
        with self.assertRaises(ValidationError):
            TtsResponse(
                sentence="Test",
                translated=False,
                genders=["male"],
                audio={"female": "audio_data"}
            )
    
    def test_tts_response_multi_language(self):
        from neon_data_models.models.api.messagebus import TtsReponseData, TtsResponse, TtsSpeaker
        
        # Create multiple language responses
        en_response = TtsResponse(
            sentence="Hello world",
            translated=False,
            genders=["female", "male"],
            audio={"female": "en_audio_female", "male": "en_audio_male"}
        )
        
        es_response = TtsResponse(
            sentence="Hola mundo",
            translated=True,
            genders=["female"],
            audio={"female": "es_audio_female"}
        )
        
        fr_response = TtsResponse(
            sentence="Bonjour le monde",
            translated=True,
            genders=["male"],
            audio={"male": "fr_audio_male"}
        )
        
        # Test with multiple language responses
        multi_lang_data = {
            "responses": {
                "en-us": en_response,
                "es-es": es_response,
                "fr-fr": fr_response
            },
            "speaker": {
                "name": "MultiLang",
                "language": "en-us",
                "gender": "female"
            }
        }
        
        tts_response_data = TtsReponseData(**multi_lang_data)
        self.assertEqual(len(tts_response_data.responses), 3)
        self.assertEqual(tts_response_data.responses["en-us"].sentence, "Hello world")
        self.assertEqual(tts_response_data.responses["es-es"].sentence, "Hola mundo")
        self.assertEqual(tts_response_data.responses["fr-fr"].sentence, "Bonjour le monde")
        self.assertEqual(tts_response_data.speaker.name, "MultiLang")
        
        # Verify each language's specific properties
        self.assertFalse(tts_response_data.responses["en-us"].translated)
        self.assertTrue(tts_response_data.responses["es-es"].translated)
        self.assertEqual(tts_response_data.responses["en-us"].genders, ["female", "male"])
        self.assertEqual(tts_response_data.responses["es-es"].genders, ["female"])
        self.assertEqual(tts_response_data.responses["fr-fr"].genders, ["male"])
    
    def test_get_response_data_validation_edge_cases(self):
        from neon_data_models.models.api.messagebus import GetResponseData
        
        # Test with a single string in messageText
        text_string = {"messageText": "Single message"}
        response_data = GetResponseData(**text_string)
        self.assertEqual(response_data.utterances, ["Single message"])
        
        # Test with both utterances and messageText (utterances should take precedence)
        dual_fields = {
            "utterances": ["Primary utterance"],
            "messageText": "Secondary utterance"
        }
        response_data = GetResponseData(**dual_fields)
        self.assertEqual(response_data.utterances, ["Primary utterance"])
        
        # Test with multiple utterances
        multi_utterance = {
            "utterances": ["First utterance", "Second utterance", "Third utterance"]
        }
        response_data = GetResponseData(**multi_utterance)
        self.assertEqual(len(response_data.utterances), 3)
        self.assertEqual(response_data.utterances[1], "Second utterance")
        
        # Test with Unicode characters
        unicode_text = {"utterances": ["こんにちは", "你好", "مرحبا"]}
        response_data = GetResponseData(**unicode_text)
        self.assertEqual(response_data.utterances[0], "こんにちは")
    
    def test_serialization_deserialization(self):
        from neon_data_models.models.api.messagebus import (
            GetTtsData, NeonGetTts, TtsResponse, TtsReponseData, NeonTtsResponse
        )
        import json
        
        # Test serialization and deserialization of GetTtsData
        tts_data = GetTtsData(text="Serialize me", lang="en-us")
        serialized = json.loads(tts_data.model_dump_json())
        self.assertEqual(serialized["text"], "Serialize me")
        self.assertEqual(serialized["lang"], "en-us")
        
        deserialized = GetTtsData.model_validate(serialized)
        self.assertEqual(deserialized.text, "Serialize me")
        self.assertEqual(deserialized.lang, "en-us")
        
        # Test serialization and deserialization of complete message
        response = TtsResponse(
            sentence="Test response",
            translated=False,
            phonemes="T EH S T",
            genders=["female"],
            audio={"female": "test_audio_data"}
        )
        
        response_data = TtsReponseData(responses={"en-us": response})
        message = NeonTtsResponse(data=response_data, context={"source": "test"})
        
        serialized_message = json.loads(message.model_dump_json())
        self.assertEqual(serialized_message["msg_type"], "neon.get_tts.response")
        self.assertEqual(serialized_message["data"]["responses"]["en-us"]["sentence"], "Test response")
        
        deserialized_message = NeonTtsResponse.model_validate(serialized_message)
        self.assertEqual(deserialized_message.msg_type, "neon.get_tts.response")
        self.assertEqual(deserialized_message.data.responses["en-us"].sentence, "Test response")
        self.assertEqual(deserialized_message.data.responses["en-us"].audio["female"], "test_audio_data")
    
    def test_stt_response_data_edge_cases(self):
        from neon_data_models.models.api.messagebus import SttReponseData
        
        # Test with multiple transcripts
        multi_transcript = {
            "transcripts": ["First guess", "Second guess", "Third guess"],
            "parser_data": {"confidence": 0.8, "source": "test_engine"}
        }
        stt_response = SttReponseData(**multi_transcript)
        self.assertEqual(len(stt_response.transcripts), 3)
        self.assertEqual(stt_response.parser_data["confidence"], 0.8)
        
        # Test with complex parser data
        complex_parser_data = {
            "transcripts": ["Hello"],
            "parser_data": {
                "confidence": 0.95,
                "engine": "test_engine",
                "metadata": {
                    "duration": 2.5,
                    "sample_rate": 16000,
                    "format": "wav",
                    "channels": 1
                },
                "alternatives": [
                    {"text": "Hello", "confidence": 0.95},
                    {"text": "Hell no", "confidence": 0.05}
                ]
            }
        }
        stt_response = SttReponseData(**complex_parser_data)
        self.assertEqual(stt_response.parser_data["metadata"]["sample_rate"], 16000)
        self.assertEqual(stt_response.parser_data["alternatives"][0]["confidence"], 0.95)
        
        # Test with empty transcripts list (should fail)
        with self.assertRaises(ValidationError):
            SttReponseData(
                transcripts=[],
                parser_data={"confidence": 0.9}
            )
        
        # Test with empty parser data (should succeed as {}is valid)
        valid_empty_parser = {
            "transcripts": ["Hello"],
            "parser_data": {}
        }
        stt_response = SttReponseData(**valid_empty_parser)
        self.assertEqual(len(stt_response.parser_data), 0)
