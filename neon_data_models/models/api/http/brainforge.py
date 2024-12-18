from typing import List
from pydantic import Field

from neon_data_models.models.base import BaseModel
from neon_data_models.models.api.llm import BrainForgeLLM


class LLMGetModelsHttpResponse(BaseModel):
    models: List[BrainForgeLLM]
