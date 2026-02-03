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

from unittest import TestCase
from datetime import datetime, timezone
from pydantic import ValidationError


class TestChatbots(TestCase):
    def test_connected_submind(self):
        from neon_data_models.models.api.chatbots import ConnectedSubmind
        
        # Test minimal creation
        minimal_submind = ConnectedSubmind(service_name="test_service")
        self.assertEqual(minimal_submind.service_name, "test_service")
        self.assertEqual(minimal_submind.attached_cids, [])
        self.assertIsNone(minimal_submind.version)
        self.assertFalse(minimal_submind.supports_raw_conversation)
        self.assertIsInstance(minimal_submind.last_ping, datetime)
        self.assertEqual(minimal_submind.bot_type, "submind")
        
        # Test full definition
        full_submind = ConnectedSubmind(
            service_name="full_service",
            attached_cids=["cid1", "cid2"],
            version="1.0.0",
            supports_raw_conversation=True
        )
        self.assertEqual(full_submind.service_name, "full_service")
        self.assertEqual(full_submind.attached_cids, ["cid1", "cid2"])
        self.assertEqual(full_submind.version, "1.0.0")
        self.assertTrue(full_submind.supports_raw_conversation)
        
        # Test alias
        cids_submind = ConnectedSubmind(
            service_name="cids_service",
            cids=["cid3"]
        )
        self.assertEqual(cids_submind.attached_cids, ["cid3"])
        
        # Test validation
        with self.assertRaises(ValidationError):
            ConnectedSubmind()  # Missing required field service_name
        
        # Test datetime factory
        import time
        submind1 = ConnectedSubmind(service_name="time_test")
        time.sleep(0.1)
        submind2 = ConnectedSubmind(service_name="time_test_2")
        self.assertLess(submind1.last_ping, submind2.last_ping)
