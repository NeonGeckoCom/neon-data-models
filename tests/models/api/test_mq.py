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

from neon_data_models.models.api.mq import UserDbRequest


class TestMQ(TestCase):
    def test_create_user_db_request(self):
        from neon_data_models.models.api.mq import CreateUserRequest

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
        from neon_data_models.models.api.mq import ReadUserRequest

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
        from neon_data_models.models.api.mq import UpdateUserRequest

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
        from neon_data_models.models.api.mq import DeleteUserRequest

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

    def test_mq_llm_propose_request(self):
        from neon_data_models.models.api.mq import LLMProposeRequest
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
        from neon_data_models.models.api.mq import LLMProposeResponse

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
        from neon_data_models.models.api.mq import LLMDiscussRequest
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
        from neon_data_models.models.api.mq import LLMDiscussResponse

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
        from neon_data_models.models.api.mq import LLMVoteRequest
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
        from neon_data_models.models.api.mq import LLMVoteResponse

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
                            message_id=""),

