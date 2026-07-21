# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2026 Neongecko.com Inc.
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

import importlib
import os
import json

from datetime import datetime, timedelta, timezone
from unittest import TestCase
from time import time
from pydantic import ValidationError


class TestBaseModel(TestCase):
    def test_base_model(self):
        import neon_data_models.models.base

        # Default behavior
        os.environ.pop("NEON_DATA_MODELS_ALLOW_EXTRA", "")
        model = neon_data_models.models.base.BaseModel()
        self.assertEqual(model.model_config["extra"], "ignore")

        # Allow extra
        os.environ["NEON_DATA_MODELS_ALLOW_EXTRA"] = "true"
        importlib.reload(neon_data_models.models.base)
        allowed = neon_data_models.models.base.BaseModel()
        self.assertEqual(allowed.model_config["extra"], "allow")
        self.assertEqual(model.model_config["extra"], "ignore")

        # Ignore extra
        os.environ["NEON_DATA_MODELS_ALLOW_EXTRA"] = "false"
        importlib.reload(neon_data_models.models.base)
        ignored = neon_data_models.models.base.BaseModel()
        self.assertEqual(ignored.model_config["extra"], "ignore")
        self.assertEqual(model.model_config["extra"], "ignore")
        self.assertEqual(allowed.model_config["extra"], "allow")

        # Ensure modules are unloaded for future inheritance tests
        import sys
        for module in list(sys.modules.keys()):
            if module.startswith("neon_data_models"):
                del sys.modules[module]

    def test_base_model_inheritance(self):
        from neon_data_models.models.base import BaseModel
        from neon_data_models.models.user.database import PermissionsConfig
        config = PermissionsConfig()
        self.assertTrue(isinstance(config, BaseModel))
        self.assertIsInstance(config.model_config["extra"], str)


