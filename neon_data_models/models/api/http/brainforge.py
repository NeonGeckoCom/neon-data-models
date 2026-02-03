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

from typing import List, Optional, Dict, Literal, Any
from uuid import uuid4
from time import time
from pydantic import Field, model_validator

from neon_data_models.models.base import BaseModel
from neon_data_models.models.api.llm import (
    BrainForgeLLM,
    LLMPersona,
    LLMRequest,
    LLMResponse,
)


class LLMGetModelsHttpResponse(BaseModel):
    models: List[BrainForgeLLM]


class LLMGetPersonasHttpRequest(BaseModel):
    model_id: str = Field(
        description="Model ID (<name>@<version>) to get personas for"
    )


class LLMGetPersonasHttpResponse(BaseModel):
    personas: List[LLMPersona] = Field(
        description="List of personas associated with the requested model."
    )


class LLMGetInferenceHttpRequest(LLMRequest):
    llm_name: str = Field(description="Model name to request")
    llm_revision: str = Field(description="Model revision to request")
    model: Optional[str] = Field(
        default=None,
        description="Model ID (<name>@<version>) used for vLLM inference",
    )

    @model_validator(mode="after")
    def set_model_from_name_and_revision(self):
        if self.model is None:
            self.model = f"{self.llm_name}@{self.llm_revision}"
        return self


class OpenAiCompletionRequest(BaseModel):
    model: str = Field(description="Model ID (generally <name>@<version>)")
    messages: List[Dict[Literal["role", "content"], str]] = Field(
        description="List of messages to send to the model for completion, "
        "including `system` and other context messages."
    )
    max_tokens: Optional[int] = Field(
        default=512, description="Maximum number of tokens to generate"
    )
    temperature: Optional[float] = Field(
        default=0.0, description="Temperature of generation"
    )
    stream: Optional[bool] = Field(
        default=False, description="Not Implemented."
    )
    persona: Optional[LLMPersona] = Field(default=None)
    extra_body: Optional[Dict[str, Any]] = Field(default=None)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "model": "<name>@<version>",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant.",
                        },
                        {"role": "user", "content": "Who are you?"},
                    ],
                    "max_tokens": 512,
                    "temperature": 0.0,
                    "stream": False,
                    "extra_body": {
                        "use_beam_search": True,
                        "best_of": 3,
                    }
                }
            ]
        }
    }

    @model_validator(mode="after")
    def ensure_default_values(self):
        """Set default values for compat with BrainForge API."""
        self.max_tokens = self.max_tokens or 512
        self.temperature = self.temperature or 0.0
        if self.stream is None:
            self.stream = False
        if self.extra_body is None:
            self.extra_body = {}
        return self

    @model_validator(mode="after")
    def get_persona(self):
        """Determine a persona based on message history or default vanilla."""
        for message in self.messages:
            if message["role"] == "system":
                sys_message = self.messages.pop(self.messages.index(message))
                if sys_message["content"]:
                    self.persona = LLMPersona(
                        name="custom", system_prompt=sys_message["content"]
                    )
                    return self
                break
        self.persona = LLMPersona(name="vanilla", system_prompt=None)
        return self

    @model_validator(mode="after")
    def validate_messages(self):
        if len(self.messages) < 1:
            raise ValueError("At least one `user` message is required.")
        return self

    def to_llm_inference_http_request(self) -> LLMGetInferenceHttpRequest:
        """
        Convert this OpenAI completion request to LLMGetInferenceHttpRequest
        """
        model, revision = self.model.split("@", 1)
        query = self.messages.pop(-1)["content"]
        history = [(msg["role"], msg["content"]) for msg in self.messages]
        return LLMGetInferenceHttpRequest(
            llm_name=model,
            llm_revision=revision,
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            query=query,
            history=history,
            persona=self.persona,
            **self.extra_body
        )


class OpenAiCompletionResponse(BaseModel):
    id: str = Field(
        description="UID for this completion request",
        default_factory=lambda: uuid4().hex,
    )
    object: Literal["chat.completion"] = "chat.completion"
    created: float = Field(
        description="Timestamp of completion request",
        default_factory=lambda: time(),
    )
    model: str = Field(description="Model ID used for this completion")
    choices: List[
        Dict[Literal["message"], Dict[Literal["role", "content"], str]]
    ] = Field(description="List of responses from the model")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": uuid4().hex,
                    "object": "chat.completion",
                    "created": time(),
                    "model": "<name>@<version>",
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": "This is a sample response",
                            }
                        }
                    ],
                }
            ]
        }
    }

    @classmethod
    def from_llm_response(
        cls, llm_response: LLMResponse, llm_request: OpenAiCompletionRequest
    ) -> "OpenAiCompletionResponse":
        """Get an OpenAI response from a BrainForge LLMResponse."""
        choices = [
            {
                "message": {
                    "role": "assistant",
                    "content": llm_response.response,
                }
            }
        ]
        return cls(model=llm_request.model, choices=choices)


__all__ = [
    LLMGetModelsHttpResponse.__name__,
    LLMGetPersonasHttpRequest.__name__,
    LLMGetPersonasHttpResponse.__name__,
    LLMGetInferenceHttpRequest.__name__,
    OpenAiCompletionRequest.__name__,
    OpenAiCompletionResponse.__name__,
]
