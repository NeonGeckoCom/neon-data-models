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

from typing import List, Optional
from pydantic import Field, model_validator

from neon_data_models.models.base import BaseModel
from neon_data_models.models.api.llm import BrainForgeLLM, LLMPersona, LLMRequest


class LLMGetModelsHttpResponse(BaseModel):
    models: List[BrainForgeLLM]


class LLMGetPersonasHttpRequest(BaseModel):
    model_id: str = Field(
        description="Model ID (<name>@<version>) to get personas for")


class LLMGetPersonasHttpResponse(BaseModel):
    personas: List[LLMPersona] = Field(
        description="List of personas associated with the requested model.")


class LLMGetInferenceHttpRequest(LLMRequest):
    llm_name: str = Field(description="Model name to request")
    llm_revision: str = Field(description="Model revision to request")
    model: Optional[str] = Field(
        default=None, 
        description="Model ID (<name>@<version>) used for vLLM inference")

    @model_validator(mode='after')
    def set_model_from_name_and_revision(self):
        if self.model is None:
            self.model = f"{self.llm_name}@{self.llm_revision}"
        return self

__all__ = [LLMGetModelsHttpResponse.__name__,
           LLMGetPersonasHttpRequest.__name__,
           LLMGetPersonasHttpResponse.__name__,
           LLMGetInferenceHttpRequest.__name__]