class TestContexts(TestCase):
    def test_session_context(self):
        from neon_data_models.models.base.contexts import SessionContext
        # Default session builds with no params
        default_session = SessionContext()
        self.assertIsNone(default_session.lang)
        self.assertIsNone(default_session.system_unit)
        self.assertIsNone(default_session.date_format)
        self.assertIsNone(default_session.time)

        # Dumped session removes `None` values
        dict_session = default_session.model_dump()
        self.assertNotIn("lang", dict_session)
        self.assertNotIn("system_unit", dict_session)
        self.assertNotIn("date_format", dict_session)
        self.assertNotIn("time", dict_session)

        # Load session from dump
        self.assertEqual(default_session, SessionContext(**dict_session))

        # Test input validation
        session_context = SessionContext(time=12, extra_key=True)
        self.assertEqual(session_context.time, 12)
        self.assertEqual(session_context.model_dump()['time'], 12)
        self.assertNotIn("extra_key", session_context.model_dump())

        with self.assertRaises(ValidationError):
            SessionContext(time="12")

    def test_timing_context(self):
        from neon_data_models.models.base.contexts import TimingContext
        
        default = TimingContext()
        self.assertIsNone(default.model_dump()['handle_utterance'])

        # Alias handling
        test_time = time()
        timing = TimingContext(transcribed=test_time,
                               text_parsers=0.0001)

        # Type casting
        self.assertIsInstance(timing.handle_utterance, datetime)
        self.assertAlmostEqual(timing.handle_utterance.timestamp(), 
                               test_time, 0)
        self.assertIsInstance(timing.transform_utterance, timedelta)
        self.assertAlmostEqual(timing.transform_utterance.total_seconds(),
                               0, 0)

        # Dump/Load
        serialized = timing.model_dump()
        self.assertEqual(serialized['handle_utterance'],
                         timing.handle_utterance.timestamp())
        self.assertEqual(serialized['transform_utterance'],
                         timing.transform_utterance.total_seconds())
        self.assertEqual(timing, TimingContext(**serialized))

        # Create a TimingContext with sample data
        now = datetime.now(tz=timezone.utc)
        one_second = timedelta(seconds=1)
        
        context = TimingContext(
            audio_begin=now,
            audio_end=now + one_second,
            get_stt=one_second,
            get_tts=timedelta(seconds=2)
        )
        
        # Test serialization
        serialized = context.model_dump()
        
        # Check that datetime fields are converted to timestamps
        self.assertIsInstance(serialized["audio_begin"], float)
        self.assertIsInstance(serialized["audio_end"], float)
        self.assertAlmostEqual(serialized["audio_begin"],
                                now.timestamp(), delta=0.01)
        self.assertAlmostEqual(serialized["audio_end"], 
                               (now + one_second).timestamp(), delta=0.01)
        
        # Check that timedelta fields are converted to seconds
        self.assertIsInstance(serialized["get_stt"], float)
        self.assertIsInstance(serialized["get_tts"], float)
        self.assertEqual(serialized["get_stt"], 1.0)
        self.assertEqual(serialized["get_tts"], 2.0)
        
        # Test JSON serialization
        json_str = json.dumps(serialized)
        self.assertTrue(json_str)  # Ensure it can be JSON serialized
        
        # Test deserialization
        deserialized_dict = json.loads(json_str)
        deserialized = TimingContext(**deserialized_dict)
        
        # Check that timestamps are converted back to datetime objects
        self.assertIsInstance(deserialized.audio_begin, datetime)
        self.assertIsInstance(deserialized.audio_end, datetime)
        self.assertAlmostEqual((deserialized.audio_begin - 
                                now).total_seconds(), 0, delta=0.01)
        self.assertAlmostEqual((deserialized.audio_end - 
                                (now + one_second)).total_seconds(), 0,
                                  delta=0.01)
        
        # Check that second values are converted back to timedelta objects
        self.assertIsInstance(deserialized.get_stt, timedelta)
        self.assertIsInstance(deserialized.get_tts, timedelta)
        self.assertEqual(deserialized.get_stt.total_seconds(), 1.0)
        self.assertEqual(deserialized.get_tts.total_seconds(), 2.0)

        
        # Test invalid type for datetime field (string)
        with self.assertRaises(ValidationError) as context:
            TimingContext(audio_begin="not a timestamp or datetime")
        self.assertIn("audio_begin", str(context.exception))
        
        # Test invalid type for datetime field (dict)
        with self.assertRaises(ValidationError) as context:
            TimingContext(client_sent={"invalid": "value"})
        self.assertIn("client_sent", str(context.exception))
        
        # Test invalid type for timedelta field
        with self.assertRaises(ValidationError) as context:
            TimingContext(get_stt="invalid")
        
        # Create a context with all fields populated
        now = datetime.now(tz=timezone.utc)
        delta = timedelta(seconds=0.5)
        
        timing = TimingContext(
            # Datetime fields
            audio_begin=now,
            audio_end=now + delta,
            client_sent=now + delta * 2,
            gradio_sent=now + delta * 3,
            handle_utterance=now + delta * 4,
            response_sent=now + delta * 5,
            speech_start=now + delta * 6,
            
            # Timedelta fields
            get_stt=delta,
            get_tts=delta * 2,
            iris_input_handling=delta * 3,
            mq_response_handler=delta * 4,
            mq_from_core=delta * 5,
            mq_from_client=delta * 6,
            mq_input_handler=delta * 7,
            client_to_core=delta * 8,
            client_from_core=delta * 9,
            save_transcript=delta * 10,
            transform_audio=delta * 11,
            transform_utterance=delta * 12,
            wait_in_queue=delta * 13
        )
        
        # Verify all fields are properly typed
        self.assertIsInstance(timing.audio_begin, datetime)
        self.assertIsInstance(timing.audio_end, datetime)
        self.assertIsInstance(timing.client_sent, datetime)
        self.assertIsInstance(timing.gradio_sent, datetime)
        self.assertIsInstance(timing.handle_utterance, datetime)
        self.assertIsInstance(timing.response_sent, datetime)
        self.assertIsInstance(timing.speech_start, datetime)
        
        self.assertIsInstance(timing.get_stt, timedelta)
        self.assertIsInstance(timing.get_tts, timedelta)
        self.assertIsInstance(timing.iris_input_handling, timedelta)
        self.assertIsInstance(timing.mq_response_handler, timedelta)
        self.assertIsInstance(timing.mq_from_core, timedelta)
        self.assertIsInstance(timing.mq_from_client, timedelta)
        self.assertIsInstance(timing.mq_input_handler, timedelta)
        self.assertIsInstance(timing.client_to_core, timedelta)
        self.assertIsInstance(timing.client_from_core, timedelta)
        self.assertIsInstance(timing.save_transcript, timedelta)
        self.assertIsInstance(timing.transform_audio, timedelta)
        self.assertIsInstance(timing.transform_utterance, timedelta)
        self.assertIsInstance(timing.wait_in_queue, timedelta)
        
        # Test serialization/deserialization with all fields
        serialized = timing.model_dump()
        deserialized = TimingContext(**serialized)
        self.assertEqual(timing, deserialized)


        # Zero timestamp
        zero_time = TimingContext(audio_begin=0)
        self.assertEqual(zero_time.audio_begin, 
                         datetime.fromtimestamp(0, tz=timezone.utc))
        
        # Negative timestamp (represents dates before 1970)
        neg_time = TimingContext(audio_begin=-86400)  # One day before epoch
        self.assertEqual(neg_time.audio_begin, 
                         datetime.fromtimestamp(-86400, tz=timezone.utc))
        
        # Very large timestamp
        future_time = TimingContext(audio_begin=2147483647)  # Year 2038
        self.assertEqual(future_time.audio_begin, 
                         datetime.fromtimestamp(2147483647, tz=timezone.utc))
        
        # Zero timedelta
        zero_delta = TimingContext(get_stt=0)
        self.assertEqual(zero_delta.get_stt, timedelta(0))
        
        # Negative timedelta
        neg_delta = TimingContext(get_stt=-1.5)
        self.assertEqual(neg_delta.get_stt, timedelta(seconds=-1.5))


        now = datetime.now(tz=timezone.utc)
        timestamp = now.timestamp()
        
        # Test with timestamp input
        timestamp_input = TimingContext(audio_begin=timestamp)
        self.assertIsInstance(timestamp_input.audio_begin, datetime)
        self.assertAlmostEqual(timestamp_input.audio_begin.timestamp(), 
                               timestamp, places=3)
        
        # Test with datetime input
        datetime_input = TimingContext(audio_begin=now)
        self.assertIsInstance(datetime_input.audio_begin, datetime)
        self.assertAlmostEqual(datetime_input.audio_begin.timestamp(), 
                               timestamp, places=3)
        
        # Compare both inputs
        self.assertAlmostEqual(timestamp_input.audio_begin.timestamp(),
                               datetime_input.audio_begin.timestamp(), 
                               places=3)
        
        # Test with timedelta object vs number of seconds
        delta = timedelta(seconds=1.5)
        delta_input = TimingContext(get_stt=delta)
        seconds_input = TimingContext(get_stt=1.5)
        
        self.assertEqual(delta_input.get_stt, delta)
        self.assertEqual(seconds_input.get_stt, delta)


        timestamp = datetime.now(tz=timezone.utc).timestamp()
        
        # Test transcribed alias for handle_utterance
        with_transcribed = TimingContext(transcribed=timestamp)
        self.assertIsInstance(with_transcribed.handle_utterance, datetime)
        self.assertAlmostEqual(with_transcribed.handle_utterance.timestamp(), 
                               timestamp, places=3)
        
        # Test text_parsers alias for transform_utterance
        with_text_parsers = TimingContext(text_parsers=1.5)
        self.assertIsInstance(with_text_parsers.transform_utterance, timedelta)
        self.assertEqual(with_text_parsers.transform_utterance, 
                         timedelta(seconds=1.5))
        
        # Test both aliases together
        with_both = TimingContext(transcribed=timestamp, text_parsers=2.5)
        self.assertIsInstance(with_both.handle_utterance, datetime)
        self.assertIsInstance(with_both.transform_utterance, timedelta)
        self.assertAlmostEqual(with_both.handle_utterance.timestamp(), 
                               timestamp, places=3)
        self.assertEqual(with_both.transform_utterance, 
                         timedelta(seconds=2.5))
        
        # Ensure serialized data doesn't contain the old field names
        serialized = with_both.model_dump()
        self.assertIn("handle_utterance", serialized)
        self.assertIn("transform_utterance", serialized)
        self.assertNotIn("transcribed", serialized)
        self.assertNotIn("text_parsers", serialized)

    def test_klat_context(self):
        from neon_data_models.models.base.contexts import KlatContext
        with self.assertRaises(ValidationError):
            KlatContext(sid=None)

        minimal_ctx = KlatContext(cid="conversation", sid="shout")
        self.assertEqual(minimal_ctx, KlatContext(**minimal_ctx.model_dump()))
        
        # Test messageID normalization to sid
        message_id_ctx = KlatContext(cid="conversation", messageID="message_id_value")
        self.assertEqual(message_id_ctx.sid, "message_id_value")
        self.assertEqual(message_id_ctx.cid, "conversation")
        
        # Test serialization with normalized field
        serialized = message_id_ctx.model_dump()
        self.assertEqual(serialized["sid"], "message_id_value")
        self.assertNotIn("messageID", serialized)
        
        # Test round-trip serialization
        deserialized = KlatContext(**serialized)
        self.assertEqual(deserialized.sid, "message_id_value")
        self.assertEqual(deserialized, message_id_ctx)
        
        # Test that sid takes precedence when both fields are provided
        both_fields_ctx = KlatContext(cid="conversation", sid="shout_id", messageID="message_id_value")
        self.assertEqual(both_fields_ctx.sid, "shout_id")

    def test_mq_context(self):
        from neon_data_models.models.base.contexts import MQContext
        default = MQContext()
        self.assertIsInstance(default.message_id, str)
        self.assertNotEqual(default.message_id, MQContext().message_id)

        minimal_ctx = MQContext(message_id="test_message_id_string")
        self.assertEqual(minimal_ctx, MQContext(**minimal_ctx.model_dump()))


