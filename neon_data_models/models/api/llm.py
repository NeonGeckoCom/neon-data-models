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
from typing import Any, Dict, List, Tuple, Optional, Literal
from pydantic import Field, model_validator, computed_field

from neon_data_models.models.base import BaseModel
from neon_data_models.types import LlmMessageRole


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
    system_prompt: Optional[str] = Field(
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

        assert any(x is not None for x in (self.description, self.system_prompt))
        if self.system_prompt is None:
            self.system_prompt = self.description
        return self


class LLMRequest(BaseModel):
    query: str = Field(description="Incoming user prompt")
    history: List[Tuple[LlmMessageRole, str]] = Field(
        description="Formatted chat history (excluding system prompt). Note "
                    "that the roles used here will differ from those used in "
                    "OpenAI-compatible requests.")
    persona: LLMPersona = Field(
        description="Requested persona to respond to this message")
    model: str = Field(description="Model to request (<name>@<revision>)")
    max_tokens: int = Field(
        default=512, ge=64, le=2048,
        description="Maximum number of tokens to include in the response")
    temperature: float = Field(
        default=0.0, ge=0.0, le=1.0,
        description="Temperature of response. 0 guarantees reproducibility, "
                    "higher values increase variability. Must be `0.0` if "
                    "`beam_search` is True")
    stream: bool = Field(
        default=None, description="Enable streaming responses. "
                                  "Mutually exclusive with `beam_search`.")
    max_history: int = Field(
        default=2, description="Maximum number of user/assistant "
                               "message pairs to include in history context. "
                               "Excludes system prompt and incoming query.")
    extra_body: Dict[str, Any] = Field(
        description="Optional dict of additional request body parameters")

    @property
    def repetition_penalty(self) -> float:
        return self.extra_body['repetition_penalty']

    @property
    def beam_search(self) -> bool:
        return self.extra_body['use_beam_search']

    @beam_search.setter
    def beam_search(self, value: bool):
        self.extra_body["use_beam_search"] = value

    @property
    def thinking_token_budget(self) -> Optional[int]:
        return self.extra_body.get('thinking_token_budget')

    @thinking_token_budget.setter
    def thinking_token_budget(self, value: Optional[int]):
        if value is None:
            self.extra_body.pop("thinking_token_budget", None)
            self.extra_body.pop("skip_special_tokens", None)
            if "chat_template_kwargs" in self.extra_body:
                self.extra_body["chat_template_kwargs"].pop(
                    "add_thinking_start", None)
                self.extra_body["chat_template_kwargs"].pop(
                    "enable_thinking", None)
        elif isinstance(value, int):
            assert value >= 0, "thinking_token_budget must be positive"
            if value >= self.max_tokens:
                raise ValueError(
                    "thinking_token_budget must be smaller than max_tokens")
            # Reasoning parsers need the literal think tags in decoded text
            self.extra_body["skip_special_tokens"] = False
            template_kwargs = self.extra_body.setdefault(
                "chat_template_kwargs", {})
            self.extra_body["thinking_token_budget"] = value
            if value == 0:
                # Treat `0` as a request for no thinking at all
                template_kwargs["add_thinking_start"] = False
                template_kwargs["enable_thinking"] = False
            else:
                template_kwargs["add_thinking_start"] = True
                template_kwargs.pop("enable_thinking", None)

    @property
    def best_of(self) -> int:
        return self.extra_body['best_of']

    @model_validator(mode='before')
    @classmethod
    def validate_inputs(cls, values):
        # Neon modules previously defined `user` and `llm` keys, but Open AI
        # specifies `assistant` in place of `llm` and is the de-facto standard
        for idx, itm in enumerate(values.get('history', [])):
            if itm[0] == "assistant":
                values['history'][idx] = ("llm", itm[1])
        # OpenAI `extra_body` may be included in input; parse those inputs
        if values.get('use_beam_search') is not None:
            values['beam_search'] = values['use_beam_search']

        values.setdefault("extra_body", {})
        values['extra_body'].setdefault("add_special_tokens", True)
        if values.get('repetition_penalty') is not None:
            values['extra_body']['repetition_penalty'] = values['repetition_penalty']
        values['extra_body'].setdefault('repetition_penalty', 1.0)
        if values.get('beam_search') is not None:
            values['extra_body']['use_beam_search'] = values['beam_search']
        values['extra_body'].setdefault('use_beam_search', None)
        if values.get('best_of') is not None:
            values['extra_body']['best_of'] = values['best_of']
        values['extra_body'].setdefault('best_of', 1)
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
        if self.stream is None and self.beam_search in (None, False):
            self.stream = True
            self.beam_search = False
        elif self.stream is None:
            self.stream = False

        assert isinstance(self.stream, bool), f"Expected `stream` to be a bool, got {type(self.stream)}"
        assert isinstance(self.beam_search, bool), f"Expected `beam_search` to be a bool, got {type(self.beam_search)}"

        # If beam search is enabled, temperature must be set to 0.0
        if self.beam_search:
            assert self.temperature == 0.0, "Beam search requires temperature 0"

        requested_budget = self.extra_body.get("thinking_token_budget")
        add_thinking_start = self.extra_body.get(
            "chat_template_kwargs", {}).get("add_thinking_start")
        if requested_budget is not None and requested_budget < 0:
            raise ValueError("thinking_token_budget must be positive")
        if requested_budget:
            if requested_budget >= self.max_tokens:
                raise ValueError(
                    "thinking_token_budget must be smaller than max_tokens")
            if add_thinking_start is not True:
                raise ValueError("add_thinking_start must be True if "
                                 "thinking_token_budget is set")
            # Reasoning parsers need the literal think tags in decoded text
            if self.extra_body.get("skip_special_tokens") is True:
                raise ValueError("skip_special_tokens must be False if "
                                 "add_thinking_start is True")
            self.thinking_token_budget = requested_budget
        elif requested_budget == 0 or add_thinking_start is False:
            # Either parameter alone means no thinking is requested; set both
            # so the request cannot ask the model to open a think block that
            # it has no budget to complete
            self.thinking_token_budget = 0
        elif add_thinking_start is True:
            raise ValueError("thinking_token_budget must be set if "
                             "add_thinking_start is True")
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
        if self.persona.system_prompt is not None:
            history.insert(0, {"role": "system",
                               "content": self.persona.system_prompt})
        history.append({"role": "user", "content": self.query})
        extra_body = dict(self.extra_body)
        if extra_body.get("thinking_token_budget") == 0:
            # A zero budget requests no thinking, but an inference engine reads
            # it as a budget to spend; it opens a think block and closes it
            # after one generated token, leaving the model to complete its
            # interrupted reasoning as response content
            extra_body.pop("thinking_token_budget")
        return {"model": self.model,
                "messages": history,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "stream": self.stream,
                "extra_body": extra_body}


class LLMResponse(BaseModel):
    response: str = Field(description="LLM Response to the input query")
    reasoning: Optional[str] = Field(
        None, description="Thinking/reasoning trace returned by the LLM")
    history: List[Tuple[LlmMessageRole, str]] = Field(
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


class ToolUseConfig(BaseModel):
    native_support: bool = Field(
        default=False,
        description="True if the model has native tool use support",
    )
    citations: bool = Field(
        default=False,
        description="True if the model supports citation generation",
    )


class BrainForgeLLM(BaseModel):
    name: str = Field(description="LLM Name")
    version: str = Field(description="LLM Version")
    tool_use: ToolUseConfig = Field(description="Tool use support",
                                    default=ToolUseConfig())
    personas: List[LLMPersona] = Field(
        default=[], description="List of personas defined in this model")

    @property
    def vllm_spec(self):
        """
        Model identifier used by vllm (<name>@<version>)
        """
        return f"{self.name}@{self.version}"


__all__ = [LLMPersonaIdentity.__name__, LLMPersona.__name__,
           LLMRequest.__name__, LLMResponse.__name__,
           BrainForgeLLM.__name__]
