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

import base64
from unittest import TestCase
from datetime import datetime
from pydantic import ValidationError

from neon_data_models.enum import CcaiState


class TestKlatSocketIO(TestCase):
    def test_get_stt_request(self):
        """Test GetSttRequest model creation and validation"""
        from neon_data_models.models.api.klat.socketio import GetSttRequest
        
        # Test with required fields
        test_object = GetSttRequest(
            cid="test_conversation_id",
            sid="test_shout_id",
            user_uid="test_user_id"
        )
        self.assertIsInstance(test_object, GetSttRequest)
        self.assertEqual(test_object.cid, "test_conversation_id")
        self.assertEqual(test_object.sid, "test_shout_id")
        self.assertEqual(test_object.user_uid, "test_user_id")
        self.assertEqual(test_object.lang, "en-us")  # Default value
        
        # Test with alias parameter
        test_object = GetSttRequest(
            cid="test_conversation_id",
            message_id="test_message_id",
            user_id="test_user_uid"
        )
        self.assertEqual(test_object.sid, "test_message_id")
        self.assertEqual(test_object.user_uid, "test_user_uid")
        
        # Test serialization/deserialization
        dumped = test_object.model_dump()
        recreated = GetSttRequest(**dumped)
        self.assertEqual(test_object, recreated)

    def test_get_stt_response(self):
        """Test GetSttResponse model creation and validation"""
        from neon_data_models.models.api.klat.socketio import GetSttResponse
        
        # Test with required fields
        test_object = GetSttResponse(
            transcript="Hello world",
            sid="test_shout_id",
            cid="test_conversation_id"
        )
        self.assertIsInstance(test_object, GetSttResponse)
        self.assertEqual(test_object.transcript, "Hello world")
        self.assertEqual(test_object.sid, "test_shout_id")
        self.assertEqual(test_object.cid, "test_conversation_id")
        self.assertEqual(test_object.lang, "en-us")  # Default value
        self.assertEqual(test_object.context, {})  # Default value
        
        # Test with context extraction
        context = {"sid": "context_sid", "cid": "context_cid", "extra": "data"}
        test_object = GetSttResponse(
            transcript="Hello world",
            context=context
        )
        self.assertEqual(test_object.sid, "context_sid")
        self.assertEqual(test_object.cid, "context_cid")
        self.assertEqual(test_object.context["extra"], "data")

        # Test serialization/deserialization
        dumped = test_object.model_dump()
        recreated = GetSttResponse(**dumped)
        self.assertEqual(test_object, recreated)

    def test_get_tts_request(self):
        """Test GetTtsRequest model creation and validation"""
        from neon_data_models.models.api.klat.socketio import GetTtsRequest
        
        # Test with required fields
        test_object = GetTtsRequest(
            cid="test_conversation_id",
            sid="test_shout_id",
            user_uid="test_user_uid",
        )
        self.assertIsInstance(test_object, GetTtsRequest)
        self.assertEqual(test_object.cid, "test_conversation_id")
        self.assertEqual(test_object.sid, "test_shout_id")
        self.assertEqual(test_object.user_uid, "test_user_uid")
        self.assertEqual(test_object.lang, "en-us")  # Default value
        
        # Test with alias parameters
        test_object = GetTtsRequest(
            cid="test_conversation_id",
            message_id="test_message_id",
            user_id="test_user_uid",
        )
        self.assertEqual(test_object.sid, "test_message_id")
        self.assertEqual(test_object.user_uid, "test_user_uid")
        
        # Test serialization/deserialization
        dumped = test_object.model_dump()
        recreated = GetTtsRequest(**dumped)
        self.assertEqual(test_object, recreated)

    def test_get_tts_response(self):
        """Test GetTtsResponse model creation and validation"""
        from neon_data_models.models.api.klat.socketio import GetTtsResponse
        
        # Mock base64 audio data
        mock_audio = base64.b64encode(b"mock audio data").decode()
        
        # Test with required fields
        test_object = GetTtsResponse(
            audio_data=mock_audio,
            sid="test_shout_id",
            cid="test_conversation_id"
        )
        self.assertIsInstance(test_object, GetTtsResponse)
        self.assertEqual(test_object.audio_data, mock_audio)
        self.assertEqual(test_object.sid, "test_shout_id")
        self.assertEqual(test_object.cid, "test_conversation_id")
        self.assertEqual(test_object.lang, "en-us")  # Default value
        self.assertEqual(test_object.gender, "undefined")  # Default value
        self.assertEqual(test_object.context, {})  # Default value
        
        # Test with context extraction
        context = {"sid": "context_sid", "cid": "context_cid"}
        test_object = GetTtsResponse(
            audio_data=mock_audio,
            context=context
        )
        self.assertEqual(test_object.sid, "context_sid")
        self.assertEqual(test_object.cid, "context_cid")
        
        # Test to_db_query method
        db_query = test_object.to_db_query()
        self.assertEqual(db_query["shout_id"], test_object.sid)
        self.assertEqual(db_query["audio_data"], test_object.audio_data)
        self.assertEqual(db_query["lang"], test_object.lang)
        self.assertEqual(db_query["gender"], test_object.gender)
        
        # Test to_incoming_tts method
        incoming_tts = test_object.to_incoming_tts()
        self.assertEqual(incoming_tts["cid"], test_object.cid)
        self.assertEqual(incoming_tts["sid"], test_object.sid)
        self.assertEqual(incoming_tts["audio_data"], test_object.audio_data)
        self.assertEqual(incoming_tts["lang"], test_object.lang)
        self.assertEqual(incoming_tts["gender"], test_object.gender)

        # Test serialization/deserialization
        dumped = test_object.model_dump()
        recreated = GetTtsResponse(**dumped)
        self.assertEqual(test_object, recreated)

    def test_new_prompt_message(self):
        """Test NewPromptMessage model creation and validation"""
        from neon_data_models.models.api.klat.socketio import NewPromptMessage
        
        # Test with required fields
        test_object = NewPromptMessage(
            cid="test_conversation_id",
            user_id="test_user-suffix",
            user_uid="test_user_uuid",
            prompt_id="test_prompt_id",
            message_text="Hello world"
        )
        self.assertIsInstance(test_object, NewPromptMessage)
        self.assertEqual(test_object.cid, "test_conversation_id")
        self.assertEqual(test_object.user_id, "test_user-suffix")
        self.assertEqual(test_object.user_uid, "test_user_uuid")
        self.assertEqual(test_object.prompt_id, "test_prompt_id")
        self.assertEqual(test_object.message_text, "Hello world")
        self.assertEqual(test_object.prompt_state, CcaiState.IDLE)  # Default value
        self.assertEqual(test_object.context, {})  # Default value
        
        # Test with alias parameters
        test_object = NewPromptMessage(
            cid="test_conversation_id",
            userID="test_user-suffix",
            user_uid="test_user_uuid",
            promptID="test_prompt_id",
            messageText="Hello world",
            promptState=CcaiState.RESP
        )
        self.assertEqual(test_object.user_id, "test_user-suffix")
        self.assertEqual(test_object.prompt_id, "test_prompt_id")
        self.assertEqual(test_object.message_text, "Hello world")
        self.assertEqual(test_object.prompt_state, CcaiState.RESP)
        
        # Test model_dump with aliases
        dumped = test_object.model_dump()
        self.assertIn("user_id", dumped)
        self.assertIn("userID", dumped)  # Should include alias
        self.assertEqual(dumped["user_id"], dumped["userID"])
        self.assertIn("prompt_id", dumped)
        self.assertIn("promptID", dumped)  # Should include alias
        self.assertEqual(dumped["prompt_id"], dumped["promptID"])

        # Test serialization/deserialization
        recreated = NewPromptMessage(**dumped)
        self.assertEqual(test_object, recreated)
        
    def test_user_message(self):
        """Test UserMessage model creation and validation"""
        from neon_data_models.models.api.klat.socketio import UserMessage
        
        # Test with required fields
        current_time = datetime.now()
        test_object = UserMessage(
            sid="test_shout_id",
            cid="test_conversation_id",
            message_body="Hello world",
            time_created=current_time,
            user_id="guest-sid",
        )
        self.assertIsInstance(test_object, UserMessage)
        self.assertEqual(test_object.sid, "test_shout_id")
        self.assertEqual(test_object.cid, "test_conversation_id")
        self.assertEqual(test_object.message_body, "Hello world")
        self.assertEqual(test_object.time_created, current_time)
        self.assertEqual(test_object.user_id, "guest-sid")
        self.assertEqual(test_object.username, "guest")  # Parsed from user_id
        self.assertEqual(test_object.source, "unknown")  # Default value
        self.assertEqual(test_object.is_bot, "0")  # Default value
        self.assertEqual(test_object.lang, "en")  # Default value
        
        # Test with alias parameters and username derivation
        test_object = UserMessage(
            sid="test_shout_id",
            cid="test_conversation_id",
            userID="test_user-suffix",
            messageText="Hello world",
            time_created=current_time
        )
        self.assertEqual(test_object.user_id, "test_user-suffix")
        self.assertEqual(test_object.message_body, "Hello world")
        # Username should be derived from user_id
        self.assertEqual(test_object.username, "test_user")
        
        # Test with validation
        try:
            UserMessage(
                sid="test_shout_id",
                cid="test_conversation_id",
                user_id="same_name",
                userDisplayName="same_name",  # Should raise error when same as user_id
                message_body="Hello world",
                time_created=current_time
            )
            self.fail("Should have raised ValueError")
        except ValueError as e:
            self.assertIn("user_id should be a nick + suffix", str(e))
        
        # Test isAnnouncement and isAudio aliases
        test_object = UserMessage(
            sid="test_shout_id",
            cid="test_conversation_id",
            message_body="Hello world",
            time_created=current_time,
            isAnnouncement=1,
            isAudio=1,
            username="test_user"
        )
        self.assertTrue(test_object.is_announcement)
        self.assertTrue(test_object.is_audio)
        self.assertEqual(test_object.username, "test_user")
        self.assertIsNone(test_object.user_id)  # Derived from username
        
        # Test to_db_query method
        db_query = test_object.to_db_query()
        self.assertEqual(db_query["_id"], test_object.sid)
        self.assertEqual(db_query["cid"], test_object.cid)
        self.assertEqual(db_query["message_text"], test_object.message_body)
        self.assertEqual(db_query["is_audio"], test_object.is_audio)
        self.assertEqual(db_query["is_announcement"], test_object.is_announcement)
        self.assertEqual(db_query["created_on"], int(current_time.timestamp()))
        
        # Test to_new_prompt_message conversion
        test_object = UserMessage(
            sid="test_shout_id",
            cid="test_conversation_id",
            userID="test_user-suffix",
            user_uid="test_uuid",
            prompt_id="test_prompt_id",
            prompt_state=CcaiState.VOTE,
            message_body="Hello world",
            time_created=current_time,
        )
        prompt_message = test_object.to_new_prompt_message()
        self.assertEqual(prompt_message.cid, test_object.cid)
        self.assertEqual(prompt_message.user_id, test_object.user_id)
        self.assertEqual(prompt_message.user_uid, test_object.user_uid)
        self.assertEqual(prompt_message.prompt_id, test_object.prompt_id)
        self.assertEqual(prompt_message.prompt_state, test_object.prompt_state)
        self.assertEqual(prompt_message.message_text, test_object.message_body)

    def test_new_ccai_prompt(self):
        """Test NewCcaiPrompt model creation and validation"""
        from neon_data_models.models.api.klat.socketio import NewCcaiPrompt
        
        # Test with required fields
        test_object = NewCcaiPrompt(
            prompt_text="What is the meaning of life?",
            cid="test_conversation_id",
            prompt_id="test_prompt_id"
        )
        self.assertIsInstance(test_object, NewCcaiPrompt)
        self.assertEqual(test_object.prompt_text, "What is the meaning of life?")
        self.assertEqual(test_object.cid, "test_conversation_id")
        self.assertEqual(test_object.prompt_id, "test_prompt_id")
        self.assertIsNotNone(test_object.created_on)
        self.assertEqual(test_object.context, {})  # Default value
        self.assertIsNone(test_object.winner)  # Default value
        self.assertEqual(test_object.participating_subminds, [])  # Default value
        self.assertEqual(test_object.proposed_responses, {})  # Default value
        self.assertEqual(test_object.votes, {})  # Default value
        self.assertEqual(test_object.submind_discussion_history, [])  # Default value
        
        # Test with None context (should convert to empty dict)
        test_object = NewCcaiPrompt(
            prompt_text="What is the meaning of life?",
            cid="test_conversation_id",
            prompt_id="test_prompt_id",
            context=None
        )
        self.assertEqual(test_object.context, {})
        
        # Test submind_opinions conversion to submind_discussion_history
        submind_opinions = {"submind1": "opinion1", "submind2": "opinion2"}
        test_object = NewCcaiPrompt(
            prompt_text="What is the meaning of life?",
            cid="test_conversation_id",
            prompt_id="test_prompt_id",
            submind_opinions=submind_opinions
        )
        self.assertEqual(len(test_object.submind_discussion_history), 1)
        self.assertEqual(test_object.submind_discussion_history[0], submind_opinions)
        
        # Test to_db_query method
        db_query = test_object.to_db_query()
        self.assertEqual(db_query["_id"], test_object.prompt_id)
        self.assertEqual(db_query["cid"], test_object.cid)
        self.assertEqual(db_query["is_completed"], "0")
        self.assertEqual(db_query["data"]["prompt_text"], test_object.prompt_text)
        self.assertEqual(db_query["created_on"], test_object.created_on)
        self.assertEqual(db_query["context"], test_object.context)

    def test_ccai_prompt_completed(self):
        """Test CcaiPromptCompleted model creation and validation"""
        from neon_data_models.models.api.klat.socketio import CcaiPromptCompleted
        
        # Prepare a context with required fields
        current_time = datetime.now()
        context = {
            "winner": "The meaning of life is 42",
            "prompt": {"prompt_id": "test_prompt_id"}
        }
        
        # Test with required fields
        test_object = CcaiPromptCompleted(
            sid="test_shout_id",
            cid="test_conversation_id",
            message_body="The meaning of life is 42",
            time_created=current_time,
            prompt_id="test_prompt_id",
            user_id="proctor-sid",
            context=context
        )
        self.assertIsInstance(test_object, CcaiPromptCompleted)
        self.assertEqual(test_object.sid, "test_shout_id")
        self.assertEqual(test_object.cid, "test_conversation_id")
        self.assertEqual(test_object.message_body, "The meaning of life is 42")
        self.assertEqual(test_object.time_created, current_time)
        self.assertEqual(test_object.prompt_id, "test_prompt_id")
        self.assertEqual(test_object.winner, "The meaning of life is 42")
        self.assertEqual(test_object.user_id, "proctor-sid")
        self.assertEqual(test_object.username, "proctor")  # Parsed from user_id
        
        # Test with username validation
        with self.assertRaises(ValidationError):
            test_object = CcaiPromptCompleted(
                sid="test_shout_id",
                cid="test_conversation_id",
                user_id="same_name",
                username="same_name",
                message_body="Hello world",
                time_created=current_time,
                prompt_id="test_prompt_id"
            )
        
        # Test missing prompt_id handling
        with self.assertRaises(ValidationError):
            CcaiPromptCompleted(
                sid="test_shout_id",
                cid="test_conversation_id",
                message_body="Hello world",
                time_created=current_time,
                prompt_id=""  # Empty string should raise assertion
            )
        
        # Test to_db_query method
        db_query = test_object.to_db_query()
        self.assertEqual(db_query["prompt_id"], test_object.prompt_id)
        self.assertEqual(db_query["prompt_context"], test_object.context)
        
        # Test model_dump with aliases
        dumped = test_object.model_dump()
        self.assertIn("prompt_id", dumped)
        self.assertIn("promptID", dumped)  # Should include alias
        self.assertEqual(dumped["prompt_id"], dumped["promptID"])

    def test_get_prompt_data(self):
        """Test GetPromptData model creation and validation"""
        from neon_data_models.models.api.klat.socketio import GetPromptData
        
        # Test with required fields
        test_object = GetPromptData(
            nick="test_user",
            cid="test_conversation_id",
            prompt_id="test_prompt_id"
        )
        self.assertIsInstance(test_object, GetPromptData)
        self.assertEqual(test_object.nick, "test_user")
        self.assertEqual(test_object.cid, "test_conversation_id")
        self.assertEqual(test_object.prompt_id, "test_prompt_id")
        self.assertEqual(test_object.limit, 5)  # Default value
        
        # Test with custom limit
        test_object = GetPromptData(
            nick="test_user",
            cid="test_conversation_id",
            prompt_id="test_prompt_id",
            limit=10
        )
        self.assertEqual(test_object.limit, 10)
        
        # Test to_db_query method
        db_query = test_object.to_db_query()
        self.assertEqual(db_query["cid"], test_object.cid)
        self.assertEqual(db_query["limit"], test_object.limit)
        self.assertEqual(db_query["prompt_ids"], [test_object.prompt_id])
        self.assertTrue(db_query["fetch_user_data"])
        
        # Test with missing prompt_id
        test_object = GetPromptData(
            nick="test_user",
            cid="test_conversation_id"
        )
        self.assertIsNone(test_object.prompt_id)
        # to_db_query should raise assertion error when prompt_id is None
        with self.assertRaises(AssertionError):
            test_object.to_db_query()

    def test_prompt_data(self):
        """Test PromptData model creation and validation"""
        from neon_data_models.models.api.klat.socketio import PromptData
        
        # Test _PromptData nested class
        test_inner_object = PromptData._PromptData(
            _id="test_id",
            is_completed='1'  # String value should be converted to boolean
        )
        self.assertIsInstance(test_inner_object, PromptData._PromptData)
        self.assertEqual(test_inner_object.id, "test_id")
        self.assertTrue(test_inner_object.is_completed)
        self.assertEqual(test_inner_object.proposed_responses, {})  # Default value
        self.assertEqual(test_inner_object.submind_opinions, {})  # Default value
        self.assertEqual(test_inner_object.votes, {})  # Default value
        self.assertEqual(test_inner_object.participating_subminds, [])  # Default value
        
        # Test serialization of _PromptData
        serialized = test_inner_object.model_dump()
        self.assertEqual(serialized["_id"], "test_id")
        self.assertTrue(serialized["is_completed"])
        
        # Test with custom serializer to match MongoDB schema
        serialized = test_inner_object.alias_serialize()
        self.assertEqual(serialized["_id"], "test_id")
        self.assertEqual(serialized["is_completed"], "1")  # Should be string "1"
        
        # Test full PromptData with single _PromptData object
        valid_prompt_data = PromptData(
            data=test_inner_object,
            receiver="test_user",
            cid="test_conversation_id"
        )
        self.assertIsInstance(valid_prompt_data, PromptData)
        self.assertEqual(valid_prompt_data.data, test_inner_object)
        self.assertEqual(valid_prompt_data.receiver, "test_user")
        self.assertEqual(valid_prompt_data.cid, "test_conversation_id")
        self.assertIsNotNone(valid_prompt_data.request_id)  # Should have auto-generated UUID
        
        # Test full PromptData with list of _PromptData objects
        test_inner_object2 = PromptData._PromptData(
            _id="test_id2",
            is_completed='0'
        )
        valid_prompt_data = PromptData(
            data=[test_inner_object, test_inner_object2],
            receiver="test_user",
            cid="test_conversation_id"
        )
        self.assertIsInstance(valid_prompt_data.data, list)
        self.assertEqual(len(valid_prompt_data.data), 2)
        self.assertEqual(valid_prompt_data.data[0], test_inner_object)
        self.assertEqual(valid_prompt_data.data[1], test_inner_object2)
        
        # Test serialization/deserialization
        dumped = valid_prompt_data.model_dump()
        recreated = PromptData(**dumped)
        self.assertEqual(valid_prompt_data.receiver, recreated.receiver)
        self.assertEqual(valid_prompt_data.cid, recreated.cid)
        self.assertEqual(valid_prompt_data.request_id, recreated.request_id)
