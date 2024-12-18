from typing import List, Optional
from pydantic import Field

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
    model: Optional[str] = None
