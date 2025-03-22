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

from typing import Annotated, List, Literal, Union
from pydantic import Field, TypeAdapter, model_validator

from neon_data_models.models.base import BaseModel
from neon_data_models.models.base.contexts import KlatContext, MQContext, \
    SessionContext, TimingContext
from neon_data_models.models.base.messagebus import BaseMessage, MessageContext
from neon_data_models.models.user.database import NeonUserConfig
from neon_data_models.models.api.messagebus import NeonGetLanguages, NeonGetTts, NeonGetStt, \
    NeonAudioInput, NeonLanguagesResponse, NeonTextInput, NeonSttResponse, NeonTtsResponse


class GetTtsData(BaseModel):
    text: str = Field(description="Text to be spoken")
    lang: str = Field(default="en-us",
                      description="BCP-47 language code for TTS")

    @model_validator(mode='before')
    @classmethod
    def validate_inputs(cls, values):
        if 'text' not in values:
            values['text'] = values.pop('utterance', None)
        return values


class GetSttData(BaseModel):
    audio_data: str = Field(description="Base64-encoded audio data")
    lang: str = Field(default="en-us",
                      description="BCP-47 language code for STT")

    @model_validator(mode='before')
    @classmethod
    def validate_inputs(cls, values):
        if 'audio_data' not in values:
            values['audio_data'] = values.get('message_body')
        return values


class GetResponseData(BaseModel):
    utterances: List[str] = Field(description="List of input utterance(s)")
    lang: str = Field(default="en-us",
                      description="BCP-47 language code for input/response")

    @model_validator(mode='before')
    @classmethod
    def validate_inputs(cls, values):
        if 'utterances' not in values:
            values['utterances'] = [values.pop('messageText', '')]
        return values

class NeonMqGetTts(NeonGetTts, MQContext):
    pass


class NeonMqGetStt(NeonGetStt, MQContext):
    pass

class NeonMqTextInput(NeonTextInput, MQContext):
    pass


class NeonMqAudioInput(NeonAudioInput, MQContext):
    pass


class NeonMqSttResponse(NeonSttResponse, MQContext):
    pass


class NeonMqTtsResponse(NeonTtsResponse, MQContext):
    pass


class NeonMqGetLanguages(NeonGetLanguages, MQContext):
    pass


class NeonMqLanguagesResponse(NeonLanguagesResponse, MQContext):
    pass


class NeonApiMessage:
    ta = TypeAdapter(Annotated[Union[NeonMqGetStt, NeonMqGetTts,
                                     NeonMqTextInput, NeonMqSttResponse,
                                     NeonMqTtsResponse, NeonMqGetLanguages,
                                     NeonMqLanguagesResponse],
                               Field(discriminator='msg_type')])

    @classmethod
    def __new__(cls, *args, **kwargs) -> BaseMessage:
        # Parse the MQ Context from a `Message` input to create a proper API message
        if 'message_id' not in kwargs:
            # Extract MQ context data from the message
            mq_data = kwargs.get('context', {}).get('mq', {})
            # Update values with MQ context data
            kwargs.update(mq_data)
        return cls.ta.validate_python(kwargs)

    @staticmethod
    def from_sio_message(sio_message: dict) -> BaseMessage:
        requested_service = sio_message.get("requested_skill",
                                         "recognizer").lower()
        if requested_service not in ["stt", "tts", "recognizer"]:
            raise ValueError(f"Invalid requested service '{requested_service}'")
        klat_context = KlatContext(**sio_message)
        mq_context = MQContext(**sio_message)
        context = MessageContext(source="mq_api",
                                 client=sio_message.get("client", "unknown"),
                                 username=sio_message.get("nick", "guest"),
                                 klat_data=klat_context, mq=mq_context,
                                 user_profiles=[NeonUserConfig()],
                                 session=SessionContext(
                                     session_id=sio_message.get("cid", "klat")),
                                 timing=TimingContext(
                                     client_sent=sio_message.get("timeCreated"))
        )
        if requested_service == "stt":
            context.destination = ["speech"]
            return NeonMqGetStt(data=GetSttData(**sio_message), context=context,
                              **mq_context.model_dump())
        elif requested_service == "tts":
            context.destination = ["audio"]
            return NeonMqGetTts(data=GetTtsData(**sio_message), context=context,
                              **mq_context.model_dump())
        elif requested_service == "recognizer":
            context.destination = ["skills"]
            return NeonMqTextInput(data=GetResponseData(**sio_message),
                                   context=context, **mq_context.model_dump())


__all__ = [NeonMqGetTts.__name__, NeonMqGetStt.__name__, 
           NeonMqTextInput.__name__, NeonMqSttResponse.__name__,
           NeonMqTtsResponse.__name__, NeonMqGetLanguages.__name__,
           NeonMqLanguagesResponse.__name__, NeonApiMessage.__name__]
