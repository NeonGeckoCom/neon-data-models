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

from typing import List, Literal, Optional, Annotated, Union
from pydantic import Field, TypeAdapter, model_validator

from neon_data_models.models.base import BaseModel
from neon_data_models.models.base.contexts import KlatContext, MQContext
from neon_data_models.models.base.messagebus import BaseMessage, MessageContext


class GetTTSData(BaseModel):
    text: str = Field(description="Text to be spoken")

    @model_validator(mode='before')
    @classmethod
    def validate_inputs(cls, values):
        if 'text' not in values:
            values['text'] = values.pop('utterance')
        return values


class GetSTTData(BaseModel):
    audio_data: str = Field(description="Base64-encoded audio data")

    @model_validator(mode='before')
    @classmethod
    def validate_inputs(cls, values):
        if 'audio_data' not in values:
            values['audio_data'] = values.get('message_body')
        return values


class GetResponseData(BaseModel):
    utterances: List[str] = Field(description="List of input utterance(s)")

    @model_validator(mode='before')
    @classmethod
    def validate_inputs(cls, values):
        if 'utterances' not in values:
            values['utterances'] = [values.pop('messageText', '')]
        return values

class NeonGetTTS(BaseMessage, MQContext):
    msg_type: Literal["neon.get_tts"] = "neon.get_tts"
    data: GetTTSData


class NeonGetSTT(BaseMessage, MQContext):
    msg_type: Literal["neon.get_stt"] = "neon.get_stt"
    data: GetSTTData


class NeonGetResponse(BaseMessage, MQContext):
    msg_type: Literal["neon.get_response"] = "neon.get_response"
    data: GetResponseData


class NeonApiMessage(BaseModel):
    def from_sio_message(sio_message):
        requested_service = sio_message.get("requested_skill",
                                         "recognizer").lower()
        if requested_service not in ["stt", "tts", "recognizer"]:
            raise ValueError(f"Invalid requested service '{requested_service}'")
        klat_context = KlatContext(**sio_message)
        mq_context = MQContext(**sio_message)
        context = MessageContext(source="mq_api",
                                 client=sio_message.get("client", "unknown"),
                                 username=sio_message.get("nick", "guest"),
                                 klat_data=klat_context, mq=mq_context)
        if requested_service == "stt":
            context.destination = ["speech"]
            return NeonGetSTT(data=GetSTTData(**sio_message), context=context,
                              **mq_context)
        elif requested_service == "tts":
            context.destination = ["audio"]
            return NeonGetTTS(data=GetTTSData(**sio_message), context=context,
                              **mq_context)
        elif requested_service == "recognizer":
            context.destination = ["skills"]
            return NeonGetResponse(data=GetResponseData(**sio_message),
                                   context=context, **mq_context)

__all__ = [NeonGetTTS.__name__, NeonGetSTT.__name__, NeonGetResponse.__name__,
           NeonApiMessage.__name__]
