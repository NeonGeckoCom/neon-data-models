# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2025 Neongecko.com Inc.
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

from neon_data_models.models.api.llm import LLMPersona


class TestBrainForgeHttp(TestCase):
    def test_llm_get_inference_http_request(self):
        from neon_data_models.models.api.http.brainforge import (
            LLMGetInferenceHttpRequest,
        )

        # Valid request
        valid_request = LLMGetInferenceHttpRequest(
            llm_name="test_model",
            llm_revision="1.0",
            query="What is the weather like today?",
            persona=LLMPersona(name="vanilla"),
            history=[],
            max_tokens=64,
            temperature=0.7,
            top_p=0.9,
            stop_sequences=["\n"],
            personas=["default"],
        )
        self.assertEqual(valid_request.llm_name, "test_model")
        self.assertEqual(valid_request.llm_revision, "1.0")
        self.assertEqual(valid_request.model, "test_model@1.0")
        self.assertEqual(
            valid_request.query, "What is the weather like today?"
        )

        # Invalid request (missing required llm_name)
        with self.assertRaises(ValidationError):
            LLMGetInferenceHttpRequest(
                llm_revision="1.0", query="What is the weather like today?"
            )

    def test_openai_completion_request(self):
        from neon_data_models.models.api.http.brainforge import (
            OpenAiCompletionRequest,
        )

        # Valid no persona
        valid_request_vanilla_persona = OpenAiCompletionRequest(
            model="test_model@v1.0",
            messages=[
                {"role": "system", "content": ""},
                {"role": "user", "content": "Hello, how are you?"},
            ],
            max_tokens=None,
            temperature=None,
            stream=None,
        )
        self.assertEqual(
            valid_request_vanilla_persona.model, "test_model@v1.0"
        )
        self.assertIsInstance(valid_request_vanilla_persona.max_tokens, int)
        self.assertIsInstance(valid_request_vanilla_persona.temperature, float)
        self.assertIsInstance(valid_request_vanilla_persona.stream, bool)
        self.assertIsInstance(
            valid_request_vanilla_persona.persona, LLMPersona
        )
        self.assertEqual(valid_request_vanilla_persona.persona.name, "vanilla")
        self.assertEqual(len(valid_request_vanilla_persona.messages), 1)

        as_llm_request = (
            valid_request_vanilla_persona.to_llm_inference_http_request()
        )
        self.assertEqual(as_llm_request.history, [])
        self.assertEqual(as_llm_request.query, "Hello, how are you?")
        self.assertEqual(
            as_llm_request.model, valid_request_vanilla_persona.model
        )

        # Valid with system prompt
        valid_request_custom_persona = OpenAiCompletionRequest(
            model="test_model@v1.0",
            messages=[
                {"role": "system", "content": "Custom system prompt"},
                {"role": "user", "content": "Hello, how are you?"},
                {"role": "assistant", "content": "I'm fine, thank you!"},
                {"role": "user", "content": "who are you?"},
            ],
            max_tokens=2048,
            temperature=1.0,
            stream=False,
        )
        self.assertIsInstance(valid_request_custom_persona.persona, LLMPersona)
        self.assertEqual(valid_request_custom_persona.persona.name, "custom")
        self.assertEqual(
            valid_request_custom_persona.persona.system_prompt,
            "Custom system prompt",
        )
        self.assertEqual(len(valid_request_custom_persona.messages), 3)

        as_llm_request = (
            valid_request_custom_persona.to_llm_inference_http_request()
        )
        self.assertEqual(len(as_llm_request.history), 2)
        self.assertEqual(as_llm_request.query, "who are you?")
        self.assertEqual(
            as_llm_request.model, valid_request_custom_persona.model
        )

        # Valid without system prompt
        valid_request_no_system = OpenAiCompletionRequest(
            model="test_model@v1.0",
            messages=[
                {"role": "user", "content": "Hello, how are you?"},
                {"role": "assistant", "content": "I'm fine, thank you!"},
                {"role": "user", "content": "who are you?"},
            ],
            max_tokens=1024,
            temperature=0.0,
            stream=False,
            extra_body={"use_beam_search": True,
                        "best_of": 3},
        )
        self.assertIsInstance(valid_request_no_system.persona, LLMPersona)
        self.assertEqual(valid_request_no_system.persona.name, "vanilla")
        self.assertEqual(len(valid_request_no_system.messages), 3)

        as_llm_request = (
            valid_request_no_system.to_llm_inference_http_request()
        )
        self.assertEqual(len(as_llm_request.history), 2)
        self.assertEqual(as_llm_request.query, "who are you?")
        self.assertEqual(as_llm_request.model, valid_request_no_system.model)
        self.assertTrue(as_llm_request.beam_search)

        # Invalid no history
        with self.assertRaises(ValidationError):
            OpenAiCompletionRequest(
                model="test_model@v1.0",
                messages=[],
                max_tokens=1024,
                temperature=0.5,
                stream=False,
            )

    def test_openai_completion_response(self):
        from neon_data_models.models.api.http.brainforge import (
            OpenAiCompletionRequest,
            OpenAiCompletionResponse,
        )
        from neon_data_models.models.api.llm import LLMResponse

        # Valid response
        llm_response = LLMResponse(
            response="Hello", history=[("user", "hi"), ("llm", "Hello")]
        )
        oai_request = OpenAiCompletionRequest(
            model="model_name@revision",
            messages=[{"role": "user", "content": "hi"}],
        )

        response = OpenAiCompletionResponse.from_llm_response(
            llm_response=llm_response, llm_request=oai_request
        )
        self.assertIsInstance(response.id, str)
        self.assertEqual(response.object, "chat.completion")
        self.assertIsInstance(response.created, float)
        self.assertEqual(response.model, oai_request.model)
        self.assertEqual(response.choices[0]["message"]["role"], "assistant")
        self.assertEqual(
            response.choices[0]["message"]["content"], llm_response.response
        )


