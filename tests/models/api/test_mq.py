# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2025 Neongecko.com Inc.
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
from datetime import datetime, timezone


class TestUsersMQ(TestCase):
    def test_create_user_db_request(self):
        from neon_data_models.models.api.mq.users import UserDbRequest, CreateUserRequest

        # Test create user valid
        valid_kwargs = {"message_id": "test_id", "operation": "create",
                        "user": {"username": "test_user"}}
        create_request = CreateUserRequest(**valid_kwargs)
        self.assertIsInstance(create_request, CreateUserRequest)
        generic_request = UserDbRequest(**valid_kwargs)
        self.assertIsInstance(generic_request, CreateUserRequest)
        self.assertEqual(generic_request.user.username,
                         create_request.user.username)

        # Test invalid
        with self.assertRaises(ValidationError):
            UserDbRequest(operation="create", username="test",
                          message_id="test0")

    def test_read_user_db_request(self):
        from neon_data_models.models.api.mq.users import UserDbRequest, ReadUserRequest

        # Test read user valid
        valid_kwargs = {"message_id": "test_id", "operation": "read",
                        "user_spec": "test_user"}
        read_request = ReadUserRequest(**valid_kwargs)
        self.assertIsInstance(read_request, ReadUserRequest)
        generic_request = UserDbRequest(**valid_kwargs)
        self.assertIsInstance(generic_request, ReadUserRequest)
        self.assertEqual(generic_request.user_spec,
                         read_request.user_spec)

        # Test invalid
        with self.assertRaises(ValidationError):
            UserDbRequest(operation="read", user={"username": "test"},
                          message_id="test0")

    def test_update_user_db_request(self):
        from neon_data_models.models.api.mq.users import UserDbRequest, UpdateUserRequest

        # Test update user valid
        valid_kwargs = {"message_id": "test_id", "operation": "update",
                        "auth_password": "test_password",
                        "user": {"username": "test_user",
                                 "skills": {"skill_id": {"test": True}}}}
        update_request = UpdateUserRequest(**valid_kwargs)
        self.assertIsInstance(update_request, UpdateUserRequest)
        self.assertEqual(update_request.auth_username,
                         update_request.user.username)
        generic_request = UserDbRequest(**valid_kwargs)
        self.assertIsInstance(generic_request, UpdateUserRequest)
        self.assertEqual(generic_request.user.username,
                         update_request.user.username)

        # Test update read username/password from User object
        update = UpdateUserRequest(message_id="test_id", operation="update",
                                   user={"username": "user",
                                         "password_hash": "password"})
        self.assertEqual(update.auth_username, "user")
        self.assertEqual(update.auth_password, "password")

        # Test update with separate authentication user
        update = UpdateUserRequest(message_id="test_id", operation="update",
                                   user={"username": "user",
                                         "password_hash": "password"},
                                   auth_username="admin",
                                   auth_password="admin_pass")
        self.assertEqual(update.user.username, "user")
        self.assertEqual(update.user.password_hash, "password")

        self.assertEqual(update.auth_username, "admin")
        self.assertEqual(update.auth_password, "admin_pass")

        # Test invalid
        with self.assertRaises(ValidationError):
            UserDbRequest(operation="update", user={"username": "test_user",
                                                    "skills": {"skill_id": {
                                                        "test": True}}},
                          message_id="test0")

    def test_delete_user_db_request(self):
        from neon_data_models.models.api.mq.users import UserDbRequest, DeleteUserRequest

        # Test delete user valid
        valid_kwargs = {"message_id": "test_id", "operation": "delete",
                        "user": {"username": "test_user"}}
        delete_request = DeleteUserRequest(**valid_kwargs)
        self.assertIsInstance(delete_request, DeleteUserRequest)
        generic_request = UserDbRequest(**valid_kwargs)
        self.assertIsInstance(generic_request, DeleteUserRequest)
        self.assertEqual(generic_request.user.username,
                         delete_request.user.username)

        # Test invalid
        with self.assertRaises(ValidationError):
            UserDbRequest(operation="delete", username="test_user",
                          message_id="test0")


class TestLLMMQ(TestCase):
    def test_mq_llm_propose_request(self):
        from neon_data_models.models.api.mq.llm import LLMProposeRequest
        from neon_data_models.models.api.llm import LLMRequest
        from neon_data_models.models.base.contexts import MQContext

        query = "who are you"
        history = []
        model_name = "test_model"
        persona = {"name": "test_persona", "system_prompt": "Test prompt."}
        message_id = "test_mid"

        # Valid fully-defined
        valid_request = LLMProposeRequest(query=query, history=history,
                                          persona=persona, model=model_name,
                                          message_id=message_id)
        self.assertIsInstance(valid_request, LLMProposeRequest)
        self.assertIsInstance(valid_request, LLMRequest)
        self.assertIsInstance(valid_request, MQContext)

        # Valid backwards-compat (no model or persona)
        backwards_compat = LLMProposeRequest(query=query, history=history,
                                             message_id=message_id)
        self.assertIsInstance(backwards_compat, LLMProposeRequest)
        self.assertIsInstance(backwards_compat, LLMRequest)
        self.assertIsInstance(backwards_compat, MQContext)
        self.assertIsNone(backwards_compat.model)
        self.assertIsNone(backwards_compat.persona)

        # Invalid Persona defined
        with self.assertRaises(ValidationError):
            LLMProposeRequest(query=query, history=history,
                              message_id=message_id, persona={})

        # Invalid MQ Context
        with self.assertRaises(ValidationError):
            LLMProposeRequest(query=query, history=history)

        # Invalid LLM Request
        with self.assertRaises(ValidationError):
            LLMProposeRequest(history=history, message_id=message_id)

    def test_mq_llm_propose_response(self):
        from neon_data_models.models.api.mq.llm import LLMProposeResponse

        # Valid response
        self.assertIsInstance(LLMProposeResponse(response="test response",
                                                 message_id=""),
                              LLMProposeResponse)

        # Missing MQ required data
        with self.assertRaises(ValidationError):
            LLMProposeResponse(response="test response")

        # Missing response required data
        with self.assertRaises(ValidationError):
            LLMProposeResponse(message_id="")

    def test_mq_llm_discuss_request(self):
        from neon_data_models.models.api.mq.llm import LLMDiscussRequest
        query = "who are you"
        history = []
        message_id = "test_mid"
        opts = {"bot 1": "resp 1", "bot 2": "resp 2"}
        invalid_opts = {"bot 1": "resp 1", "bot 2": None}

        # Valid request
        valid_request = LLMDiscussRequest(query=query, history=history,
                                          message_id=message_id, options=opts)
        self.assertIsInstance(valid_request, LLMDiscussRequest)

        # Invalid options
        with self.assertRaises(ValidationError):
            LLMDiscussRequest(query=query, history=history,
                              message_id=message_id, options=invalid_opts)

        # Invalid MQ Context
        with self.assertRaises(ValidationError):
            LLMDiscussRequest(query=query, history=history, options=opts)

        # Invalid LLM Request
        with self.assertRaises(ValidationError):
            LLMDiscussRequest(query=query, message_id=message_id, options=opts)

    def test_mq_llm_discuss_response(self):
        from neon_data_models.models.api.mq.llm import LLMDiscussResponse

        # Valid response
        self.assertIsInstance(LLMDiscussResponse(opinion="test opinion",
                                                 message_id=""),
                              LLMDiscussResponse)

        # Missing MQ required data
        with self.assertRaises(ValidationError):
            LLMDiscussResponse(opinion="test opinion")

        # Missing response required data
        with self.assertRaises(ValidationError):
            LLMDiscussResponse(message_id="")

    def test_mq_llm_vote_request(self):
        from neon_data_models.models.api.mq.llm import LLMVoteRequest
        query = "who are you"
        history = []
        message_id = "test_mid"
        responses = ["resp 1", "resp 2"]
        invalid_responses = ["resp 1", "resp 2", None]

        # Valid request
        valid_request = LLMVoteRequest(query=query, history=history,
                                       message_id=message_id,
                                       responses=responses)
        self.assertIsInstance(valid_request, LLMVoteRequest)

        # Invalid options
        with self.assertRaises(ValidationError):
            LLMVoteRequest(query=query, history=history, message_id=message_id,
                           responses=invalid_responses)

        # Invalid MQ Context
        with self.assertRaises(ValidationError):
            LLMVoteRequest(query=query, history=history, responses=responses)

        # Invalid LLM Request
        with self.assertRaises(ValidationError):
            LLMVoteRequest(query=query, message_id=message_id,
                           responses=responses)

    def test_mq_llm_vote_response(self):
        from neon_data_models.models.api.mq.llm import LLMVoteResponse

        # Valid response
        self.assertIsInstance(LLMVoteResponse(sorted_answer_indexes=[2, 0, 1],
                                              message_id=""),
                              LLMVoteResponse)

        # Missing MQ required data
        with self.assertRaises(ValidationError):
            LLMVoteResponse(sorted_answer_indexes=[2, 0, 1])

        # Missing response required data
        with self.assertRaises(ValidationError):
            LLMVoteResponse(message_id="")

        # Invalid response data
        with self.assertRaises(ValidationError):
            LLMVoteResponse(sorted_answer_indexes=[2, 0, 1, "invalid"],
                            message_id="")


