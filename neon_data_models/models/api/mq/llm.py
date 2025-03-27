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

from typing import Optional, Dict, List
from pydantic import Field

from neon_data_models.models.api.llm import LLMRequest, LLMPersona
from neon_data_models.models.base.contexts import MQContext


class LLMProposeRequest(MQContext, LLMRequest):
    model: Optional[str] = Field(
        default=None,
        description="MQ implementation defines `model` as optional because the "
                    "queue defines the requested model in most cases.")
    persona: Optional[LLMPersona] = Field(
        default=None,
        description="MQ implementation defines `persona` as an optional "
                    "parameter, with default behavior hard-coded into each "
                    "LLM module.")


class LLMProposeResponse(MQContext):
    response: str = Field(description="LLM response to the prompt")


class LLMDiscussRequest(LLMProposeRequest):
    options: Dict[str, str] = Field(
        description="Mapping of participant name to response to be discussed.")


class LLMDiscussResponse(MQContext):
    opinion: str = Field(description="LLM response to the available options.")


class LLMVoteRequest(LLMProposeRequest):
    responses: List[str] = Field(
        description="List of responses to choose from.")


class LLMVoteResponse(MQContext):
    sorted_answer_indexes: List[int] = Field(
        description="Indices of `responses` ordered high to low by preference.")


__all__ = [LLMProposeRequest.__name__, LLMProposeResponse.__name__,
           LLMDiscussRequest.__name__, LLMDiscussResponse.__name__,
           LLMVoteRequest.__name__, LLMVoteResponse.__name__]
