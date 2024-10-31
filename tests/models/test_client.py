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

from time import time
from unittest import TestCase
from pydantic import ValidationError
from datetime import date
from neon_data_models.models.user.database import NeonUserConfig, TokenConfig, User, MQRequest, PermissionsConfig


class TestNode(TestCase):
    def test_node_data(self):
        from neon_data_models.models.client.node import (NodeData, NodeSoftware,
                                                         NodeLocation,
                                                         NodeNetworking)
        # Default config
        node_config = NodeData()
        self.assertEqual(node_config, NodeData(**node_config.model_dump()))
        self.assertIsInstance(node_config.networking, NodeNetworking)
        self.assertIsInstance(node_config.software, NodeSoftware)
        self.assertIsInstance(node_config.location, NodeLocation)

        # With location compat. handling
        config_2 = NodeData(networking={"local_ip": "10.0.0.2"},
                            location={"lat": 42.0, "lon": -71.0})
        self.assertNotEqual(node_config.device_id, config_2.device_id)
        self.assertEqual(config_2.networking.local_ip, "10.0.0.2")

        self.assertIsInstance(config_2.location.latitude, float)
        self.assertIsInstance(config_2.location.longitude, float)