class TestNeonHttp(TestCase):
    def test_neon_skill_api_http_data(self):
        from neon_data_models.models.api.http.neon import NeonSkillApiHttpData

        # Valid data with all fields
        valid_data = NeonSkillApiHttpData(
            skill_id="skill-about.neongeckocom",
            api_method="skill_info_examples",
            help="API Method to build a list of examples",
            request_schema=None,
            response_schema=None,
            signature=None,
            msg_type="skill-about.neongeckocom.skill_info_examples",
        )
        self.assertEqual(valid_data.skill_id, "skill-about.neongeckocom")
        self.assertEqual(valid_data.api_method, "skill_info_examples")
        self.assertEqual(valid_data.help, "API Method to build a list of examples")
        self.assertEqual(
            valid_data.msg_type, "skill-about.neongeckocom.skill_info_examples"
        )

        # Valid data with schema
        valid_data_with_schema = NeonSkillApiHttpData(
            skill_id="skill-date_time.neongeckocom",
            api_method="get_current_time",
            help="Get the current timestamp in seconds since epoch.",
            request_schema={
                "properties": {
                    "location": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Location",
                    }
                },
                "title": "_CurrentTimeRequest",
                "type": "object",
            },
            response_schema={
                "properties": {
                    "current_timestamp": {
                        "title": "Current Timestamp",
                        "type": "number",
                    }
                },
                "required": ["current_timestamp"],
                "title": "_CurrentTimeResponse",
                "type": "object",
            },
            signature="(request: skill_date_time._CurrentTimeRequest) -> skill_date_time._CurrentTimeResponse",
            msg_type="skill-date_time.neongeckocom.get_current_time",
        )
        self.assertIsInstance(valid_data_with_schema.request_schema, dict)
        self.assertIsInstance(valid_data_with_schema.response_schema, dict)
        self.assertIsInstance(valid_data_with_schema.signature, str)

        # Invalid data (missing required fields)
        with self.assertRaises(ValidationError):
            NeonSkillApiHttpData(
                skill_id="test_skill",
                # Missing api_method
                help="Test help",
            )

    def test_neon_http_list_skill_api_response(self):
        from neon_data_models.models.api.http.neon import (
            NeonHttpListSkillApiResponse,
            NeonSkillApiHttpData,
        )

        # Valid response with multiple items
        valid_response = NeonHttpListSkillApiResponse(
            root=[
                NeonSkillApiHttpData(
                    skill_id="skill-about.neongeckocom",
                    api_method="skill_info_examples",
                    help="API Method to build a list of examples",
                    request_schema=None,
                    response_schema=None,
                    signature=None,
                    msg_type="skill-about.neongeckocom.skill_info_examples",
                ),
                NeonSkillApiHttpData(
                    skill_id="skill-date_time.neongeckocom",
                    api_method="get_current_time",
                    help="Get the current timestamp in seconds since epoch.",
                    request_schema={
                        "properties": {
                            "location": {
                                "anyOf": [{"type": "string"}, {"type": "null"}],
                                "default": None,
                                "title": "Location",
                            }
                        },
                        "title": "_CurrentTimeRequest",
                        "type": "object",
                    },
                    response_schema={
                        "properties": {
                            "current_timestamp": {
                                "title": "Current Timestamp",
                                "type": "number",
                            }
                        },
                        "required": ["current_timestamp"],
                        "title": "_CurrentTimeResponse",
                        "type": "object",
                    },
                    signature="(request: skill_date_time._CurrentTimeRequest) -> skill_date_time._CurrentTimeResponse",
                    msg_type="skill-date_time.neongeckocom.get_current_time",
                ),
            ]
        )
        self.assertEqual(len(valid_response.root), 2)
        self.assertIsInstance(valid_response.root[0], NeonSkillApiHttpData)
        self.assertEqual(
            valid_response.root[0].skill_id, "skill-about.neongeckocom"
        )
        self.assertEqual(
            valid_response.root[1].skill_id, "skill-date_time.neongeckocom"
        )

        # Valid empty response
        empty_response = NeonHttpListSkillApiResponse(root=[])
        self.assertEqual(len(empty_response.root), 0)

        # Test serialization/deserialization
        data = valid_response.model_dump()
        # For RootModel, the data is a list, so we create directly from the list
        reconstructed = NeonHttpListSkillApiResponse(root=data)
        self.assertEqual(len(reconstructed.root), 2)
        self.assertEqual(
            reconstructed.root[0].skill_id, "skill-about.neongeckocom"
        )
        with self.assertRaises(ValidationError):
            # Invalid, empty response
            NeonHttpListSkillApiResponse(root=None)

        with self.assertRaises(ValidationError):
            # Invalid type
            NeonHttpListSkillApiResponse(root={})

    def test_neon_http_skill_api_request(self):
        from neon_data_models.models.api.http.neon import NeonHttpSkillApiRequest

        # Valid request with no args/kwargs
        valid_request = NeonHttpSkillApiRequest(
            skill_id="skill-about.neongeckocom",
            api_method="skill_info_examples",
        )
        self.assertEqual(valid_request.skill_id, "skill-about.neongeckocom")
        self.assertEqual(valid_request.api_method, "skill_info_examples")
        self.assertEqual(valid_request.args, [])
        self.assertEqual(valid_request.kwargs, {})

        # Valid request with args and kwargs
        valid_request_with_data = NeonHttpSkillApiRequest(
            skill_id="skill-date_time.neongeckocom",
            api_method="get_current_time",
            args=["arg1", "arg2"],
            kwargs={"location": "Seattle", "timezone": "UTC"},
        )
        self.assertEqual(valid_request_with_data.args, ["arg1", "arg2"])
        self.assertEqual(
            valid_request_with_data.kwargs,
            {"location": "Seattle", "timezone": "UTC"},
        )

        # Invalid request (missing required fields)
        with self.assertRaises(ValidationError):
            NeonHttpSkillApiRequest(
                skill_id="test_skill",
                # Missing api_method
            )

        with self.assertRaises(ValidationError):
            NeonHttpSkillApiRequest(
                # Missing skill_id
                api_method="test_method",
            )

    def test_neon_http_skill_api_response(self):
        from neon_data_models.models.api.http.neon import NeonHttpSkillApiResponse

        # Valid response with result
        valid_response_with_result = NeonHttpSkillApiResponse(
            result="API Response matching advertised schema",
            error=None,
        )
        self.assertEqual(
            valid_response_with_result.result,
            "API Response matching advertised schema",
        )
        self.assertIsNone(valid_response_with_result.error)

        # Valid response with error
        valid_response_with_error = NeonHttpSkillApiResponse(
            result=None, error="API Method error message"
        )
        self.assertIsNone(valid_response_with_error.result)
        self.assertEqual(
            valid_response_with_error.error, "API Method error message"
        )

        # Valid response with complex result
        complex_result = {
            "timestamp": 1640995200.0,
            "timezone": "UTC",
            "formatted_time": "2022-01-01 00:00:00",
        }
        valid_response_complex = NeonHttpSkillApiResponse(
            result=complex_result, error=None
        )
        self.assertEqual(valid_response_complex.result, complex_result)
        self.assertIsNone(valid_response_complex.error)

        # Valid response with list result
        list_result = ["item1", "item2", "item3"]
        valid_response_list = NeonHttpSkillApiResponse(
            result=list_result, error=None
        )
        self.assertEqual(valid_response_list.result, list_result)

        # Valid response with both result and error (should be allowed)
        both_fields_response = NeonHttpSkillApiResponse(
            result="some result", error="some error"
        )
        self.assertEqual(both_fields_response.result, "some result")
        self.assertEqual(both_fields_response.error, "some error")

        # Test serialization/deserialization
        response_data = valid_response_complex.model_dump()
        reconstructed = NeonHttpSkillApiResponse(**response_data)
        self.assertEqual(reconstructed.result, complex_result)
        self.assertIsNone(reconstructed.error)