class TestNeonMQ(TestCase):
    def test_get_tts_data(self):
        from neon_data_models.models.api.mq.neon import GetTtsData

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

    def test_get_stt_data(self):
        from neon_data_models.models.api.mq.neon import GetSttData

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

    def test_get_response_data(self):
        from neon_data_models.models.api.mq.neon import GetResponseData

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

    def test_neon_mq_get_tts(self):
        from neon_data_models.models.api.mq.neon import NeonMqGetTts, GetTtsData
        from neon_data_models.models.base.contexts import MQContext

        # Test valid request
        message_id = "test_mid"
        data = GetTtsData(text="Hello world")
        valid_request = NeonMqGetTts(data=data, message_id=message_id, context={})
        self.assertIsInstance(valid_request, NeonMqGetTts)
        self.assertIsInstance(valid_request, MQContext)
        self.assertEqual(valid_request.data.text, "Hello world")
        self.assertEqual(valid_request.message_id, message_id)

        # Test missing MQ required data
        with self.assertRaises(ValidationError):
            NeonMqGetTts(data=data)

        # Test missing data required
        with self.assertRaises(ValidationError):
            NeonMqGetTts(message_id=message_id)

    def test_neon_mq_get_stt(self):
        from neon_data_models.models.api.mq.neon import NeonMqGetStt, GetSttData
        from neon_data_models.models.base.contexts import MQContext

        # Test valid request
        message_id = "test_mid"
        data = GetSttData(audio_data="base64encodedstring")
        valid_request = NeonMqGetStt(data=data, message_id=message_id,
                                     context={})
        self.assertIsInstance(valid_request, NeonMqGetStt)
        self.assertIsInstance(valid_request, MQContext)
        self.assertEqual(valid_request.data.audio_data, "base64encodedstring")
        self.assertEqual(valid_request.message_id, message_id)

        # Test missing MQ required data
        with self.assertRaises(ValidationError):
            NeonMqGetStt(data=data)

        # Test missing data required
        with self.assertRaises(ValidationError):
            NeonMqGetStt(message_id=message_id)

    def test_neon_mq_get_response(self):
        from neon_data_models.models.api.mq.neon import NeonMqTextInput, GetResponseData
        from neon_data_models.models.base.contexts import MQContext

        # Test valid request
        message_id = "test_mid"
        data = GetResponseData(utterances=["How are you?"])
        valid_request = NeonMqTextInput(data=data, message_id=message_id,
                                          context={})
        self.assertIsInstance(valid_request, NeonMqTextInput)
        self.assertIsInstance(valid_request, MQContext)
        self.assertEqual(valid_request.data.utterances, ["How are you?"])
        self.assertEqual(valid_request.message_id, message_id)

        # Test missing MQ required data
        with self.assertRaises(ValidationError):
            NeonMqTextInput(data=data)

        # Test missing data required
        with self.assertRaises(ValidationError):
            NeonMqTextInput(message_id=message_id)

    def test_neon_mq_stt_response(self):
        from neon_data_models.models.api.mq.neon import NeonMqSttResponse
        # TODO: This needs defined serialized messages
        # # Test valid response
        # valid_response = NeonMqSttResponse(
        #     transcription="Hello world",
        #     message_id="test_mid"
        # )
        # self.assertIsInstance(valid_response, NeonMqSttResponse)
        # self.assertEqual(valid_response.transcription, "Hello world")
        # self.assertEqual(valid_response.message_id, "test_mid")

        # # Test missing MQ required data
        # with self.assertRaises(ValidationError):
        #     NeonMqSttResponse(transcription="Hello world")

        # # Test missing transcription data
        # with self.assertRaises(ValidationError):
        #     NeonMqSttResponse(message_id="test_mid")

    def test_neon_mq_tts_response(self):
        from neon_data_models.models.api.mq.neon import NeonMqTtsResponse
        # TODO: This needs defined serialized messages
        # # Test valid response
        # valid_response = NeonMqTtsResponse(
        #     audio_data="base64encodedstring",
        #     message_id="test_mid"
        # )
        # self.assertIsInstance(valid_response, NeonMqTtsResponse)
        # self.assertEqual(valid_response.audio_data, "base64encodedstring")
        # self.assertEqual(valid_response.message_id, "test_mid")

        # # Test missing MQ required data
        # with self.assertRaises(ValidationError):
        #     NeonMqTtsResponse(audio_data="base64encodedstring")

        # # Test missing audio data
        # with self.assertRaises(ValidationError):
        #     NeonMqTtsResponse(message_id="test_mid")

    def test_neon_api_message(self):
        from neon_data_models.models.api.mq.neon import NeonApiMessage, GetTtsData, GetSttData, GetResponseData
        from neon_data_models.models.api.mq.neon import NeonMqGetTts, NeonMqGetStt, NeonMqTextInput
        from neon_data_models.models.api.mq.neon import NeonMqSttResponse, NeonMqTtsResponse

        # Test TTS message
        tts_message = NeonApiMessage(
            msg_type="neon.get_tts",
            data=GetTtsData(text="Hello world"),
            context={},
            message_id="test_mid"
        )
        self.assertIsInstance(tts_message, NeonMqGetTts)

        # Test STT message
        stt_message = NeonApiMessage(
            msg_type="neon.get_stt",
            data=GetSttData(audio_data="base64encodedstring"),
            context={},
            message_id="test_mid"
        )
        self.assertIsInstance(stt_message, NeonMqGetStt)

        # Test get response message
        response_message = NeonApiMessage(
            msg_type="recognizer_loop:utterance",
            data=GetResponseData(utterances=["How are you?"]),
            context={},
            message_id="test_mid"
        )
        self.assertIsInstance(response_message, NeonMqTextInput)

        # Test STT response
        stt_response = NeonApiMessage(
            msg_type="neon.get_stt.response",
            data={"transcripts": ["test"],
                  "parser_data": {}},
            context={},
            message_id="test_mid"
        )
        self.assertIsInstance(stt_response, NeonMqSttResponse)

        # Test TTS response
        tts_response = NeonApiMessage(
            msg_type="neon.get_tts.response",
            data={"responses": {"en-us": {"sentence": "test",
                                          "translated": False,
                                          "phonemes": "",
                                          "genders": ["female"],
                                          "audio": {
                                          "female": "fake_b64_audio"}}}},
            context={},
            message_id="test_mid"
        )
        self.assertIsInstance(tts_response, NeonMqTtsResponse)

        # Test from_sio_message for STT
        sio_stt = {
            "requested_skill": "stt",
            "message_body": "base64encodedstring",
            "client": "test_client",
            "nick": "test_user",
            "cid": "test_session",
            "sid": "test_shout_id",
            "timeCreated": 123456789,
            "message_id": "test_mid"
        }
        stt_req = NeonApiMessage.from_sio_message(sio_stt)
        self.assertIsInstance(stt_req, NeonMqGetStt)
        self.assertEqual(stt_req.data.audio_data, "base64encodedstring")

        # Test from_sio_message for TTS
        sio_tts = {
            "requested_skill": "tts",
            "utterance": "Hello world",
            "client": "test_client",
            "nick": "test_user",
            "cid": "test_session",
            "sid": "test_shout_id",
            "timeCreated": 123456789,
            "message_id": "test_mid"
        }
        tts_req = NeonApiMessage.from_sio_message(sio_tts)
        self.assertIsInstance(tts_req, NeonMqGetTts)
        self.assertEqual(tts_req.data.text, "Hello world")

        # Test from_sio_message for recognizer
        sio_recognizer = {
            "requested_skill": "recognizer",
            "messageText": "How are you?",
            "client": "test_client",
            "nick": "test_user",
            "cid": "test_session",
            "sid": "test_shout_id",
            "timeCreated": 123456789,
            "message_id": "test_mid"
        }
        recognizer_req = NeonApiMessage.from_sio_message(sio_recognizer)
        self.assertIsInstance(recognizer_req, NeonMqTextInput)
        self.assertEqual(recognizer_req.data.utterances, ["How are you?"])

        # Test invalid requested_skill
        with self.assertRaises(ValueError):
            NeonApiMessage.from_sio_message({"requested_skill": "invalid"})

    def test_neon_mq_text_input(self):
        from neon_data_models.models.api.mq.neon import NeonMqTextInput, GetResponseData
        from neon_data_models.models.base.contexts import MQContext

        # Test valid request
        message_id = "test_mid"
        data = GetResponseData(utterances=["How are you?"])
        valid_request = NeonMqTextInput(data=data, message_id=message_id,
                                       context={})
        self.assertIsInstance(valid_request, NeonMqTextInput)
        self.assertIsInstance(valid_request, MQContext)
        self.assertEqual(valid_request.data.utterances, ["How are you?"])
        self.assertEqual(valid_request.message_id, message_id)

        # Test missing MQ required data
        with self.assertRaises(ValidationError):
            NeonMqTextInput(data=data)

        # Test missing data required
        with self.assertRaises(ValidationError):
            NeonMqTextInput(message_id=message_id)

    def test_neon_api_message_validation(self):
        from neon_data_models.models.api.mq.neon import NeonApiMessage, GetTtsData

        # Test parse_from_messagebus validator with MQ context in a nested field
        message_with_mq = {
            "msg_type": "neon.get_tts",
            "data": {"text": "Hello world"},
            "context": {"mq": {
                "message_id": "mq_mid"
            }}
        }
        
        api_message = NeonApiMessage(**message_with_mq)
        self.assertEqual(api_message.message_id, "mq_mid")
        
        # Test with direct MQ context fields
        direct_message = {
            "msg_type": "neon.get_tts",
            "data": {"text": "Hello world"},
            "context": {},
            "message_id": "direct_mid"
        }
        
        direct_api_message = NeonApiMessage(**direct_message)
        self.assertEqual(direct_api_message.message_id, "direct_mid")

    def test_neon_mq_audio_input(self):
        from neon_data_models.models.api.mq.neon import NeonMqAudioInput, GetSttData
        from neon_data_models.models.api.messagebus import NeonAudioInput
        from neon_data_models.models.base.contexts import MQContext

        # Test valid request
        message_id = "test_mid"
        data = GetSttData(audio_data="base64encodedstring")
        valid_request = NeonMqAudioInput(data=data, message_id=message_id, context={})
        self.assertIsInstance(valid_request, NeonMqAudioInput)
        self.assertIsInstance(valid_request, NeonAudioInput)
        self.assertIsInstance(valid_request, MQContext)
        self.assertEqual(valid_request.data.audio_data, "base64encodedstring")
        self.assertEqual(valid_request.message_id, message_id)
        self.assertEqual(valid_request.msg_type, "neon.audio_input")

        # Test missing MQ required data
        with self.assertRaises(ValidationError):
            NeonMqAudioInput(data=data)

        # Test missing data required
        with self.assertRaises(ValidationError):
            NeonMqAudioInput(message_id=message_id)

    def test_neon_mq_get_languages(self):
        from neon_data_models.models.api.mq.neon import NeonMqGetLanguages
        from neon_data_models.models.api.messagebus import NeonGetLanguages
        from neon_data_models.models.base.contexts import MQContext

        # Test valid request
        message_id = "test_mid"
        valid_request = NeonMqGetLanguages(message_id=message_id, data={},
                                            context={})
        self.assertIsInstance(valid_request, NeonMqGetLanguages)
        self.assertIsInstance(valid_request, NeonGetLanguages)
        self.assertIsInstance(valid_request, MQContext)
        self.assertEqual(valid_request.message_id, message_id)
        self.assertEqual(valid_request.msg_type, "neon.languages.get")

        # Test missing MQ required data
        with self.assertRaises(ValidationError):
            NeonMqGetLanguages()

    def test_neon_mq_languages_response(self):
        from neon_data_models.models.api.mq.neon import NeonMqLanguagesResponse
        from neon_data_models.models.api.messagebus import NeonLanguagesResponse, NeonLanguagesData
        from neon_data_models.models.base.contexts import MQContext

        # Test valid response
        message_id = "test_mid"
        data = NeonLanguagesData(
            stt=["en-us", "es-es"],
            tts=["en-us", "fr-fr"],
            skills=["en-us"]
        )
        valid_response = NeonMqLanguagesResponse(data=data, message_id=message_id, context={})
        self.assertIsInstance(valid_response, NeonMqLanguagesResponse)
        self.assertIsInstance(valid_response, NeonLanguagesResponse)
        self.assertIsInstance(valid_response, MQContext)
        self.assertEqual(valid_response.message_id, message_id)
        self.assertEqual(valid_response.msg_type, "neon.languages.get.response")
        self.assertEqual(valid_response.data.stt, ["en-us", "es-es"])
        self.assertEqual(valid_response.data.tts, ["en-us", "fr-fr"])
        self.assertEqual(valid_response.data.skills, ["en-us"])

        # Test missing MQ required data
        with self.assertRaises(ValidationError):
            NeonMqLanguagesResponse(data=data)

        # Test missing data required
        with self.assertRaises(ValidationError):
            NeonMqLanguagesResponse(message_id=message_id)

    def test_neon_api_message_languages(self):
        from neon_data_models.models.api.mq.neon import NeonApiMessage
        from neon_data_models.models.api.mq.neon import NeonMqGetLanguages, NeonMqLanguagesResponse
        from neon_data_models.models.api.messagebus import NeonLanguagesData

        # Test GetLanguages message
        languages_get_message = NeonApiMessage(
            msg_type="neon.languages.get",
            data={},
            context={},
            message_id="test_mid"
        )
        self.assertIsInstance(languages_get_message, NeonMqGetLanguages)
        self.assertEqual(languages_get_message.message_id, "test_mid")
        self.assertEqual(languages_get_message.msg_type, "neon.languages.get")

        # Test LanguagesResponse message
        languages_data = NeonLanguagesData(
            stt=["en-us", "es-es"],
            tts=["en-us", "fr-fr"],
            skills=["en-us"]
        )
        languages_response = NeonApiMessage(
            msg_type="neon.languages.get.response",
            data=languages_data,
            context={},
            message_id="test_mid"
        )
        self.assertIsInstance(languages_response, NeonMqLanguagesResponse)
        self.assertEqual(languages_response.data.stt, ["en-us", "es-es"])
        self.assertEqual(languages_response.data.tts, ["en-us", "fr-fr"])
        self.assertEqual(languages_response.data.skills, ["en-us"])

    def test_neon_mq_unknown_message(self):
        from neon_data_models.models.api.mq.neon import NeonMqUnknownMessage
        from neon_data_models.models.base.messagebus import BaseMessage
        from neon_data_models.models.base.contexts import MQContext

        # Test valid initialization
        unknown_message = NeonMqUnknownMessage(
            msg_type="unknown.type",
            message_id="test_mid",
            data={},
            context={}
        )
        
        # Test inheritance
        self.assertIsInstance(unknown_message, NeonMqUnknownMessage)
        self.assertIsInstance(unknown_message, BaseMessage)
        self.assertIsInstance(unknown_message, MQContext)
        
        # Test properties
        self.assertEqual(unknown_message.msg_type, "unknown.type")
        self.assertEqual(unknown_message.message_id, "test_mid")
        
        # Test with missing required fields
        with self.assertRaises(ValidationError):
            NeonMqUnknownMessage()

    def test_neon_api_message_fallback(self):
        from neon_data_models.models.api.mq.neon import NeonApiMessage, NeonMqUnknownMessage
        
        # Test with unknown message type
        unknown_message_data = {
            "msg_type": "unknown.message.type",
            "message_id": "test_mid",
            "data": {"some_field": "some_value"},
            "context": {}
        }
        
        message = NeonApiMessage(**unknown_message_data)
        
        # Verify fallback to NeonMqUnknownMessage
        self.assertIsInstance(message, NeonMqUnknownMessage)
        self.assertEqual(message.msg_type, "unknown.message.type")
        self.assertEqual(message.message_id, "test_mid")
        
        # Test with the specific problematic message type from the error
        ovos_stt_message = {
            "msg_type": "ovos.languages.stt.response",
            "message_id": "test_mid",
            "data": {"languages": ["en-us", "es-es"]},
            "context": {}
        }
        
        message = NeonApiMessage(**ovos_stt_message)
        
        # Verify it doesn't raise an exception and preserves the data
        self.assertIsInstance(message, NeonMqUnknownMessage)
        self.assertEqual(message.msg_type, "ovos.languages.stt.response")
        self.assertEqual(message.message_id, "test_mid")
        self.assertEqual(message.data, {"languages": ["en-us", "es-es"]})

    def test_neon_api_message_with_nested_data(self):
        from neon_data_models.models.api.mq.neon import NeonApiMessage, NeonMqUnknownMessage
        
        # Test with deeply nested data
        complex_message = {
            "msg_type": "complex.unknown.type",
            "message_id": "test_mid",
            "data": {
                "nested": {
                    "deeply": {
                        "value": "test"
                    }
                },
                "list_data": [1, 2, 3, {"key": "value"}]
            },
            "context": {
                "client": "test_client",
                "user": "test_user"
            }
        }
        
        message = NeonApiMessage(**complex_message)
        
        # Verify complex data is preserved
        self.assertIsInstance(message, NeonMqUnknownMessage)
        self.assertEqual(message.msg_type, "complex.unknown.type")
        self.assertEqual(message.message_id, "test_mid")
        self.assertEqual(message.data["nested"]["deeply"]["value"], "test")
        self.assertEqual(message.data["list_data"][3]["key"], "value")
        self.assertEqual(message.context.client, "test_client")


