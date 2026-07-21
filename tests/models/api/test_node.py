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
from datetime import datetime, timedelta
from unittest import TestCase
from pydantic import ValidationError

from neon_data_models.enum import AlertType
from neon_data_models.models.api.mq import UserDbRequest


class TestNodeV1(TestCase):
    def test_node_audio_input(self):
        from neon_data_models.models.api.node_v1 import NodeAudioInput
        valid_data = {"audio_data": "abc123", "lang": "en-us"}

        # Invalid msg_type
        with self.assertRaises(ValidationError):
            NodeAudioInput(msg_type="bad_message_type",
                           data=valid_data, context={})

        # Missing context
        with self.assertRaises(ValidationError):
            NodeAudioInput(data=valid_data)

        # Valid with or without `msg_type` explicitly passed
        self.assertEqual(NodeAudioInput(msg_type="neon.audio_input",
                                        data=valid_data, context={}),
                         NodeAudioInput(data=valid_data, context={}))

    def test_node_text_input(self):
        from neon_data_models.models.api.node_v1 import NodeTextInput
        valid_data = {"utterances": ["abc123"], "lang": "en-us"}

        # Invalid msg_type
        with self.assertRaises(ValidationError):
            NodeTextInput(msg_type="bad_message_type",
                           data=valid_data, context={})

        # Missing context
        with self.assertRaises(ValidationError):
            NodeTextInput(data=valid_data)

        # Valid with or without `msg_type` explicitly passed
        self.assertEqual(NodeTextInput(msg_type="recognizer_loop:utterance",
                                        data=valid_data, context={}),
                         NodeTextInput(data=valid_data, context={}))

    def test_node_get_stt(self):
        from neon_data_models.models.api.node_v1 import NodeGetStt
        valid_data = {"audio_data": "abc123", "lang": "en-us"}

        # Invalid msg_type
        with self.assertRaises(ValidationError):
            NodeGetStt(msg_type="bad_message_type",
                          data=valid_data, context={})

        # Missing context
        with self.assertRaises(ValidationError):
            NodeGetStt(data=valid_data)

        # Valid with or without `msg_type` explicitly passed
        self.assertEqual(NodeGetStt(msg_type="neon.get_stt",
                                       data=valid_data, context={}),
                         NodeGetStt(data=valid_data, context={}))

    def test_node_get_tts(self):
        from neon_data_models.models.api.node_v1 import NodeGetTts
        valid_data = {"text": "abc123", "lang": "en-us"}

        # Invalid msg_type
        with self.assertRaises(ValidationError):
            NodeGetTts(msg_type="bad_message_type",
                          data=valid_data, context={})

        # Missing context
        with self.assertRaises(ValidationError):
            NodeGetTts(data=valid_data)

        # Valid with or without `msg_type` explicitly passed
        self.assertEqual(NodeGetTts(msg_type="neon.get_tts",
                                       data=valid_data, context={}),
                         NodeGetTts(data=valid_data, context={}))

    def test_node_klat_response(self):
        from neon_data_models.models.api.node_v1 import NodeKlatResponse
        valid_data = {"en-us": {"sentence": "test",
                                "audio": {"male": None, "female": None}}}

        invalid_gender = {"en-us": {"sentence": "test",
                                    "audio": {"FAIL": None, "female": None}}}

        invalid_data = {"en-us": "audio_file"}

        # Invalid msg_type
        with self.assertRaises(ValidationError):
            NodeKlatResponse(msg_type="bad_message_type",
                             data=valid_data, context={})

        # Missing context
        with self.assertRaises(ValidationError):
            NodeKlatResponse(data=valid_data)

        # Invalid data
        with self.assertRaises(ValidationError):
            NodeKlatResponse(data=invalid_gender, context={})
        with self.assertRaises(ValidationError):
            NodeKlatResponse(data=invalid_data, context={})

        # Valid with or without `msg_type` explicitly passed
        self.assertEqual(NodeKlatResponse(msg_type="klat.response",
                                       data=valid_data, context={}),
                         NodeKlatResponse(data=valid_data, context={}))

    def test_node_audio_input_response(self):
        from neon_data_models.models.api.node_v1 import NodeAudioInputResponse
        valid_data = {"parser_data": {}, "transcripts": [""],
                      "skills_recv": True}

        # Invalid msg_type
        with self.assertRaises(ValidationError):
            NodeAudioInputResponse(msg_type="bad_message_type",
                          data=valid_data, context={})

        # Missing context
        with self.assertRaises(ValidationError):
            NodeAudioInputResponse(data=valid_data)

        # Valid with or without `msg_type` explicitly passed
        self.assertEqual(NodeAudioInputResponse(
            msg_type="neon.audio_input.response",
                                       data=valid_data, context={}),
                         NodeAudioInputResponse(data=valid_data, context={}))

    def test_node_get_stt_response(self):
        from neon_data_models.models.api.node_v1 import NodeGetSttResponse
        valid_data = {"parser_data": {}, "transcripts": [""],
                      "skills_recv": True}

        # Invalid msg_type
        with self.assertRaises(ValidationError):
            NodeGetSttResponse(msg_type="bad_message_type",
                          data=valid_data, context={})

        # Missing context
        with self.assertRaises(ValidationError):
            NodeGetSttResponse(data=valid_data)

        # Valid with or without `msg_type` explicitly passed
        self.assertEqual(NodeGetSttResponse(
            msg_type="neon.get_stt.response",
                                       data=valid_data, context={}),
                         NodeGetSttResponse(data=valid_data, context={}))

    def test_node_get_tts_response(self):
        from neon_data_models.models.api.node_v1 import NodeGetTtsResponse
        valid_data = {"en-us": {"sentence": "test",
                                "audio": {"male": None, "female": None}}}

        invalid_gender = {"en-us": {"sentence": "test",
                                    "audio": {"FAIL": None, "female": None}}}

        invalid_data = {"en-us": "audio_file"}

        # Invalid msg_type
        with self.assertRaises(ValidationError):
            NodeGetTtsResponse(msg_type="bad_message_type",
                             data=valid_data, context={})

        # Missing context
        with self.assertRaises(ValidationError):
            NodeGetTtsResponse(data=valid_data)

        # Invalid data
        with self.assertRaises(ValidationError):
            NodeGetTtsResponse(data=invalid_gender, context={})
        with self.assertRaises(ValidationError):
            NodeGetTtsResponse(data=invalid_data, context={})

        # Valid with or without `msg_type` explicitly passed
        self.assertEqual(NodeGetTtsResponse(msg_type="neon.get_tts.response",
                                       data=valid_data, context={}),
                         NodeGetTtsResponse(data=valid_data, context={}))

    def test_core_ww_detected(self):
        from neon_data_models.models.api.node_v1 import CoreWWDetected
        valid_data = {"wake_word": "hey_neon"}

        # Invalid msg_type
        with self.assertRaises(ValidationError):
            CoreWWDetected(msg_type="bad_message_type",
                          data=valid_data, context={})

        # Missing context
        with self.assertRaises(ValidationError):
            CoreWWDetected(data=valid_data)

        # Valid with or without `msg_type` explicitly passed
        self.assertEqual(CoreWWDetected(msg_type="neon.ww_detected",
                                       data=valid_data, context={}),
                         CoreWWDetected(data=valid_data, context={}))

    def test_core_intent_failure(self):
        from neon_data_models.models.api.node_v1 import CoreIntentFailure
        valid_data = {}

        # Invalid msg_type
        with self.assertRaises(ValidationError):
            CoreIntentFailure(msg_type="bad_message_type",
                          data=valid_data, context={})

        # Missing context
        with self.assertRaises(ValidationError):
            CoreIntentFailure(data=valid_data)

        # Valid with or without `msg_type` explicitly passed
        self.assertEqual(CoreIntentFailure(msg_type="complete_intent_failure",
                                       data=valid_data, context={}),
                         CoreIntentFailure(data=valid_data, context={}))

    def test_core_error_response(self):
        from neon_data_models.models.api.node_v1 import CoreErrorResponse
        valid_data = {"error": "test error", "data": {"testing": True}}

        # Invalid msg_type
        with self.assertRaises(ValidationError):
            CoreErrorResponse(msg_type="bad_message_type",
                          data=valid_data, context={})

        # Missing context
        with self.assertRaises(ValidationError):
            CoreErrorResponse(data=valid_data)

        # Valid with or without `msg_type` explicitly passed
        self.assertEqual(CoreErrorResponse(msg_type="klat.error",
                                       data=valid_data, context={}),
                         CoreErrorResponse(data=valid_data, context={}))

        # Valid with default data
        self.assertIsInstance(CoreErrorResponse(data={}, context={}),
                              CoreErrorResponse)

    def test_core_clear_data(self):
        from neon_data_models.models.api.node_v1 import CoreClearData
        from neon_data_models.enum import UserData
        valid_data = {"username": "test_user",
                      "data_to_remove": [UserData.ALL_DATA]}
        valid_data_int = {"username": "test_user",
                          "data_to_remove": [UserData.ALL_DATA.value]}

        # Invalid msg_type
        with self.assertRaises(ValidationError):
            CoreClearData(msg_type="bad_message_type",
                              data=valid_data, context={})

        # Missing context
        with self.assertRaises(ValidationError):
            CoreClearData(data=valid_data)

        # Valid with or without `msg_type` explicitly passed
        self.assertEqual(CoreClearData(msg_type="neon.clear_data",
                                           data=valid_data, context={}),
                         CoreClearData(data=valid_data, context={}))

        # Valid with int cast to enum
        self.assertEqual(CoreClearData(data=valid_data, context={}),
                         CoreClearData(data=valid_data_int, context={}))

    def test_core_alert_expired(self):
        from neon_data_models.models.api.node_v1 import CoreAlertExpired
        alert_expiration = datetime.utcnow() + timedelta(minutes=30)
        expiration_iso = alert_expiration.isoformat()

        frequency_delta = timedelta(days=1)
        frequency_seconds = frequency_delta.total_seconds()

        base_alert = {"alert_type": AlertType.ALARM,
                      "priority": 7,
                      "repeat_days": None,
                      "end_repeat": None,
                      "alert_name": "Test Alert",
                      "context": {}}
        datetime_alert = {**base_alert,
                          **{"next_expiration_time": alert_expiration,
                             "repeat_frequency": frequency_delta}}
        iso_alert = {**base_alert, **{"next_expiration_time": expiration_iso,
                                      "repeat_frequency": frequency_seconds}}

        # Invalid msg_type
        with self.assertRaises(ValidationError):
            CoreAlertExpired(msg_type="bad_message_type",
                              data=datetime_alert, context={})

        # Missing context
        with self.assertRaises(ValidationError):
            CoreAlertExpired(data=datetime_alert)

        # Valid with or without `msg_type` explicitly passed
        self.assertEqual(CoreAlertExpired(msg_type="neon.alert_expired",
                                           data=datetime_alert, context={}),
                         CoreAlertExpired(data=datetime_alert, context={}))

        # Validate cast from timestamp/epoch to datetime/timedelta
        self.assertEqual(CoreAlertExpired(data=datetime_alert, context={}),
                         CoreAlertExpired(data=iso_alert, context={}))

    def test_node_hello(self):
        from neon_data_models.models.api.node_v1 import NodeHello
        from neon_data_models.enum import NodeNativeAction
        valid_data = {"node_id": "node-a1b2c3d4",
                      "node_name": "Kitchen Phone",
                      "capabilities": {"launch_camera_app": True,
                                       "launch_sms_app": False}}

        # Invalid msg_type
        with self.assertRaises(ValidationError):
            NodeHello(msg_type="bad_message_type",
                      data=valid_data, context={})

        # Missing context
        with self.assertRaises(ValidationError):
            NodeHello(data=valid_data)

        # Missing node_id
        with self.assertRaises(ValidationError):
            NodeHello(data={"node_name": "Kitchen Phone"}, context={})

        # Valid with or without `msg_type` explicitly passed
        hello = NodeHello(data=valid_data, context={})
        self.assertEqual(NodeHello(msg_type="node.hello",
                                   data=valid_data, context={}), hello)

        # Capability keys validate to `NodeNativeAction` and serialize back
        # to wire strings
        self.assertTrue(
            hello.data.capabilities[NodeNativeAction.LAUNCH_CAMERA_APP])
        self.assertFalse(
            hello.data.capabilities[NodeNativeAction.LAUNCH_SMS_APP])
        self.assertEqual(hello.model_dump()["data"]["capabilities"],
                         {"launch_camera_app": True,
                          "launch_sms_app": False})

        # name and capabilities are optional
        minimal = NodeHello(data={"node_id": "node-a1b2c3d4"}, context={})
        self.assertEqual(minimal.data.node_name, "")
        self.assertEqual(minimal.data.capabilities, {})

        # Unknown capability keys are dropped, not rejected
        # (forward-compatibility with Nodes newer than this schema)
        extended = NodeHello(data={**valid_data,
                                   "capabilities": {"future_action": True,
                                                    "launch_sms_app": True}},
                             context={})
        self.assertEqual(extended.data.capabilities,
                         {NodeNativeAction.LAUNCH_SMS_APP: True})

    def test_node_invoke_native(self):
        from neon_data_models.models.api.node_v1 import NodeInvokeNative
        from neon_data_models.enum import NodeNativeAction

        # Launch-only action
        launch_only = NodeInvokeNative(data={"action": "launch_camera_app"},
                                       context={})
        self.assertEqual(launch_only.data.action,
                         NodeNativeAction.LAUNCH_CAMERA_APP)
        self.assertEqual(launch_only.data.params, {})

        # Action with pre-fill payload
        with_params = NodeInvokeNative(
            data={"action": "launch_email_app",
                  "params": {"subject": "Running late", "body": "Sorry!"}},
            context={})
        self.assertEqual(with_params.data.params["subject"], "Running late")

        # Unknown action is rejected
        with self.assertRaises(ValidationError):
            NodeInvokeNative(data={"action": "launch_unknown_app"},
                             context={})

        # Missing action is rejected
        with self.assertRaises(ValidationError):
            NodeInvokeNative(data={}, context={})

        # Action enum serializes to its wire string
        self.assertEqual(launch_only.model_dump()["data"]["action"],
                         "launch_camera_app")

    def test_node_invoke_native_response(self):
        from neon_data_models.models.api.node_v1 import NodeInvokeNativeResponse
        from neon_data_models.enum import NativeActionErrorCode

        # Success response
        success = NodeInvokeNativeResponse(
            data={"action": "launch_camera_app", "status": "success"},
            context={})
        self.assertIsNone(success.data.error)

        # Error response
        error = NodeInvokeNativeResponse(
            data={"action": "launch_camera_app", "status": "error",
                  "error": {"code": "unavailable",
                            "message": "No camera app is available."}},
            context={})
        self.assertEqual(error.data.error.code,
                         NativeActionErrorCode.UNAVAILABLE)

        # Error status without an error object is rejected
        with self.assertRaises(ValidationError):
            NodeInvokeNativeResponse(
                data={"action": "launch_camera_app", "status": "error"},
                context={})

        # Success status with an error object is rejected
        with self.assertRaises(ValidationError):
            NodeInvokeNativeResponse(
                data={"action": "launch_camera_app", "status": "success",
                      "error": {"code": "unavailable"}},
                context={})

        # Unknown error code is rejected
        with self.assertRaises(ValidationError):
            NodeInvokeNativeResponse(
                data={"action": "launch_camera_app", "status": "error",
                      "error": {"code": "not_an_error_code"}},
                context={})

        # Error code serializes to its wire string
        self.assertEqual(
            error.model_dump()["data"]["error"]["code"], "unavailable")

    def test_native_action_wire_strings(self):
        # These enum values are the wire contract shared with HANA, the
        # skills, and the Node app. Changing one is a breaking change.
        from neon_data_models.enum import (NodeNativeAction,
                                           NativeActionErrorCode)
        self.assertEqual({a.value for a in NodeNativeAction},
                         {"launch_camera_app", "launch_voice_recorder_app",
                          "launch_reminders_app", "launch_clock_app",
                          "launch_sms_app", "launch_email_app"})
        self.assertEqual({c.value for c in NativeActionErrorCode},
                         {"not_supported", "permission_denied",
                          "unavailable", "internal_error"})

    def test_native_action_models_round_trip(self):
        from neon_data_models.models.api.node_v1 import (
            NodeHello, NodeInvokeNative, NodeInvokeNativeResponse)
        from neon_data_models.enum import NodeNativeAction

        hello = NodeHello(
            data={"node_id": "node-a1b2c3d4", "node_name": "Kitchen Phone",
                  "capabilities": {a.value: True for a in NodeNativeAction}},
            context={})
        invoke = NodeInvokeNative(
            data={"action": "launch_sms_app",
                  "params": {"to": "+15551234567", "body": "On my way"}},
            context={})
        response = NodeInvokeNativeResponse(
            data={"action": "launch_sms_app", "status": "error",
                  "error": {"code": "not_supported"}},
            context={})

        # Serialization round-trips to an equal object for every model
        self.assertEqual(hello, NodeHello(**hello.model_dump()))
        self.assertEqual(invoke, NodeInvokeNative(**invoke.model_dump()))
        self.assertEqual(response,
                         NodeInvokeNativeResponse(**response.model_dump()))

    def test_native_action_models_as_messagebus_message(self):
        # HANA consumes these via `as_messagebus_message`; enum fields must
        # arrive on the bus as their wire strings, not Enum objects
        from neon_data_models.models.api.node_v1 import (
            NodeInvokeNative, NodeInvokeNativeResponse)

        invoke = NodeInvokeNative(data={"action": "launch_clock_app"},
                                  context={})
        bus_msg = invoke.as_messagebus_message()
        self.assertEqual(bus_msg.msg_type, "node.invoke_native")
        self.assertEqual(bus_msg.data["action"], "launch_clock_app")

        response = NodeInvokeNativeResponse(
            data={"action": "launch_clock_app", "status": "error",
                  "error": {"code": "internal_error", "message": "oops"}},
            context={})
        bus_msg = response.as_messagebus_message()
        self.assertEqual(bus_msg.msg_type, "node.invoke_native.response")
        self.assertEqual(bus_msg.data["error"]["code"], "internal_error")

    def test_native_action_version_skew_tolerance(self):
        # An older hub must tolerate payloads from a newer Node: unknown
        # fields and capability keys are dropped, unknown params are carried.
        # (Unknown `action`/`error.code` values are strictly rejected by
        # design — extending those enums is a coordinated release.)
        from neon_data_models.models.api.node_v1 import (NodeHello,
                                                         NodeInvokeNative)

        # Unknown fields added by a future spec revision are ignored
        hello = NodeHello(data={"node_id": "node-a1b2c3d4",
                                "protocol_version": 2},
                          context={})
        self.assertIsNone(hello.data.model_dump().get("protocol_version"))

        # Unknown params keys are retained so a relaying hub passes them
        # through to the Node untouched
        invoke = NodeInvokeNative(
            data={"action": "launch_email_app",
                  "params": {"subject": "hi", "importance": "high"}},
            context={})
        self.assertEqual(invoke.data.params["importance"], "high")
        self.assertEqual(
            invoke.model_dump()["data"]["params"]["importance"], "high")

    def test_node_hello_name_length_cap(self):
        from neon_data_models.models.api.node_v1 import NodeHello
        from neon_data_models.models.base.contexts import NodeContext

        NodeHello(data={"node_id": "n", "node_name": "x" * 128}, context={})
        with self.assertRaises(ValidationError):
            NodeHello(data={"node_id": "n", "node_name": "x" * 129},
                      context={})
        with self.assertRaises(ValidationError):
            NodeContext(node_id="n", node_name="x" * 129)
