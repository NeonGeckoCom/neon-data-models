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
from uuid import uuid4

from pydantic import ValidationError
from datetime import date
from neon_data_models.models.user.database import NeonUserConfig, TokenConfig, User


class TestDatabase(TestCase):
    def test_neon_user_config(self):
        default = NeonUserConfig()
        valid_with_extras = NeonUserConfig(
            user={"first_name": "Daniel",
                  "middle_name": "James",
                  "last_name": "McKnight",
                  "preferred_name": "tester",
                  "dob": "2001-01-01",
                  "email": "developers@neon.ai",
                  "extra_key": "This should be removed by validation"
                  },
            language={"input": ["en-us", "uk-ua"],
                      "output": ["en-us", "es-es"]},
            units={"time": 24, "date": "YMD", "measure": "metric"},
            location={"latitude": 47.6765382, "longitude": -122.2070775,
                      "name": "Kirkland, WA",
                      "timezone": "America/Los_Angeles"},
            extra_section={"test": True}
        )

        # Ensure invalid keys are removed and defaults are added
        self.assertEqual(default.model_dump().keys(),
                         valid_with_extras.model_dump().keys())
        for section in default.model_dump().keys():
            if section == "skills":
                # `skills` is not a model, the contents are arbitrary
                continue
            default_keys = getattr(default, section).model_dump().keys()
            extras_keys = getattr(valid_with_extras, section).model_dump().keys()
            self.assertEqual(default_keys, extras_keys)

        # Validation errors
        with self.assertRaises(ValidationError):
            NeonUserConfig(units={"time": 13})
        with self.assertRaises(ValidationError):
            NeonUserConfig(location={"latitude": "test"})
        with self.assertRaises(ValidationError):
            NeonUserConfig(user={"dob": "01/01/2001"})

        # Valid type casting
        config = NeonUserConfig(location={"latitude": "47.6765382",
                                          "longitude": "-122.2070775"})
        self.assertIsInstance(config.location.latitude, float)
        self.assertIsInstance(config.location.longitude, float)

        config = NeonUserConfig(user={"dob": "2001-01-01"})
        self.assertIsInstance(config.user.dob, date)

    def test_user(self):
        user_kwargs = dict(username="test",
                           password_hash="test",
                           tokens=[{"token_name": "test_token",
                                    "token_id": str(uuid4()),
                                    "user_id": str(uuid4()),
                                    "client_id": str(uuid4()),
                                    "permissions": {},
                                    "refresh_expiration_timestamp": round(time()),
                                    "creation_timestamp": round(time()),
                                    "last_refresh_timestamp": round(time())}])
        default_user = User(**user_kwargs)
        self.assertIsInstance(default_user.tokens[0], TokenConfig)
        with self.assertRaises(ValidationError):
            User()

        with self.assertRaises(ValidationError):
            User(username="test", password_hash="test",
                 tokens=[{"description": "test"}])

        duplicate_user = User(**user_kwargs)
        self.assertNotEqual(default_user, duplicate_user)
        self.assertEqual(default_user.tokens, duplicate_user.tokens)

    def test_permissions_config(self):
        from neon_data_models.models.user.database import PermissionsConfig
        from neon_data_models.enum import AccessRoles

        # Test Default
        default_config = PermissionsConfig()
        for _, value in default_config.model_dump().items():
            self.assertEqual(value, AccessRoles.NONE)

        test_config = PermissionsConfig(klat=AccessRoles.USER,
                                        core=AccessRoles.GUEST,
                                        diana=AccessRoles.GUEST,
                                        node=AccessRoles.NODE,
                                        hub=AccessRoles.NODE,
                                        llm=AccessRoles.NONE)
        # Test dump/load
        self.assertEqual(PermissionsConfig(**test_config.model_dump()),
                         test_config)

        # Test to/from roles
        roles = test_config.to_roles()
        self.assertIsInstance(roles, list)
        for role in roles:
            self.assertEqual(len(role.split()), 2)
        self.assertEqual(PermissionsConfig.from_roles(roles), test_config)

    def test_token_config(self):
        from neon_data_models.models.user.database import TokenConfig
        # TODO


class TestNeonProfile(TestCase):
    def test_create(self):
        from neon_data_models.models.user import UserProfile
        default = UserProfile()
        self.assertIsInstance(default, UserProfile)

        # TODO: Test creation with params

    def test_from_user_object(self):
        from neon_data_models.models.user import UserProfile

        neon_config = {"user": {"first_name": "Test",
                                "last_name": "User",
                                "dob": date.today().replace(year=2000)},
                       "language": {"input_languages": ["en-us", "uk-ua"],
                                    "output_languages": ["uk-ua", "en-us"]},
                       "units": {"measure": "metric"},
                       "location": {"latitude": 47.48288,
                                    "longitude": -122.217064,
                                    "timezone": "America/Los_Angeles"},
                       "response_mode": {"tts_gender": "male",
                                         "tts_speed_multiplier": 0.9}
                       }
        age = date.today().year - 2000
        user_from_db = User(username="test_user",
                            password_hash="test_password",
                            neon=neon_config)

        user_profile = UserProfile.from_user_object(user_from_db)

        # User
        self.assertEqual(user_profile.user.username, "test_user")
        self.assertEqual(user_profile.user.password, "test_password")
        self.assertEqual(user_profile.user.first_name, "Test")
        self.assertEqual(user_profile.user.last_name, "User")
        self.assertEqual(user_profile.user.full_name, "Test User")
        self.assertEqual(user_profile.user.age, f"{age}")
        self.assertEqual(user_profile.user.dob,
                         date.today().replace(year=2000).strftime("%Y/%m/%d"))

        # Speech
        self.assertEqual(user_profile.speech.stt_language, "en")
        self.assertEqual(user_profile.speech.alt_languages, ["uk"])
        self.assertEqual(user_profile.speech.tts_language, "uk-ua")
        self.assertEqual(user_profile.speech.secondary_tts_language, "en-us")
        self.assertEqual(user_profile.speech.tts_gender, "male")
        self.assertEqual(user_profile.speech.secondary_tts_gender, "male")
        self.assertEqual(user_profile.speech.speed_multiplier, 0.9)

        # Units
        self.assertEqual(user_profile.units.measure, "metric")

        # Location
        self.assertIsInstance(user_profile.location.lat, float)
        self.assertIsInstance(user_profile.location.lng, float)
        self.assertEqual(user_profile.location.tz, "America/Los_Angeles")
        self.assertIn(user_profile.location.utc, (-7.0, -8.0))
