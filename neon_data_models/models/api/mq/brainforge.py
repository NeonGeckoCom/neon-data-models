from typing import List, Optional

from pydantic import Field

from neon_data_models.models.base.contexts import MQContext
from neon_data_models.models.api.llm import BrainForgeLLM, LLMRequest, LLMResponse, LLMPersona
from neon_data_models.models.api.http.brainforge import LLMGetModelsHttpResponse, LLMGetPersonasHttpRequest


class LLMGetModels(MQContext):
    user_id: str = Field(
        description="ID of user to get models for")


class LLMGetModelsResponse(MQContext, LLMGetModelsHttpResponse):
    pass


class LLMGetPersonas(LLMGetModels, LLMGetPersonasHttpRequest):
    @property
    def model_name(self):
        return self.model_id.split("@")[0]

    @property
    def model_version(self):
        return self.model_id.split("@", 1)[1]


class LLMGetPersonasResponse(MQContext):
    model: Optional[BrainForgeLLM] = Field(
        "Full configuration of requested model if model is loaded and access "
        "is allowed, else None.")

    @property
    def personas(self) -> List[LLMPersona]:
        """
        Convenience property defined to easily reference the personas requested
        """
        return self.model.personas if self.model else []


class LLMGetInference(LLMRequest, MQContext):
    user_id: str = Field("ID of user making the request")

    def as_llm_request(self):
        """
        Get a plain `LLMRequest` object from this `LLMGetInference` object.
        """
        return LLMRequest(**self.model_dump())


class LLMGetInferenceResponse(LLMResponse, MQContext):
    pass


__all__ = [LLMGetModels.__name__, LLMGetModelsResponse.__name__,
           LLMGetPersonas.__name__, LLMGetPersonasResponse.__name__,
           LLMGetInference.__name__, LLMGetInferenceResponse.__name__]
