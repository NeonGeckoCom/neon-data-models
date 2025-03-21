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
"""
Defines models for `Message` objects sent on the Neon messagebus.
"""

from typing import Any, List, Literal, Dict
from pydantic import Field, model_validator

from neon_data_models.types import Gender
from neon_data_models.models.base import BaseModel
from neon_data_models.models.base.messagebus import BaseMessage


# Data models
class GetTtsData(BaseModel):
    text: str = Field(description="Text to be spoken")
    lang: str = Field(default="en-us",
                      description="BCP-47 language code for TTS")

    @model_validator(mode='before')
    @classmethod
    def validate_inputs(cls, values):
        if hasattr(values, 'model_dump'):
            values = values.model_dump()
        if 'text' not in values:
            values['text'] = values.get('utterance')
        return values


class TtsResponse(BaseModel):
    sentence: str
    translated: bool
    phonemes: str
    genders: List[Gender]
    audio: Dict[Gender, str]


class TtsReponseData(BaseModel):
    responses: Dict[str, TtsResponse]


class GetSttData(BaseModel):
    audio_data: str = Field(description="Base64-encoded audio data")
    lang: str = Field(default="en-us",
                      description="BCP-47 language code for STT")

    @model_validator(mode='before')
    @classmethod
    def validate_inputs(cls, values):
        if hasattr(values, 'model_dump'):
            values = values.model_dump()
        if 'audio_data' not in values:
            values['audio_data'] = values.get('message_body')
        return values


class SttReponseData(BaseModel):
    transcripts: List[str]
    parser_data: Dict[str, Any]


class GetResponseData(BaseModel):
    utterances: List[str] = Field(description="List of input utterance(s)")
    lang: str = Field(default="en-us",
                      description="BCP-47 language code for input/response")

    @model_validator(mode='before')
    @classmethod
    def validate_inputs(cls, values):
        if hasattr(values, 'model_dump'):
            values = values.model_dump()
        if 'utterances' not in values:
            values['utterances'] = [values.pop('messageText', '')]
        return values


# Message models
class NeonGetTts(BaseMessage):
    msg_type: Literal["neon.get_tts"] = "neon.get_tts"
    data: GetTtsData


class NeonGetStt(BaseMessage):
    msg_type: Literal["neon.get_stt"] = "neon.get_stt"
    data: GetSttData


class NeonTextInput(BaseMessage):
    msg_type: Literal["recognizer_loop:utterance"] = "recognizer_loop:utterance"
    data: GetResponseData


class NeonAudioInput(BaseMessage):
    msg_type: Literal["neon.audio_input"] = "neon.audio_input"
    data: GetSttData


class NeonSttResponse(BaseMessage):
    msg_type: Literal["neon.get_stt.response"] = "neon.get_stt.response"
    data: SttReponseData


class NeonTtsResponse(BaseMessage):
    msg_type: Literal["neon.get_tts.response",
                      "klat.response"] = "neon.get_tts.response"
    data: TtsReponseData

__all__ = [NeonGetTts.__name__, NeonGetStt.__name__, NeonTextInput.__name__,
           NeonAudioInput.__name__, NeonSttResponse.__name__,
           NeonTtsResponse.__name__]