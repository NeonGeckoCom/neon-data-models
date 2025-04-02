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
from typing import List, Tuple, Optional, Literal
from pydantic import Field, model_validator, computed_field

from neon_data_models.models.base import BaseModel


_DEFAULT_MQ_TO_ROLE = {"user": "user", "llm": "assistant"}


class LLMPersonaIdentity(BaseModel):
    """
    Defines metadata for a unique persona.
    """
    name: str = Field(alias="persona_name", 
                      description="Unique name for this persona")
    user_id: Optional[str] = Field(
        None, description="`user_id` of the user who created this persona.")

    @computed_field
    @property
    def id(self) -> str:
        persona_id = self.name
        if self.user_id:
            persona_id += f"_{self.user_id}"
        return persona_id


class LLMPersona(LLMPersonaIdentity):
    """
    Complete persona definition that may be applied to LLM inference or
    committed to a database.
    """
    description: Optional[str] = Field(
        None, description="Human-readable description of this persona")
    system_prompt: str = Field(
        None, description="System prompt associated with this persona. "
                          "If None, `description` will be used.")
    enabled: bool = Field(
        True, description="Flag used to mark a defined persona as "
                          "available for use.")

    @model_validator(mode='after')
    def validate_request(self):
        if self.name == "vanilla":
            assert self.system_prompt in (None, "")
            self.system_prompt = None
            return self

        assert any((self.description, self.system_prompt))
        if self.system_prompt is None:
            self.system_prompt = self.description
        return self


class LLMRequest(BaseModel):
    query: str = Field(description="Incoming user prompt")
    # TODO: History may support more options in the future
    history: List[Tuple[Literal["user", "llm"], str]] = Field(
        description="Formatted chat history (excluding system prompt). Note "
                    "that the roles used here will differ from those used in "
                    "OpenAI-compatible requests.")
    persona: LLMPersona = Field(
        description="Requested persona to respond to this message")
    model: str = Field(description="Model to request")
    max_tokens: int = Field(
        default=512, ge=64, le=2048,
        description="Maximum number of tokens to include in the response")
    temperature: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Temperature of response. 0 guarantees reproducibility, "
                    "higher values increase variability. Must be `0.0` if "
                    "`beam_search` is True")
    repetition_penalty: float = Field(
        default=1.0, ge=1.0, le=2.0,
        description="Repetition penalty. Higher values limit repeated "
                    "information in responses")
    stream: bool = Field(
        default=None, description="Enable streaming responses. "
                                  "Mutually exclusive with `beam_search`.")
    best_of: int = Field(
        default=1, ge=1,
        description="Number of beams to use if `beam_search` is enabled.")
    beam_search: bool = Field(
        default=None, description="Enable beam search. "
                                  "Mutually exclusive with `stream`.")
    max_history: int = Field(
        default=2, description="Maximum number of user/assistant "
                               "message pairs to include in history context.")

    @model_validator(mode='before')
    @classmethod
    def validate_inputs(cls, values):
        # Neon modules previously defined `user` and `llm` keys, but Open AI
        # specifies `assistant` in place of `llm` and is the de-facto standard
        for idx, itm in enumerate(values.get('history', [])):
            if itm[0] == "assistant":
                values['history'][idx] = ("llm", itm[1])
        return values

    @model_validator(mode='after')
    def validate_request(self):
        # If beams are specified, make sure valid `stream` and `beam_search`
        # values are specified
        if self.best_of > 1:
            if self.stream is True:
                raise ValueError("Cannot stream with a `best_of` value "
                                 "greater than 1")
            if self.beam_search is False:
                raise ValueError("Cannot have a `best_of` value other than 1 "
                                 "if `beam_search` is False")
            self.stream = False
            self.beam_search = True
        # If streaming, beam_search must be False
        if self.stream is True:
            if self.beam_search is True:
                raise ValueError("Cannot enable both `stream` and "
                                 "`beam_search`")
            self.beam_search = False
        # If beam search is enabled, `best_of` must be >1
        if self.beam_search is True and self.best_of <= 1:
            raise ValueError(f"best_of must be greater than 1 when using "
                             f"beam search. Got {self.best_of}")
        # If beam search is enabled, streaming must be False
        if self.beam_search is True:
            if self.stream is True:
                raise ValueError("Cannot enable both `stream` and "
                                 "`beam_search`")
            self.stream = False
        if self.stream is None and self.beam_search is None:
            self.stream = True
            self.beam_search = False

        assert isinstance(self.stream, bool)
        assert isinstance(self.beam_search, bool)

        # If beam search is enabled, temperature must be set to 0.0
        if self.beam_search:
            assert self.temperature == 0.0
        return self

    @property
    def messages(self) -> List[dict]:
        """
        Get chat history as a list of dict messages
        """
        return [{"role": m[0], "content": m[1]} for m in self.history]

    def to_completion_kwargs(self, mq2role: dict = None) -> dict:
        """
        Get kwargs to pass to an OpenAI completion request.
        @param mq2role: dict mapping `llm` and `user` keys to `role` values to
            use in message history.
        """
        mq2role = mq2role or _DEFAULT_MQ_TO_ROLE
        history = self.messages[-2*self.max_history:]
        for msg in history:
            msg["role"] = mq2role.get(msg["role"]) or msg["role"]
        history.insert(0, {"role": "system",
                           "content": self.persona.system_prompt})
        return {"model": self.model,
                "messages": history,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "stream": self.stream,
                "extra_body": {"add_special_tokens": True,
                               "repetition_penalty": self.repetition_penalty,
                               "use_beam_search": self.beam_search,
                               "best_of": self.best_of}}


class LLMResponse(BaseModel):
    response: str = Field(description="LLM Response to the input query")
    history: List[Tuple[Literal["user", "llm"], str]] = Field(
        description="List of (role, content) tuples in chronological order "
                    "(`response` is in the last list element)")
    finish_reason: Literal["length", "stop"] = Field(
        "stop", description="Reason response generation ended.")

    @model_validator(mode='before')
    @classmethod
    def validate_inputs(cls, values):
        # Neon modules previously defined `user` and `llm` keys, but Open AI
        # specifies `assistant` in place of `llm` and is the de-facto standard
        for idx, itm in enumerate(values.get('history', [])):
            if itm[0] == "assistant":
                values['history'][idx] = ("llm", itm[1])
        return values


__all__ = [LLMPersonaIdentity.__name__, LLMPersona.__name__,
           LLMRequest.__name__, LLMResponse.__name__]
