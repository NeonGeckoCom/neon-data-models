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

from unittest import TestCase
from pydantic import ValidationError


class TestLLM(TestCase):
    def test_llm_persona(self):
        from neon_data_models.models.api.llm import LLMPersona
        # Valid description
        legacy_mq_persona = LLMPersona(name="my persona",
                                       description="You are a helpful chatbot.")
        self.assertEqual(legacy_mq_persona.system_prompt,
                         legacy_mq_persona.description)

        # Valid system prompt
        legacy_bf_persona = LLMPersona(name="neon",
                                       system_prompt="You are NeonLLM.")
        self.assertIsNone(legacy_bf_persona.description)
        self.assertEqual(legacy_bf_persona.system_prompt,
                         "You are NeonLLM.")

        # Fully-defined persona
        full_persona = LLMPersona(name="custom chatbot",
                                  description="A customized bot for something",
                                  system_prompt="You are a custom chatbot.")
        self.assertEqual(full_persona.system_prompt,
                         "You are a custom chatbot.")
        self.assertEqual(full_persona.description,
                         "A customized bot for something")

        # Under-defined persona
        with self.assertRaises(ValidationError):
            LLMPersona(name="underdefined persona")

        # Valid vanilla persona
        vanilla = LLMPersona(name="vanilla")
        self.assertIsNone(vanilla.system_prompt)

        vanilla_2 = LLMPersona(name="vanilla", description="A vanilla chatbot")
        self.assertIsNone(vanilla_2.system_prompt)

        # Invalid vanilla persona
        with self.assertRaises(ValidationError):
            LLMPersona(name="vanilla", system_prompt="This should be empty")

    def test_llm_request(self):
        from neon_data_models.models.api.llm import LLMRequest, LLMPersona
        test_query = "how are you?"
        test_history = [("user", "hello"),
                        ("assistant", "Hi, how can I help you today?"),
                        ("user", "I am well, how about you?"),
                        ("assistant", "As a large language model, I do not feel")]
        test_persona = {"name": "Test Bot",
                        "system_prompt": "This is the system prompt."}
        test_model = "my_model_spec"
        # Minimal definition
        valid_request = LLMRequest(query=test_query, history=test_history,
                                   persona=test_persona, model=test_model)
        self.assertIsInstance(valid_request.persona, LLMPersona)
        self.assertTrue(valid_request.stream)
        self.assertFalse(valid_request.beam_search)
        self.assertEqual(len(valid_request.history), len(test_history))
        self.assertEqual(len(valid_request.to_completion_kwargs()['messages']),
                         2 * valid_request.max_history + 1)

        # Valid explicit streaming
        streaming_request = LLMRequest(query=test_query, history=test_history,
                                       persona=test_persona, model=test_model,
                                       stream=True)
        self.assertEqual(streaming_request, valid_request)

        # Valid explicit beam search
        beam_search_request = LLMRequest(query=test_query, history=test_history,
                                         persona=test_persona, model=test_model,
                                         beam_search=True, best_of=2)
        self.assertTrue(beam_search_request.beam_search)
        self.assertFalse(beam_search_request.stream)

        # Valid best_of, implied beam search
        best_of_request = LLMRequest(query=test_query, history=test_history,
                                     persona=test_persona, model=test_model,
                                     best_of=3)
        self.assertTrue(best_of_request.beam_search)
        self.assertFalse(best_of_request.stream)

        # Valid explicitly disable streaming and beam search
        valid_no_stream = LLMRequest(query=test_query, history=test_history,
                                     persona=test_persona, model=test_model,
                                     stream=False, beam_search=False)
        self.assertFalse(valid_no_stream.beam_search)
        self.assertFalse(valid_no_stream.stream)

        # Validate `llm` history input
        old_history = [("user", "hello"),
                       ("llm", "Hi, how can I help you today?"),
                       ("user", "I am well, how about you?"),
                       ("llm", "As a large language model, I do not feel")]
        validated = LLMRequest(query=test_query, history=old_history,
                               persona=test_persona, model=test_model)
        self.assertEqual(validated.history, test_history)

        # Invalid streaming with beam search
        with self.assertRaises(ValidationError):
            LLMRequest(query=test_query, history=test_history,
                       persona=test_persona, model=test_model, stream=True,
                       beam_search=True)
        # Invalid streaming with best_of > 1
        with self.assertRaises(ValidationError):
            LLMRequest(query=test_query, history=test_history,
                       persona=test_persona, model=test_model, stream=True,
                       best_of=2)
        # Invalid temperature with beam search
        with self.assertRaises(ValidationError):
            LLMRequest(query=test_query, history=test_history,
                       persona=test_persona, model=test_model, stream=False,
                       temperature=0.8, best_of=2)
        # Invalid beam search with best_of=1
        with self.assertRaises(ValidationError):
            LLMRequest(query=test_query, history=test_history,
                       persona=test_persona, model=test_model, stream=False,
                       beam_search=True, best_of=1)
        # Invalid history
        test_history.append(("invalid_key", "okay"))
        with self.assertRaises(ValidationError):
            LLMRequest(query=test_query, history=test_history,
                       persona=test_persona, model=test_model)
        test_history.pop()

    def test_llm_response(self):
        from neon_data_models.models.api.llm import LLMResponse
        valid_response = "hello"
        valid_history = [("user", "hello"), ("assistant", "How can I help?")]
        legacy_history = [("user", "hello"), ("llm", "How can I help?")]

        # Valid response with valid history
        response = LLMResponse(response=valid_response, history=valid_history)
        self.assertEqual(response.response, valid_response)
        self.assertEqual(response.history, valid_history)

        # Valid response with legacy history
        response = LLMResponse(response=valid_response, history=legacy_history)
        self.assertEqual(response.response, valid_response)
        self.assertEqual(response.history, valid_history)

        # Invalid response
        with self.assertRaises(ValidationError):
            LLMResponse(response=None, history=valid_history)

        # Invalid history
        valid_history.append(("invalid", "response"))
        with self.assertRaises(ValidationError):
            LLMResponse(response=valid_response, history=valid_history)
