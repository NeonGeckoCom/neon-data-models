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

        # # Invalid MQ Context
        # with self.assertRaises(ValidationError):
        #     LLMProposeRequest(query=query, history=history)

        # Invalid LLM Request
        with self.assertRaises(ValidationError):
            LLMProposeRequest(history=history, message_id=message_id)

    def test_mq_llm_propose_response(self):
        from neon_data_models.models.api.mq.llm import LLMProposeResponse

        # Valid response
        self.assertIsInstance(LLMProposeResponse(response="test response",
                                                 message_id=""),
                              LLMProposeResponse)

        # # Missing MQ required data
        # with self.assertRaises(ValidationError):
        #     LLMProposeResponse(response="test response")

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

        # # Invalid MQ Context
        # with self.assertRaises(ValidationError):
        #     LLMDiscussRequest(query=query, history=history, options=opts)

        # Invalid LLM Request
        with self.assertRaises(ValidationError):
            LLMDiscussRequest(query=query, message_id=message_id, options=opts)

    def test_mq_llm_discuss_response(self):
        from neon_data_models.models.api.mq.llm import LLMDiscussResponse

        # Valid response
        self.assertIsInstance(LLMDiscussResponse(opinion="test opinion",
                                                 message_id=""),
                              LLMDiscussResponse)

        # # Missing MQ required data
        # with self.assertRaises(ValidationError):
        #     LLMDiscussResponse(opinion="test opinion")

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

        # # Invalid MQ Context
        # with self.assertRaises(ValidationError):
        #     LLMVoteRequest(query=query, history=history, responses=responses)

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

        # # Missing MQ required data
        # with self.assertRaises(ValidationError):
        #     LLMVoteResponse(sorted_answer_indexes=[2, 0, 1])

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

    def test_chatbots_mq_submind_response(self):
        from neon_data_models.models.api.mq.chatbots import ChatbotsMqResponse, ChatbotsMqSubmindResponse
        
        # Test basic initialization with required fields
        current_time = datetime.now(tz=timezone.utc)
        valid_kwargs = {
            "userID": "user123",
            "messageText": "Hello, this is a response",
            "message_id": "test_message_id",
            "conversation_state": 0
        }
        
        response = ChatbotsMqResponse(**valid_kwargs)
        self.assertIsInstance(response, ChatbotsMqSubmindResponse)
        self.assertEqual(response.user_id, "user123")
        self.assertEqual(response.message_text, "Hello, this is a response")
        self.assertEqual(response.bot, "0")  # Default value check
        self.assertFalse(response.is_announcement)  # Default value check
        
        # Test with all fields including aliases
        full_kwargs = {
            "userID": "user123",
            "userDisplayName": "John Doe",
            "messageText": "Hello, this is a complete response",
            "messageID": "msg123",
            "repliedMessage": "original_msg456",
            "bot": "1",
            "promptID": "prompt789",
            "prompt_state": 2,
            "is_announcement": True,
            "timeCreated": current_time,
            "source": "test_source",
            "client": "test_client",
            "cid": "conversation123",
            "message_id": "message123"
        }
        
        full_response = ChatbotsMqResponse(**full_kwargs)
        self.assertIsInstance(full_response, ChatbotsMqSubmindResponse)
        self.assertEqual(full_response.user_id, "user123")
        self.assertEqual(full_response.username, "John Doe")
        self.assertEqual(full_response.message_text, "Hello, this is a complete response")
        self.assertEqual(full_response.sid, "msg123")
        self.assertEqual(full_response.replied_message, "original_msg456")
        self.assertEqual(full_response.bot, "1")
        self.assertEqual(full_response.prompt_id, "prompt789")
        self.assertEqual(full_response.prompt_state, 2)
        self.assertTrue(full_response.is_announcement)
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
                available_subminds=["submind1", "submind2"],
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
            "conversation_state": 0,
            "context": context
        }
        save_prompt = ChatbotsMqSavePrompt(**valid_kwargs)
        self.assertIsInstance(save_prompt, ChatbotsMqSavePrompt)
        self.assertEqual(save_prompt.user_id, "user123")
        self.assertEqual(save_prompt.message_text, "Prompt completed")
        self.assertEqual(save_prompt.prompt_id, "prompt123")
        # self.assertEqual(save_prompt.prompt_text, "Test prompt text")
        # self.assertEqual(save_prompt.created_on, "2023-01-01")
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
        
        # Test initialization with required fields
        valid_kwargs = {
            "user_id": "user123",
            "messageText": "New prompt",
            "message_id": "test_message_id",
            "prompt_id": "prompt123",
            "prompt_text": "Test prompt text",
            "conversation_state": 0
        }

        new_prompt = ChatbotsMqNewPrompt(**valid_kwargs)
        self.assertIsInstance(new_prompt, ChatbotsMqNewPrompt)
        self.assertEqual(new_prompt.user_id, "user123")
        self.assertEqual(new_prompt.message_text, valid_kwargs["messageText"])
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
            "conversation_state": 0,
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
            "prompt_text": "Only prompt text",
            "conversation_state": 0
        }
        partial_prompt = ChatbotsMqNewPrompt(**partial_kwargs)
        self.assertEqual(partial_prompt.message_text, '')

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
        from neon_data_models.models.api.mq.chatbots import ChatbotsMqRequest, ChatbotsMqResponse, ChatbotsMqSubmindResponse
        from neon_data_models.models.api.mq.chatbots import ChatbotsMqSavePrompt, ChatbotsMqNewPrompt
        
        # Test instantiation with basic properties
        req = ChatbotsMqRequest(
            username="test_user",
            cid="test_conversation",
            message_text="Test message",
            message_id="test_message_id",
            conversation_state=0,
            time_created=datetime.now(timezone.utc)
        )
        self.assertIsInstance(req, ChatbotsMqRequest)
        
        resp = ChatbotsMqResponse(
            userID="test_user",
            messageText="Test response",
            message_id="test_message_id",
            conversation_state=0,
        )
        self.assertIsInstance(resp, ChatbotsMqSubmindResponse)
        
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
            "supports_raw_conversation": True,
            "last_ping": current_time
        }
        
        submind = ConnectedSubmind(**valid_kwargs)
        self.assertIsInstance(submind, ConnectedSubmind)
        self.assertIsInstance(submind.bot_type, str)
        self.assertEqual(submind.service_name, "test_service")
        self.assertEqual(submind.attached_cids, ["cid1", "cid2"])
        self.assertEqual(submind.last_ping, current_time)
        self.assertTrue(submind.supports_raw_conversation)
        
        # Test model_dump functionality
        serialized = submind.model_dump()
        self.assertIsInstance(serialized["bot_type"], str)
        self.assertEqual(serialized["service_name"], "test_service")
        self.assertEqual(serialized["attached_cids"], ["cid1", "cid2"])

        # Test validation logic for deprecated fields
        deprecated_kwargs = valid_kwargs.copy()
        deprecated_kwargs["bot_type"] = "proctor"
        # deprecated_kwargs["shout"] = "hello"
        submind = ConnectedSubmind(**deprecated_kwargs)
        self.assertIsInstance(submind.bot_type, str)
        # self.assertEqual(submind.shout, "chatbot state")

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
            supports_raw_conversation=True,
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

        # # Test missing required fields
        # with self.assertRaises(ValidationError):
        #     ChatbotsMqPromptsDataRequest()

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

    def test_chatbots_mq_submind_response(self):
        from neon_data_models.models.api.mq.chatbots import ChatbotsMqSubmindResponse
        from datetime import datetime, timezone

        # Test basic initialization with required fields
        current_time = datetime.now(tz=timezone.utc)
        valid_kwargs = {
            "userID": "test_user",
            "messageText": "Test submind response",
            "message_id": "test_message_id",
            "prompt_state": 1,
        }
        
        response = ChatbotsMqSubmindResponse(**valid_kwargs)
        self.assertIsInstance(response, ChatbotsMqSubmindResponse)
        self.assertEqual(response.user_id, "test_user")
        self.assertEqual(response.message_text, "Test submind response")
        self.assertEqual(response.bot, "0")  # Default value check
        
        # Test with all fields including aliased fields
        full_kwargs = {
            "userID": "submind1",
            "userDisplayName": "Test Submind",
            "messageText": "Full test response",
            "messageID": "test_shout_id",
            "repliedMessage": "original_message_id",
            "bot": "1",
            "promptID": "prompt_id_123",
            "conversation_state": 2,
            "is_announcement": True,
            "timeCreated": current_time,
            "source": "test_source",
            "client": "test_client",
            "cid": "conversation123",
            "message_id": "test_message_id"
        }
        
        full_response = ChatbotsMqSubmindResponse(**full_kwargs)
        self.assertIsInstance(full_response, ChatbotsMqSubmindResponse)
        self.assertEqual(full_response.user_id, "submind1")
        self.assertEqual(full_response.username, "Test Submind")
        self.assertEqual(full_response.message_text, "Full test response")
        self.assertEqual(full_response.sid, "test_shout_id")
        self.assertEqual(full_response.replied_message, "original_message_id")
        self.assertEqual(full_response.bot, "1")
        self.assertEqual(full_response.prompt_id, "prompt_id_123")
        self.assertEqual(full_response.prompt_state, 2)
        self.assertTrue(full_response.is_announcement)
        self.assertEqual(full_response.time_created, current_time)
        self.assertEqual(full_response.source, "test_source")
        
        # Test alternate field names (validate_inputs validator)
        alternate_kwargs = {
            "nick": "submind2",
            "shout": "Message using alternate field names",
            "responded_shout": "parent_message_id",
            "time": current_time.timestamp(),
            "message_id": "test_message_id",
            "conversation_state": 2,
        }
        
        alternate_response = ChatbotsMqSubmindResponse(**alternate_kwargs)
        self.assertEqual(alternate_response.user_id, "submind2")
        self.assertEqual(alternate_response.message_text, "Message using alternate field names")
        self.assertEqual(alternate_response.replied_message, "parent_message_id")
        
        # Test model_dump serialization
        serialized = full_response.model_dump(by_alias=True)
        self.assertEqual(serialized["userID"], "submind1")
        self.assertEqual(serialized["messageText"], "Full test response")
        self.assertTrue(serialized["isAnnouncement"])
        self.assertEqual(serialized["nick"], "submind1")  # Check backwards compatibility field
        self.assertEqual(serialized["shout"], "Full test response")  # Check backwards compatibility field
        
        # Test missing required fields
        with self.assertRaises(ValidationError):
            ChatbotsMqSubmindResponse(messageText="Missing user_id", message_id="test_id")
        
        with self.assertRaises(ValidationError):
            ChatbotsMqSubmindResponse(userID="test_user", message_id="test_id")

    def test_chatbots_mq_response_type_adapter(self):
        from neon_data_models.models.api.mq.chatbots import ChatbotsMqResponse
        from neon_data_models.models.api.mq.chatbots import ChatbotsMqSubmindResponse, ChatbotsMqSavePrompt, ChatbotsMqNewPrompt
        from neon_data_models.enum import CcaiControl
        from datetime import datetime, timezone
        
        current_time = datetime.now(tz=timezone.utc)
        
        # Test regular submind response
        regular_message = {
            "userID": "submind1",
            "messageText": "Regular response",
            "conversation_state": 2,
            "message_id": "test_message_id"
        }
        
        result = ChatbotsMqResponse(**regular_message)
        self.assertIsInstance(result, ChatbotsMqSubmindResponse)
        self.assertEqual(result.user_id, "submind1")
        self.assertEqual(result.message_text, "Regular response")
        
        # Test new prompt message
        new_prompt_message = {
            "routing_key": None,
            "message_id": "8ee915f080ae416da1f31081cc4f945a",
            "sid": "",
            "cid": "35d5dff220",
            "title": "",
            "user_id": "proctor-f3277918bcc947359994f711452450b6",
            "username": None,
            "message_text": "!MSG:CREATE_PROMPT",
            "replied_message": None,
            "bot": "1",
            "prompt_id": "f747c1f3caeb4975983b2eb52c35491e",
            "prompt_text": "Why is testing important?",
            "prompt_state": 1,
            "is_announcement": False,
            "time_created": current_time,
            "source": "klat_observer",
            "bot_type": "proctor",
            "service_name": "proctor",
            "context": {},
            "dom": "",
            "omit_reply": True,
            "no_save": False,
            "created_on": 1743531762,
        }

        alt_new_prompt_message = {
            "nick": "proctor-ac18f03d0937490080c798d3b242ecd0",
            "bot_type": "proctor",
            "service_name": "proctor",
            "cid": "35d5dff220",
            "dom": "",
            "conversation_state": 1,
            "responded_shout": None,
            "shout": "!MSG:CREATE_PROMPT",
            "context": {},
            "prompt_id": "00cbbd4c9f33422f9628c7b0c2e90c5b",
            "time": "1743539074",
            "prompt_text": "Why is testing important?",
            "created_on": 1743539074,
            "omit_reply": True,
            "no_save": False,
            "message_id": "f7affd3166244e74ba814f92ccd26eb7",
            "bot": "1"
        }

        result = ChatbotsMqResponse(**new_prompt_message)
        self.assertIsInstance(result, ChatbotsMqNewPrompt)
        self.assertEqual(result.prompt_id, new_prompt_message['prompt_id'])
        
        alt_response = ChatbotsMqResponse(**alt_new_prompt_message)
        self.assertIsInstance(alt_response, ChatbotsMqNewPrompt)
        self.assertEqual(alt_response.user_id, alt_new_prompt_message['nick'])
        

        # Test save prompt message
        save_prompt_message = {
            "routing_key": None,
            "message_id": "e2ad6e92438f4ec0acaa386e22e24954",
            "sid": "",
            "cid": "35d5dff220",
            "title": "",
            "user_id": "proctor-f3277918bcc947359994f711452450b6",
            "username": None,
            "message_text": "!MSG:SAVE_PROMPT_RESULTS",
            "replied_message": None,
            "bot": "1",
            "prompt_id": "prompt_123",
            "prompt_state": 4,
            "is_announcement": False,
            "time_created": current_time,
            "source": "klat_observer",
            "bot_type": "proctor",
            "service_name": "proctor",
            "context": {
                "winner": "submind1",
                "prompt_text": "Test prompt"
            },
            "dom": "",
            "omit_reply": True,
            "no_save": False
        }
        alt_save_prompt_message = {
            "nick": "proctor-ac18f03d0937490080c798d3b242ecd0",
            "bot_type": "proctor",
            "service_name": "proctor",
            "cid": "35d5dff220",
            "dom": "",
            "conversation_state": 4,
            "responded_shout": None,
            "shout": "!MSG:SAVE_PROMPT_RESULTS",
            "context": {},
            "prompt_id": "",
            "time": "1743539090",
            "omit_reply": True,
            "conversation_context": {
                "message_id": "66d5c444961243d9bf95c5a068b0211a",
                "state": 4,
                "prompt": {
                    "routing_key": None,
                    "message_id": "98add3204f",
                    "sid": "7f80ae0d-a5a9-440d-f113-df167b70be9e",
                    "cid": "35d5dff220",
                    "title": "",
                    "username": "ca45d1ea45134523af7f",
                    "message_text": "Why is testing important?",
                    "from_bot": False,
                    "prompt_id": "00cbbd4c9f33422f9628c7b0c2e90c5b",
                    "prompt_state": None,
                    "time_created": 1743539036.0,
                    "requested_participants": [
                    "proctor"
                    ],
                    "recipient": None,
                    "bound_service": "",
                    "bot": "0",
                    "messageText": "Why is testing important?",
                    "nick": "ca45d1ea45134523af7f"
                },
                "is_active": True,
                "prompt_text": "Why is testing important?",
                "available_subminds": [
                    "nucleotidings_vllm",
                    "logistics_vllm",
                    "neon_vllm"
                ],
                "nick_mapping": {},
                "participating_subminds": [
                    "nucleotidings_vllm",
                    "logistics_vllm",
                    "neon_vllm"
                ],
                "proposed_responses": {
                    "neon_vllm": "Testing is crucial.",
                    "logistics_vllm": "Testing is important.",
                    "nucleotidings_vllm": "Testing is important."
                },
                "submind_opinions": {
                    "neon_vllm": "The answer provided by \"logistics_vllm\" is the best answer",
                    "nucleotidings_vllm": "The answer provided by 'logistics_vllm' is considered the best.",
                    "logistics_vllm": "The answer provided by \"nucleotidings_vllm\" is the best answer."
                },
                "votes": {
                    "neon_vllm": "logistics_vllm",
                    "logistics_vllm": "nucleotidings_vllm",
                    "nucleotidings_vllm": "logistics_vllm"
                },
                "votes_per_submind": {
                    "logistics_vllm": [
                    "neon_vllm",
                    "nucleotidings_vllm"
                    ],
                    "nucleotidings_vllm": [
                    "logistics_vllm"
                    ]
                },
                "winner": "logistics_vllm"
            },
            "no_save": False,
            "message_id": "6924c0422b9347ae9604e4e97cd0847a",
            "bot": "1"
        }
        
        result = ChatbotsMqResponse(**save_prompt_message)
        self.assertIsInstance(result, ChatbotsMqSavePrompt)
        self.assertEqual(result.prompt_id, "prompt_123")
        # self.assertIsNone(result.created_on)
        self.assertEqual(result.context.winner, "submind1")
        self.assertIsInstance(ChatbotsMqResponse(**alt_save_prompt_message),
                              ChatbotsMqSavePrompt)

        # Test with message_text vs messageText
        alternate_syntax = {
            "userID": "submind1",
            "message_text": "Using message_text instead of messageText",
            "conversation_state": 2,
            "message_id": "test_message_id"
        }
        
        result = ChatbotsMqResponse(**alternate_syntax)
        self.assertIsInstance(result, ChatbotsMqSubmindResponse)
        self.assertEqual(result.message_text, "Using message_text instead of messageText")

    def test_chatbots_mq_submind_connection(self):
        from neon_data_models.models.api.mq.chatbots import ChatbotsMqSubmindConnection
        from datetime import datetime, timezone
        
        # Test basic initialization
        current_time = datetime.now(tz=timezone.utc)
        valid_kwargs = {
            "nick": "submind1",
            "time": current_time,
            "message_id": "test_message_id"
        }
        
        connection = ChatbotsMqSubmindConnection(**valid_kwargs)
        self.assertIsInstance(connection, ChatbotsMqSubmindConnection)
        self.assertEqual(connection.user_id, "submind1")  # Check aliased field
        self.assertEqual(connection.time, current_time)
        
        # Test with all fields
        minimal_kwargs = {
            "user_id": "submind2",
            "time": current_time,
            "cids": ["conversation1", "conversation2"],
            "supports_raw_conversation": True,
            "message_id": "test_message_id"
        }
        
        full_connection = ChatbotsMqSubmindConnection(**minimal_kwargs)
        self.assertEqual(full_connection.user_id, "submind2")
        self.assertEqual(full_connection.cids, ["conversation1", "conversation2"])
        
        # With context
        minimal_kwargs = {
            "user_id": "submind_2-longuuidstring",
            "time": current_time,
            "cids": ["conversation1", "conversation2"],
            "supports_raw_conversation": True,
            "message_id": "test_message_id",
            "context": {}
        }
        parsed_service_name = ChatbotsMqSubmindConnection(**minimal_kwargs)
        self.assertEqual(parsed_service_name.context.service_name, "submind_2")
        
        # Test missing required fields
        with self.assertRaises(ValidationError):
            ChatbotsMqSubmindConnection(time=current_time, message_id="test_id")
        
        with self.assertRaises(ValidationError):
            ChatbotsMqSubmindConnection(user_id="submind1", time=current_time,
                                        cids="invalid_type")

    def test_chatbots_mq_submind_disconnection(self):
        from neon_data_models.models.api.mq.chatbots import ChatbotsMqSubmindDisconnection
        
        # Test basic initialization
        valid_kwargs = {
            "nick": "submind1",
            "message_id": "test_message_id"
        }
        
        disconnection = ChatbotsMqSubmindDisconnection(**valid_kwargs)
        self.assertIsInstance(disconnection, ChatbotsMqSubmindDisconnection)
        self.assertEqual(disconnection.user_id, "submind1")  # Check aliased field
        
        # Test with user_id instead of nick
        alternate_kwargs = {
            "user_id": "submind2",
            "message_id": "test_message_id"
        }
        
        alternate_disconnection = ChatbotsMqSubmindDisconnection(**alternate_kwargs)
        self.assertEqual(alternate_disconnection.user_id, "submind2")
        
        # Test missing required fields
        with self.assertRaises(ValidationError):
            ChatbotsMqSubmindDisconnection(message_id="test_id")

    def test_chatbots_mq_submind_invitation(self):
        from neon_data_models.models.api.mq.chatbots import ChatbotsMqSubmindInvitation
        
        # Test basic initialization
        valid_kwargs = {
            "cid": "conversation123",
            "requested_participants": ["submind1", "submind2"],
            "message_id": "test_message_id"
        }
        
        invitation = ChatbotsMqSubmindInvitation(**valid_kwargs)
        self.assertIsInstance(invitation, ChatbotsMqSubmindInvitation)
        self.assertEqual(invitation.cid, "conversation123")
        self.assertEqual(invitation.requested_participants, ["submind1", "submind2"])
        
        # Test missing required fields
        with self.assertRaises(ValidationError):
            ChatbotsMqSubmindInvitation(cid="conversation123", message_id="test_id")
        
        with self.assertRaises(ValidationError):
            ChatbotsMqSubmindInvitation(requested_participants=["submind1"], message_id="test_id")

    def test_chatbots_mq_update_participating_subminds(self):
        from neon_data_models.models.api.mq.chatbots import ChatbotsMqUpdateParticipatingSubminds
        
        # Test basic initialization with required fields
        valid_kwargs = {
            "cid": "conversation123",
            "message_id": "test_message_id"
        }
        
        update = ChatbotsMqUpdateParticipatingSubminds(**valid_kwargs)
        self.assertIsInstance(update, ChatbotsMqUpdateParticipatingSubminds)
        self.assertEqual(update.cid, "conversation123")
        self.assertEqual(update.subminds_to_invite, [])  # Default value
        self.assertEqual(update.subminds_to_kick, [])  # Default value
        
        # Test with all fields
        full_kwargs = {
            "cid": "conversation123",
            "subminds_to_invite": ["new_submind1", "new_submind2"],
            "subminds_to_kick": ["old_submind1"],
            "message_id": "test_message_id"
        }
        
        full_update = ChatbotsMqUpdateParticipatingSubminds(**full_kwargs)
        self.assertEqual(full_update.subminds_to_invite, ["new_submind1", "new_submind2"])
        self.assertEqual(full_update.subminds_to_kick, ["old_submind1"])
        
        # Test missing required fields
        with self.assertRaises(ValidationError):
            ChatbotsMqUpdateParticipatingSubminds(subminds_to_invite=["submind1"], message_id="test_id")
        
        # TODO: Should this raise an exception if the request does nothing?
        # with self.assertRaises(ValidationError):
        #     ChatbotsMqUpdateParticipatingSubminds(cid="conversation123")

    def test_chatbots_mq_submind_conversation_ban(self):
        from neon_data_models.models.api.mq.chatbots import ChatbotsMqSubmindConversationBan
        
        # Test basic initialization
        valid_kwargs = {
            "nick": "submind1",
            "cid": "conversation123",
            "message_id": "test_message_id"
        }
        
        ban = ChatbotsMqSubmindConversationBan(**valid_kwargs)
        self.assertIsInstance(ban, ChatbotsMqSubmindConversationBan)
        self.assertEqual(ban.user_id, "submind1")  # Check aliased field
        self.assertEqual(ban.cid, "conversation123")
        
        # Test with user_id instead of nick
        alternate_kwargs = {
            "user_id": "submind2",
            "cid": "conversation456",
            "message_id": "test_message_id"
        }
        
        alternate_ban = ChatbotsMqSubmindConversationBan(**alternate_kwargs)
        self.assertEqual(alternate_ban.user_id, "submind2")
        self.assertEqual(alternate_ban.cid, "conversation456")
        
        # Test missing required fields
        with self.assertRaises(ValidationError):
            ChatbotsMqSubmindConversationBan(user_id="submind1", message_id="test_id")
        
        with self.assertRaises(ValidationError):
            ChatbotsMqSubmindConversationBan(cid="conversation123", message_id="test_id")

    def test_chatbots_mq_submind_global_ban(self):
        from neon_data_models.models.api.mq.chatbots import ChatbotsMqSubmindGlobalBan
        
        # Test basic initialization
        valid_kwargs = {
            "nick": "submind1",
            "message_id": "test_message_id"
        }
        
        ban = ChatbotsMqSubmindGlobalBan(**valid_kwargs)
        self.assertIsInstance(ban, ChatbotsMqSubmindGlobalBan)
        self.assertEqual(ban.user_id, "submind1")  # Check aliased field
        
        # Test with user_id instead of nick
        alternate_kwargs = {
            "user_id": "submind2",
            "message_id": "test_message_id"
        }
        
        alternate_ban = ChatbotsMqSubmindGlobalBan(**alternate_kwargs)
        self.assertEqual(alternate_ban.user_id, "submind2")
        
        # Test missing required fields
        with self.assertRaises(ValidationError):
            ChatbotsMqSubmindGlobalBan(message_id="test_id")

    def test_chatbots_mq_submind_response_error(self):
        from neon_data_models.models.api.mq.chatbots import ChatbotsMqSubmindResponseError
        
        # Test basic initialization
        valid_kwargs = {
            "message": "An error occurred",
            "message_id": "test_message_id"
        }
        
        error_response = ChatbotsMqSubmindResponseError(**valid_kwargs)
        self.assertIsInstance(error_response, ChatbotsMqSubmindResponseError)
        self.assertEqual(error_response.message, "An error occurred")
        self.assertEqual(error_response.message_id, "test_message_id")
        
        # Test with alias field
        alias_kwargs = {
            "msg": "An error with alias field",
            "message_id": "test_message_id"
        }
        
        alias_response = ChatbotsMqSubmindResponseError(**alias_kwargs)
        self.assertEqual(alias_response.message, "An error with alias field")
        
        # Test serialization
        serialized = error_response.model_dump()
        self.assertEqual(serialized["message"], "An error occurred")
        
        # Test by_alias serialization
        serialized_alias = error_response.model_dump(by_alias=True)
        self.assertEqual(serialized_alias["msg"], "An error occurred")
        
        # Test without message (should be None by default)
        no_message = ChatbotsMqSubmindResponseError(message_id="test_message_id")
        self.assertIsNone(no_message.message)

    def test_chatbots_mq_response_edge_cases(self):
        from neon_data_models.models.api.mq.chatbots import ChatbotsMqResponse
        from neon_data_models.models.api.mq.chatbots import ChatbotsMqSubmindResponse
        
        # Test with empty/minimal valid message
        minimal_message = {
            "userID": "test_user",
            "messageText": "",
            "message_id": "test_message_id"
        }
        
        result = ChatbotsMqResponse(**minimal_message)
        self.assertIsInstance(result, ChatbotsMqSubmindResponse)
        self.assertEqual(result.message_text, "")
        
        # Test with mixed aliased and non-aliased fields
        mixed_fields = {
            "userID": "test_user",
            "shout": "Using aliased shout field",
            "message_id": "test_message_id",
            "nick": "nick_value"  # This should be used for user_id too
        }
        
        result = ChatbotsMqResponse(**mixed_fields)
        self.assertIsInstance(result, ChatbotsMqSubmindResponse)
        self.assertEqual(result.message_text, "Using aliased shout field")
        self.assertEqual(result.user_id, "test_user")  # userID takes precedence over nick
        
        # Test with malformed timestamps that should be converted
        timestamp_message = {
            "userID": "test_user",
            "messageText": "Timestamp test",
            "created_on": "1611234567",  # String timestamp
            "time": 1611234567,  # Integer timestamp
            "message_id": "test_message_id"
        }
        
        result = ChatbotsMqResponse(**timestamp_message)
        self.assertIsInstance(result, ChatbotsMqSubmindResponse)
        # Ensure the timestamps are properly handled in serialization
        serialized = result.model_dump(by_alias=True)
        self.assertEqual(serialized["created_on"], 1611234567)
        
        # Test with null/None fields that should be handled
        null_fields = {
            "userID": "test_user",
            "messageText": "Test with nulls",
            "message_id": "test_message_id",
            "sid": None,  # Should be handled by the model validator
            "repliedMessage": None,
            "promptID": None
        }
        
        result = ChatbotsMqResponse(**null_fields)
        self.assertIsInstance(result, ChatbotsMqSubmindResponse)
        self.assertEqual(result.sid, "")  # Default value when None is provided
