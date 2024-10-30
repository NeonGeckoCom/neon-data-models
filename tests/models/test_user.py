from time import time
from unittest import TestCase
from pydantic import ValidationError
from datetime import date
from neon_data_models.models.user.database import NeonUserConfig, TokenConfig, User, MQRequest, PermissionsConfig


class TestDatabaseValidation(TestCase):
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

    def test_user_model(self):
        user_kwargs = dict(username="test",
                           password_hash="test",
                           tokens=[{"username": "test",
                                    "client_id": "test_id",
                                    "permissions": {},
                                    "refresh_token": "",
                                    "expiration": round(time()),
                                    "refresh_expiration": round(time()),
                                    "token_name": "test_token",
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

    def test_mq_request_model(self):
        valid_model = MQRequest(operation="create", username="test_user")
        self.assertIsInstance(valid_model, MQRequest)
        with self.assertRaises(ValidationError):
            MQRequest(operation="get", username="test")
        with self.assertRaises(ValidationError):
            MQRequest(operation="delete", username="test_user", user="test_user")
