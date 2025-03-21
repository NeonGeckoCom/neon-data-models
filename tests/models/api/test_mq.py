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

