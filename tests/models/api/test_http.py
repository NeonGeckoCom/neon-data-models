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

