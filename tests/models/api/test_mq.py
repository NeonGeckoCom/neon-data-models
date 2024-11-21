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
                                   auth_username="admin", auth_password="admin_pass")
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