class TestMessagebus(TestCase):
    def test_base_model(self):
        from ovos_bus_client.message import Message
        from neon_data_models.models.base.messagebus import BaseMessage
        from neon_data_models.models.client import NodeData
        from neon_data_models.models.user import UserProfile

        with self.assertRaises(ValidationError):
            BaseMessage()

        # Test minimal message
        message = BaseMessage(msg_type="test", data={}, context={})
        self.assertEqual(message.msg_type, "test")
        self.assertTrue(message.context.neon_should_respond)

        # Test defined context
        message = BaseMessage(msg_type="test",
                              data={}, context={"node_data": {"extra": True},
                                                "user_profiles": [{}],
                                                "extra_key": "text"})
        # Defined keys will generate objects
        self.assertIsInstance(message.context.node_data, NodeData)
        self.assertIsInstance(message.context.user_profiles[0], UserProfile)

        as_messagebus = message.as_messagebus_message()
        self.assertIsInstance(as_messagebus, Message)
        self.assertEqual(as_messagebus.msg_type, message.msg_type)
        self.assertEqual(as_messagebus.data, message.data)
        self.assertEqual(as_messagebus.context, message.context.model_dump())

        serialized = message.model_dump()
        # Extra context keys are always retained for compat.
        self.assertEqual(serialized["context"]["extra_key"], "text")
        # Extra keys within a defined object are excluded
        self.assertIsNone(serialized["context"]["node_data"].get("extra"))
        self.assertEqual(message, BaseMessage(**serialized))

    def test_message_context(self):
        from neon_data_models.models.base.messagebus import MessageContext
        from neon_data_models.models.client import NodeData
        from neon_data_models.models.user import UserProfile

        # Default Behavior
        default_context = MessageContext()
        self.assertIsInstance(default_context, MessageContext)

        # Include extra keys
        extra_context = MessageContext(session={},
                                       node_data={"extra": True},
                                       user_profiles=[{}],
                                       klat_data={"cid": "cid", "sid": "sid"},
                                       mq={"message_id": "test_mid"},
                                       extra_context=True)
        # Configured values should create context objects
        self.assertIsInstance(extra_context, MessageContext)
        from neon_data_models.models.base.contexts import SessionContext
        self.assertIsInstance(extra_context.session, SessionContext)
        self.assertIsInstance(extra_context.node_data, NodeData)
        self.assertIsInstance(extra_context.user_profiles[0], UserProfile)
        from neon_data_models.models.base.contexts import KlatContext
        self.assertIsInstance(extra_context.klat_data, KlatContext)
        from neon_data_models.models.base.contexts import MQContext
        self.assertIsInstance(extra_context.mq, MQContext)

        # Serialization retains top-level extra keys
        serialized = extra_context.model_dump()
        self.assertIsNone(serialized['node_data'].get('extra'))
        self.assertTrue(serialized['extra_context'])

        # Round-trip serialization results in the same object
        self.assertEqual(extra_context, MessageContext(**serialized))
    
        # Test destination validation
        # Test default initialization
        default_context = MessageContext()
        self.assertEqual(default_context.destination, ["skills"])
        
        # Test string input gets converted to list
        string_context = MessageContext(destination="test")
        self.assertEqual(string_context.destination, ["test"])
        
        # Test list input remains a list
        list_context = MessageContext(destination=["test1", "test2"])
        self.assertEqual(list_context.destination, ["test1", "test2"])
        
        # Test serialization/deserialization
        serialized = string_context.model_dump()
        self.assertEqual(serialized["destination"], ["test"])
        
        # Test round-trip
        deserialized = MessageContext(**serialized)
        self.assertEqual(deserialized.destination, ["test"])

        # Test session=None validation
        none_session_context = MessageContext(session=None)
        self.assertIsNotNone(none_session_context.session)
        self.assertIsInstance(none_session_context.session, SessionContext)
        
        # Test that the default is used when None is provided
        default_session = SessionContext()
        self.assertEqual(none_session_context.session.model_dump(), 
                         default_session.model_dump())
        
        # Test serialization with None session that gets defaulted
        serialized = none_session_context.model_dump(exclude_none=True)
        self.assertIn("session", serialized)
        self.assertEqual(serialized["session"], default_session.model_dump())
        
        # Test round-trip serialization
        deserialized = MessageContext(**serialized)
        self.assertEqual(deserialized.session.model_dump(), 
                         default_session.model_dump())
        
        # Test when None is passed in a nested dictionary
        nested_none_context = MessageContext(**{"session": None})
        self.assertIsNotNone(nested_none_context.session)
        self.assertIsInstance(nested_none_context.session, SessionContext)

    def test_node_context(self):
        from neon_data_models.enum import NodeNativeAction
        from neon_data_models.models.base.contexts import NodeContext
        from neon_data_models.models.base.messagebus import MessageContext

        # node_id is required
        with self.assertRaises(ValidationError):
            NodeContext()

        minimal = NodeContext(node_id="node-a1b2c3d4")
        self.assertEqual(minimal.node_name, "")
        self.assertIsNone(minimal.site_id)
        self.assertEqual(minimal.capabilities, {})

        populated = NodeContext(node_id="node-a1b2c3d4",
                                node_name="Kitchen Phone",
                                site_id="kitchen",
                                capabilities={"launch_camera_app": True})
        self.assertEqual(populated, NodeContext(**populated.model_dump()))

        # MessageContext carries an optional `node` context
        self.assertIsNone(MessageContext().node)
        ctx = MessageContext(node=populated.model_dump())
        self.assertIsInstance(ctx.node, NodeContext)
        self.assertTrue(
            ctx.node.capabilities[NodeNativeAction.LAUNCH_CAMERA_APP])
        self.assertEqual(ctx.model_dump()["node"]["capabilities"],
                         {"launch_camera_app": True})