class TestChatbotsMQ(TestCase):
    def test_chatbots_mq_request(self):
        from neon_data_models.models.api.mq.chatbots import ChatbotsMqRequest
        
        # Test basic initialization with required fields
        current_time = datetime.now(tz=timezone.utc)
        valid_kwargs = {
            "username": "test_user",
            "cid": "test_conversation",
            "message_text": "Hello, how are you?",
            "message_id": "test_message_id",
            "time_created": current_time
        }
        
        chatbot_request = ChatbotsMqRequest(**valid_kwargs)
        self.assertIsInstance(chatbot_request, ChatbotsMqRequest)
        self.assertEqual(chatbot_request.username, "test_user")
        self.assertEqual(chatbot_request.cid, "test_conversation")
        self.assertEqual(chatbot_request.message_text, "Hello, how are you?")
        self.assertEqual(chatbot_request.time_created, current_time)
        self.assertFalse(chatbot_request.from_bot)  # Default value check
        
        # Test with all fields
        full_kwargs = {
            "username": "test_user",
            "cid": "test_conversation",
            "message_text": "Hello, how are you?",
            "from_bot": True,
            "prompt_id": "test_prompt_id",
            "prompt_state": 1,
            "time_created": current_time,
            "requested_participants": ["participant1", "participant2"],
            "recipient": "test_recipient",
            "bound_service": "test_service",
            "client": "test_client",
            "message_id": "test_message_id",
            "messageID": "test_sid"
        }
        
        full_request = ChatbotsMqRequest(**full_kwargs)
        self.assertIsInstance(full_request, ChatbotsMqRequest)
        self.assertEqual(full_request.username, "test_user")
        self.assertEqual(full_request.cid, "test_conversation")
        self.assertEqual(full_request.sid, "test_sid")
        self.assertEqual(full_request.message_text, "Hello, how are you?")
        self.assertTrue(full_request.from_bot)
        self.assertEqual(full_request.prompt_id, "test_prompt_id")
        self.assertEqual(full_request.prompt_state, 1)
        self.assertEqual(full_request.time_created, current_time)
        self.assertEqual(full_request.requested_participants, ["participant1", "participant2"])
        self.assertEqual(full_request.recipient, "test_recipient")
        self.assertEqual(full_request.bound_service, "test_service")
        self.assertEqual(full_request.message_id, "test_message_id")
        
        # Test missing required fields
        with self.assertRaises(ValidationError):
            # Missing message text
            ChatbotsMqRequest(username="test_user", cid="test_conversation")
        
        with self.assertRaises(ValidationError):
            # Missing username
            ChatbotsMqRequest(cid="test_conversation", message_text="Hello", 
                              time_created=current_time)
        
        with self.assertRaises(ValidationError):
            # Missing cid
            ChatbotsMqRequest(username="test_user", message_text="Hello", time_created=current_time)
        
        # Test model_dump method for backwards compatibility
        # Test with from_bot=True
        bot_request = ChatbotsMqRequest(
            username="test_user",
            cid="test_conversation",
            message_id="test_message_id",
            message_text="Hello from bot",
            from_bot=True,
            time_created=datetime.now(tz=timezone.utc)
        )
        serialized_bot = bot_request.model_dump()
        self.assertEqual(serialized_bot["bot"], "1")
        self.assertTrue(serialized_bot["from_bot"])
        self.assertEqual(serialized_bot["messageText"], bot_request.message_text)
        self.assertEqual(serialized_bot["nick"], bot_request.username)
        
        # Test with from_bot=False (default)
        user_request = ChatbotsMqRequest(
            username="test_user",
            cid="test_conversation",
            message_id="test_message_id",
            message_text="Hello from user",
            time_created=datetime.now(tz=timezone.utc)
        )
        serialized_user = user_request.model_dump()
        self.assertEqual(serialized_user["bot"], "0")
        self.assertFalse(serialized_user["from_bot"])
        
        # Test from_sio_message method
        sio_message = {
            "userDisplayName": "display_name",
            "userID": "user_id",
            "cid": "test_conversation",
            "messageText": "Hello from SIO",
            "bot": 1,
            "promptID": "test_prompt_id",
            "promptState": 2,
            "timeCreated": current_time,
            "recipient": "chatbots",
            "bound_service": "test_service",
            "message_id": "test_message_id"
        }
        
        sio_request = ChatbotsMqRequest.from_sio_message(sio_message)
        self.assertIsInstance(sio_request, ChatbotsMqRequest)
        self.assertEqual(sio_request.username, "display_name")
        self.assertEqual(sio_request.cid, "test_conversation")
        self.assertEqual(sio_request.message_text, "Hello from SIO")
        self.assertTrue(sio_request.from_bot)
        self.assertEqual(sio_request.prompt_id, "test_prompt_id")
        self.assertEqual(sio_request.prompt_state, 2)
        self.assertEqual(sio_request.time_created, current_time)
        self.assertEqual(sio_request.recipient, "chatbots")
        self.assertEqual(sio_request.bound_service, "test_service")
        
        # Test userID fallback
        sio_message = {
            "userID": "user_id",
            "cid": "test_conversation",
            "messageText": "Hello from SIO",
            "timeCreated": current_time,
            "message_id": "test_message_id"
        }
        
        sio_request = ChatbotsMqRequest.from_sio_message(sio_message)
        self.assertEqual(sio_request.username, "user_id")

    def test_chatbots_mq_response(self):
        from neon_data_models.models.api.mq.chatbots import ChatbotsMqResponse
        from datetime import datetime, timezone
        
        # Test basic initialization with required fields
        current_time = datetime.now(tz=timezone.utc)
        valid_kwargs = {
            "userID": "user123",
            "messageText": "Hello, this is a response",
            "message_id": "test_message_id"
        }
        
        response = ChatbotsMqResponse(**valid_kwargs)
        self.assertIsInstance(response, ChatbotsMqResponse)
        self.assertEqual(response.user_id, "user123")
        self.assertEqual(response.message_text, "Hello, this is a response")
        self.assertEqual(response.bot, "0")  # Default value check
        self.assertEqual(response.is_announcement, "0")  # Default value check
        
        # Test with all fields including aliases
        full_kwargs = {
            "userID": "user123",
            "userDisplayName": "John Doe",
            "messageText": "Hello, this is a complete response",
            "messageID": "msg123",
            "repliedMessage": "original_msg456",
            "bot": "1",
            "promptID": "prompt789",
            "promptState": 2,
            "isAnnouncement": "1",
            "timeCreated": current_time,
            "source": "test_source",
            "client": "test_client",
            "cid": "conversation123",
            "message_id": "message123"
        }
        
        full_response = ChatbotsMqResponse(**full_kwargs)
        self.assertIsInstance(full_response, ChatbotsMqResponse)
        self.assertEqual(full_response.user_id, "user123")
        self.assertEqual(full_response.username, "John Doe")
        self.assertEqual(full_response.message_text, "Hello, this is a complete response")
        self.assertEqual(full_response.sid, "msg123")
        self.assertEqual(full_response.replied_message, "original_msg456")
        self.assertEqual(full_response.bot, "1")
        self.assertEqual(full_response.prompt_id, "prompt789")
        self.assertEqual(full_response.prompt_state, 2)
        self.assertEqual(full_response.is_announcement, "1")
        self.assertEqual(full_response.time_created, current_time)
        self.assertEqual(full_response.source, "test_source")
        self.assertEqual(full_response.cid, "conversation123")
        self.assertEqual(full_response.message_id, "message123")
        
        # Test model_dump with aliased fields
        serialized = full_response.model_dump()
        self.assertIn("userID", serialized)
        self.assertIn("userDisplayName", serialized)
        self.assertIn("messageText", serialized)
        self.assertIn("messageID", serialized)
        self.assertIn("repliedMessage", serialized)
        self.assertIn("promptID", serialized)
        self.assertIn("isAnnouncement", serialized)
        self.assertIn("timeCreated", serialized)
        
        # Test invalid literal values
        with self.assertRaises(ValidationError):
            ChatbotsMqResponse(
                userID="user123",
                messageText="Test",
                bot="2",  # Invalid value, only "0" or "1" allowed
                message_id="test_id"
            )
            
        with self.assertRaises(ValidationError):
            ChatbotsMqResponse(
                userID="user123",
                messageText="Test",
                isAnnouncement="2",  # Invalid value, only "0" or "1" allowed
                message_id="test_id"
            )

    def test_prompt_completed_context(self):
        from neon_data_models.models.api.mq.chatbots import PromptCompletedContext, ChatbotsMqRequest
        from datetime import datetime, timezone
        
        # Create a test ChatbotsMqRequest for the prompt field
        request = ChatbotsMqRequest(
            username="test_user",
            cid="test_conversation",
            message_text="Test prompt",
            message_id="test_message_id",
            time_created=datetime.now(tz=timezone.utc)
        )
        
        # Test initialization with required fields
        valid_kwargs = {
            "prompt": request,
            "is_active": True,
            "prompt_text": "Test prompt text",
            "available_subminds": ["submind1", "submind2"],
            "state": 1,
            "participating_subminds": ["submind1"],
            "proposed_responses": {"submind1": "Response 1"},
            "submind_opinions": {"submind1": "Opinion 1"},
            "votes": {"submind1": "vote1"},
            "votes_per_submind": {"submind1": ["vote1"]}
        }
        
        context = PromptCompletedContext(**valid_kwargs)
        self.assertIsInstance(context, PromptCompletedContext)
        self.assertEqual(context.prompt, request)
        self.assertTrue(context.is_active)
        self.assertEqual(context.prompt_text, "Test prompt text")
        self.assertEqual(context.available_subminds, ["submind1", "submind2"])
        self.assertEqual(context.state, 1)
        self.assertEqual(context.participating_subminds, ["submind1"])
        self.assertEqual(context.proposed_responses, {"submind1": "Response 1"})
        self.assertEqual(context.submind_opinions, {"submind1": "Opinion 1"})
        self.assertEqual(context.votes, {"submind1": "vote1"})
        self.assertEqual(context.votes_per_submind, {"submind1": ["vote1"]})
        self.assertEqual(context.winner, "")  # Default value
        
        # Test with winner field
        context_with_winner = PromptCompletedContext(
            **valid_kwargs,
            winner="submind1"
        )
        self.assertEqual(context_with_winner.winner, "submind1")
        
        # Test missing required fields
        with self.assertRaises(ValidationError):
            PromptCompletedContext(
                is_active=True,
                prompt_text="Test prompt text",
                available_subminds=["submind1", "submind2"],
                state=1,
                participating_subminds=["submind1"],
                proposed_responses={"submind1": "Response 1"},
                submind_opinions={"submind1": "Opinion 1"},
                votes={"submind1": "vote1"},
                votes_per_submind={"submind1": ["vote1"]}
            )

    def test_chatbots_mq_save_prompt(self):
        from neon_data_models.models.api.mq.chatbots import ChatbotsMqSavePrompt, PromptCompletedContext, ChatbotsMqRequest
        from datetime import datetime, timezone
        
        # Create necessary components for testing
        request = ChatbotsMqRequest(
            username="test_user",
            cid="test_conversation",
            message_text="Test prompt",
            message_id="test_message_id",
            time_created=datetime.now(tz=timezone.utc)
        )
        
        context = PromptCompletedContext(
            prompt=request,
            is_active=False,
            prompt_text="Test prompt text",
            available_subminds=["submind1", "submind2"],
            state=2,
            participating_subminds=["submind1"],
            proposed_responses={"submind1": "Response 1"},
            submind_opinions={"submind1": "Opinion 1"},
            votes={"submind1": "vote1"},
            votes_per_submind={"submind1": ["vote1"]},
            winner="submind1"
        )
        
        # Test initialization
        valid_kwargs = {
            "userID": "user123",
            "messageText": "Prompt completed",
            "message_id": "test_message_id",
            "prompt_id": "prompt123",
            "prompt_text": "Test prompt text",
            "created_on": "2023-01-01",
            "context": context
        }
        
        save_prompt = ChatbotsMqSavePrompt(**valid_kwargs)
        self.assertIsInstance(save_prompt, ChatbotsMqSavePrompt)
        self.assertEqual(save_prompt.user_id, "user123")
        self.assertEqual(save_prompt.message_text, "Prompt completed")
        self.assertEqual(save_prompt.prompt_id, "prompt123")
        self.assertEqual(save_prompt.prompt_text, "Test prompt text")
        self.assertEqual(save_prompt.created_on, "2023-01-01")
        self.assertEqual(save_prompt.context, context)
        
        # Test model_dump inheritance from ChatbotsMqResponse
        serialized = save_prompt.model_dump()
        self.assertIn("userID", serialized)
        self.assertIn("messageText", serialized)
        self.assertIn("prompt_id", serialized)
        self.assertIn("context", serialized)
        
        # Test missing required fields
        with self.assertRaises(ValidationError):
            ChatbotsMqSavePrompt(
                userID="user123",
                messageText="Prompt completed",
                message_id="test_message_id",
                prompt_id="prompt123",
                prompt_text="Test prompt text",
                created_on="2023-01-01"
                # Missing context
            )

    def test_chatbots_mq_new_prompt(self):
        from neon_data_models.models.api.mq.chatbots import ChatbotsMqNewPrompt
        from datetime import datetime, timezone
        
        # Test initialization with required fields
        valid_kwargs = {
            "user_id": "user123",
            "messageText": "New prompt",
            "message_id": "test_message_id",
            "prompt_id": "prompt123",
            "prompt_text": "Test prompt text"
        }
        
        new_prompt = ChatbotsMqNewPrompt(**valid_kwargs)
        self.assertIsInstance(new_prompt, ChatbotsMqNewPrompt)
        self.assertEqual(new_prompt.user_id, "user123")
        self.assertEqual(new_prompt.message_text, "Test prompt text")
        self.assertEqual(new_prompt.prompt_id, "prompt123")
        self.assertEqual(new_prompt.prompt_text, "Test prompt text")
        self.assertIsNone(new_prompt.context)
        
        # Test with conversation_context alias
        context_kwargs = {
            "user_id": "user123",
            "messageText": "New prompt with context",
            "message_id": "test_message_id",
            "prompt_id": "prompt123",
            "prompt_text": "Test prompt text",
            "conversation_context": {"some_key": "some_value"}
        }
        
        context_prompt = ChatbotsMqNewPrompt(**context_kwargs)
        self.assertEqual(context_prompt.context, {"some_key": "some_value"})
        
        # Test model validator
        # Create a message with prompt_text but no messageText
        partial_kwargs = {
            "user_id": "user123",
            "message_id": "test_message_id",
            "prompt_id": "prompt123",
            "prompt_text": "Only prompt text"
        }
        
        partial_prompt = ChatbotsMqNewPrompt(**partial_kwargs)
        self.assertEqual(partial_prompt.message_text, "Only prompt text")
        
        # Test model_dump inheritance from ChatbotsMqResponse
        serialized = new_prompt.model_dump()
        self.assertIn("user_id", serialized)
        self.assertIn("messageText", serialized)
        self.assertIn("prompt_id", serialized)
        
        # Test missing required fields
        with self.assertRaises(ValidationError):
            ChatbotsMqNewPrompt(
                user_id="user123",
                messageText="New prompt",
                message_id="test_message_id"
                # Missing prompt_id
            )
            
        with self.assertRaises(ValidationError):
            ChatbotsMqNewPrompt(
                user_id="user123",
                message_id="test_message_id",
                prompt_id="prompt123"
                # Missing messageText or prompt_text
            )

    def test_old_class_names_compatibility(self):
        """Test backward compatibility with old class names"""
        import neon_data_models.models.api.mq.chatbots as chatbots_module
        
        # Check if the old class names are still available through __all__
        self.assertIn("ChatbotsMqRequest", chatbots_module.__all__)
        self.assertIn("ChatbotsMqResponse", chatbots_module.__all__)
        self.assertIn("ChatbotsMqSavePrompt", chatbots_module.__all__)
        self.assertIn("ChatbotsMqNewPrompt", chatbots_module.__all__)
        
        # Import the actual classes to verify they exist
        from neon_data_models.models.api.mq.chatbots import ChatbotsMqRequest, ChatbotsMqResponse
        from neon_data_models.models.api.mq.chatbots import ChatbotsMqSavePrompt, ChatbotsMqNewPrompt
        
        # Test instantiation with basic properties
        req = ChatbotsMqRequest(
            username="test_user",
            cid="test_conversation",
            message_text="Test message",
            message_id="test_message_id",
            time_created=datetime.now(timezone.utc)
        )
        self.assertIsInstance(req, ChatbotsMqRequest)
        
        resp = ChatbotsMqResponse(
            userID="test_user",
            messageText="Test response",
            message_id="test_message_id"
        )
        self.assertIsInstance(resp, ChatbotsMqResponse)
        
        # These tests verify that the classes are properly defined and usable
        # even with the new names

    def test_connected_submind(self):
        from neon_data_models.models.api.mq.chatbots import ConnectedSubmind
        from neon_data_models.enum import CcaiState
        from neon_data_models.types import BotType
        
        # Test valid initialization with required fields
        current_time = datetime.now(tz=timezone.utc)
        valid_kwargs = {
            "message_id": "test_message_id",
            "bot_type": "submind",
            "service_name": "test_service",
            "cid": "test_conversation",
            "dom": "test_domain",
            "conversation_state": CcaiState.IDLE,
            "responded_shout": "test_shout_id",
            "shout": "chatbot state",
            "context": {"key": "value"},
            "prompt_id": "test_prompt_id",
            "omit_reply": False,
            "no_save": False,
            "attached_cids": ["cid1", "cid2"],
            "supports_raw_shouts": True,
            "last_ping": current_time
        }
        
        submind = ConnectedSubmind(**valid_kwargs)
        self.assertIsInstance(submind, ConnectedSubmind)
        self.assertIsInstance(submind.bot_type, str)
        self.assertEqual(submind.service_name, "test_service")
        self.assertEqual(submind.attached_cids, ["cid1", "cid2"])
        self.assertEqual(submind.last_ping, current_time)
        self.assertTrue(submind.supports_raw_shouts)
        
        # Test model_dump functionality
        serialized = submind.model_dump()
        self.assertIsInstance(serialized["bot_type"], str)
        self.assertEqual(serialized["service_name"], "test_service")
        self.assertEqual(serialized["attached_cids"], ["cid1", "cid2"])
        
        # Test missing required fields
        with self.assertRaises(ValidationError):
            ConnectedSubmind(
                message_id="test_message_id",
                service_name="test_service")

        # Test validation logic for deprecated fields
        deprecated_kwargs = valid_kwargs.copy()
        deprecated_kwargs["bot_type"] = "proctor"
        deprecated_kwargs["shout"] = "hello"
        submind = ConnectedSubmind(**deprecated_kwargs)
        self.assertEqual(submind.bot_type, "facilitator")
        self.assertEqual(submind.shout, "chatbot state")

    def test_chatbots_mq_subminds_state(self):
        from neon_data_models.models.api.mq.chatbots import ChatbotsMqSubmindsState, ConnectedSubmind
        from neon_data_models.enum import SubmindStatus
        from neon_data_models.models.api.mq.chatbots import CcaiState
        from datetime import datetime, timezone
        
        # Create test ConnectedSubmind for use in the test
        current_time = datetime.now(tz=timezone.utc)
        connected_submind = ConnectedSubmind(
            message_id="connected_mid",
            bot_type="submind",
            service_name="test_service",
            cid="test_conversation",
            dom="test_domain",
            conversation_state=CcaiState.IDLE,
            responded_shout="test_shout_id",
            shout="chatbot state",
            context={"key": "value"},
            prompt_id="test_prompt_id",
            omit_reply=False,
            no_save=False,
            attached_cids=["cid1", "cid2"],
            supports_raw_shouts=True,
            last_ping=current_time
        )
        
        # Create SubmindState objects for testing
        submind_state1 = {"submind_id": "submind1", "status": SubmindStatus.ACTIVE}
        submind_state2 = {"submind_id": "submind2", "status": SubmindStatus.BANNED}
        
        # Test valid initialization
        valid_kwargs = {
            "message_id": "test_message_id",
            "subminds_per_cid": {
                "cid1": [submind_state1, submind_state2],
                "cid2": [submind_state1]
            },
            "connected_subminds": {
                "submind1": connected_submind
            },
            "cid_submind_bans": {
                "cid1": ["banned_submind1"],
                "cid2": ["banned_submind2", "banned_submind3"]
            },
            "banned_subminds": ["globally_banned1", "globally_banned2"]
        }
        
        state = ChatbotsMqSubmindsState(**valid_kwargs)
        self.assertIsInstance(state, ChatbotsMqSubmindsState)
        
        # Test the nested SubmindState objects
        self.assertEqual(state.subminds_per_cid["cid1"][0].submind_id, "submind1")
        self.assertEqual(state.subminds_per_cid["cid1"][0].status, SubmindStatus.ACTIVE)
        self.assertEqual(state.subminds_per_cid["cid1"][1].submind_id, "submind2")
        self.assertEqual(state.subminds_per_cid["cid1"][1].status, SubmindStatus.BANNED)
        
        # Test the connected_subminds mapping
        self.assertIsInstance(state.connected_subminds["submind1"], ConnectedSubmind)
        self.assertEqual(state.connected_subminds["submind1"].service_name, "test_service")
        
        # Test the ban lists
        self.assertEqual(state.cid_submind_bans["cid1"], ["banned_submind1"])
        self.assertEqual(state.cid_submind_bans["cid2"], ["banned_submind2", "banned_submind3"])
        self.assertEqual(state.banned_subminds, ["globally_banned1", "globally_banned2"])
        
        # Test model_dump functionality
        serialized = state.model_dump()
        self.assertIn("subminds_per_cid", serialized)
        self.assertIn("connected_subminds", serialized)
        self.assertIn("cid_submind_bans", serialized)
        self.assertIn("banned_subminds", serialized)
        
        # Test missing required fields
        with self.assertRaises(ValidationError):
            ChatbotsMqSubmindsState(
                message_id="test_message_id"
                # Missing other required fields
            )

    def test_chatbots_mq_configured_personas_request(self):
        from neon_data_models.models.api.mq.chatbots import ChatbotsMqConfiguredPersonasRequest
        
        # Test valid initialization
        valid_request = ChatbotsMqConfiguredPersonasRequest(
            service_name="test_service",
            message_id="test_message_id"
        )
        self.assertIsInstance(valid_request, ChatbotsMqConfiguredPersonasRequest)
        self.assertEqual(valid_request.service_name, "test_service")
        self.assertEqual(valid_request.message_id, "test_message_id")
        
        # Test serialization
        serialized = valid_request.model_dump()
        self.assertEqual(serialized["service_name"], "test_service")
        self.assertEqual(serialized["message_id"], "test_message_id")
        
        # Test missing MQ required data
        with self.assertRaises(ValidationError):
            ChatbotsMqConfiguredPersonasRequest(service_name="test_service")
        
        # Test missing service_name
        with self.assertRaises(ValidationError):
            ChatbotsMqConfiguredPersonasRequest(message_id="test_message_id")

    def test_chatbots_mq_configured_personas_response(self):
        from neon_data_models.models.api.mq.chatbots import ChatbotsMqConfiguredPersonasResponse
        from neon_data_models.models.api.mq.chatbots import ChatbotsMqConfiguredPersonasRequest
        from neon_data_models.models.api.llm import LLMPersona
        
        # Create test data
        current_time = datetime.now(tz=timezone.utc)
        test_personas = [
            LLMPersona(
                name="persona1",
                system_prompt="System prompt 1",
                # supported_llms=["test_service", "another_service"]
            ),
            LLMPersona(
                name="persona2",
                system_prompt="System prompt 2",
                # supported_llms=["test_service"]
            )
        ]
        
        # Test valid initialization
        valid_response = ChatbotsMqConfiguredPersonasResponse(
            update_time=current_time,
            items=test_personas,
            message_id="test_message_id"
        )
        self.assertIsInstance(valid_response, ChatbotsMqConfiguredPersonasResponse)
        self.assertEqual(valid_response.update_time, current_time)
        self.assertEqual(len(valid_response.items), 2)
        self.assertEqual(valid_response.items[0].name, "persona1")
        self.assertEqual(valid_response.items[1].name, "persona2")
        
        # Test model_dump behavior with persona_name addition
        serialized = valid_response.model_dump()
        self.assertEqual(serialized["items"][0]["persona_name"], "persona1")
        self.assertEqual(serialized["items"][1]["persona_name"], "persona2")
        
        # Test from_persona_request method with ChatbotsMqConfiguredPersonasRequest
        response_data = {
            "update_time": current_time,
            "items": [
                {
                    "name": "persona1",
                    "system_prompt": "System prompt 1",
                    "supported_llms": ["test_service", "another_service"]
                },
                {
                    "name": "persona2",
                    "system_prompt": "System prompt 2",
                    "supported_llms": ["test_service"]
                },
                {
                    "name": "persona3",
                    "system_prompt": "System prompt 3",
                    "supported_llms": ["another_service"]
                }
            ]
        }
        
        # Create a request object
        request = ChatbotsMqConfiguredPersonasRequest(
            service_name="test_service",
            message_id="test_req_id",
            routing_key="test.routing.key",
            user_id="test_user"
        )
        
        filtered_response = ChatbotsMqConfiguredPersonasResponse.from_persona_request(
            response_data, request
        )
        
        # Verify filtering based on service_name
        self.assertEqual(len(filtered_response.items), 2)  # Only personas with "test_service" in supported_llms
        self.assertEqual(filtered_response.items[0].name, "persona1")
        self.assertEqual(filtered_response.items[1].name, "persona2")
        
        # Verify request properties are preserved
        self.assertEqual(filtered_response.message_id, "test_req_id")
        self.assertEqual(filtered_response.routing_key, "test.routing.key")
        
        # Test backward compatibility - omitting context
        response_without_context = ChatbotsMqConfiguredPersonasResponse(
            update_time=current_time,
            items=test_personas,
            message_id="test_message_id"
        )
        self.assertIsInstance(
            response_without_context.context['mq']['message_id'], str)
        
        # Test missing required fields
        with self.assertRaises(ValidationError):
            ChatbotsMqConfiguredPersonasResponse(
                update_time=current_time,
                items=test_personas
                # Missing message_id
            )
            
        with self.assertRaises(ValidationError):
            ChatbotsMqConfiguredPersonasResponse(
                message_id="test_message_id",
                items=test_personas
                # Missing update_time
            )
            
        with self.assertRaises(ValidationError):
            ChatbotsMqConfiguredPersonasResponse(
                message_id="test_message_id",
                update_time=current_time
                # Missing items
            )

    def test_chatbots_mq_prompts_data_request(self):
        from neon_data_models.models.api.mq.chatbots import ChatbotsMqPromptsDataRequest

        # Test valid initialization
        valid_request = ChatbotsMqPromptsDataRequest(message_id="test_message_id")
        self.assertIsInstance(valid_request, ChatbotsMqPromptsDataRequest)
        self.assertEqual(valid_request.message_id, "test_message_id")

        # Test missing required fields
        with self.assertRaises(ValidationError):
            ChatbotsMqPromptsDataRequest()

    def test_chatbots_mq_prompts_data_response(self):
        from neon_data_models.models.api.mq.chatbots import ChatbotsMqPromptsDataResponse, ChatbotsMqPromptsDataRequest

        # Test valid initialization
        valid_response = ChatbotsMqPromptsDataResponse(
            message_id="test_message_id", records=["prompt1", "prompt2"]
        )
        self.assertIsInstance(valid_response, ChatbotsMqPromptsDataResponse)
        self.assertEqual(valid_response.records, ["prompt1", "prompt2"])

        # Test from_prompt_data_request method
        request = ChatbotsMqPromptsDataRequest(message_id="test_message_id")
        response_data = {"records": ["prompt1", "prompt2"]}
        response = ChatbotsMqPromptsDataResponse.from_prompt_data_request(
            response_data, request
        )
        self.assertEqual(response.message_id, "test_message_id")
        self.assertEqual(response.records, ["prompt1", "prompt2"])

        # Test missing required fields
        with self.assertRaises(ValidationError):
            ChatbotsMqPromptsDataResponse(records=["prompt1", "prompt2"])
