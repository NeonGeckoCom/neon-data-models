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

import importlib
import os
from datetime import datetime, timedelta

from unittest import TestCase
from time import time
from pydantic import ValidationError

from neon_data_models.models.client import NodeData
from neon_data_models.models.user import NeonUserConfig


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
        test_duration = 0.00001234
        timing = TimingContext(transcribed=test_time,
                               text_parsers=test_duration)

        # Type casting
        self.assertIsInstance(timing.handle_utterance, datetime)
        self.assertAlmostEqual(timing.handle_utterance.timestamp(), test_time, 5)
        self.assertIsInstance(timing.transform_utterance, timedelta)
        self.assertAlmostEqual(timing.transform_utterance.total_seconds(), test_duration, 5)

        # Dump/Load
        serialized = timing.model_dump()
        self.assertEqual(serialized['handle_utterance'],
                         timing.handle_utterance)
        self.assertEqual(serialized['transform_utterance'],
                         timing.transform_utterance)
        self.assertEqual(timing, TimingContext(**serialized))

    def test_klat_context(self):
        from neon_data_models.models.base.contexts import KlatContext
        with self.assertRaises(ValidationError):
            KlatContext()

        minimal_ctx = KlatContext(cid="conversation", sid="shout")
        self.assertEqual(minimal_ctx, KlatContext(**minimal_ctx.model_dump()))

    def test_mq_context(self):
        from neon_data_models.models.base.contexts import MQContext
        with self.assertRaises(ValidationError):
            MQContext()

        minimal_ctx = MQContext(message_id="test_message_id_string")
        self.assertEqual(minimal_ctx, MQContext(**minimal_ctx.model_dump()))


class TestMessagebus(TestCase):
    def test_base_model(self):
        from neon_data_models.models.base.messagebus import BaseMessage

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
        self.assertIsInstance(message.context.user_profiles[0], NeonUserConfig)

        serialized = message.model_dump()
        # Extra context keys are always retained for compat.
        self.assertEqual(serialized["context"]["extra_key"], "text")
        # Extra keys within a defined object are excluded
        self.assertIsNone(serialized["context"]["node_data"].get("extra"))
        self.assertEqual(message, BaseMessage(**serialized))

    def test_message_context(self):
        from neon_data_models.models.base.messagebus import MessageContext

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
        self.assertIsInstance(extra_context.user_profiles[0], NeonUserConfig)
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
