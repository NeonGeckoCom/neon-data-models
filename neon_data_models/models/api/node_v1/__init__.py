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

from datetime import datetime, timedelta
from pydantic import Field
from typing import List, Literal, Optional, Annotated, Dict

from neon_data_models.enum import UserData, AlertType, Weekdays
from neon_data_models.models.base import BaseModel
from neon_data_models.models.base.messagebus import BaseMessage, MessageContext


class AudioInputData(BaseModel):
    audio_data: str = Field(description="base64-encoded audio")
    lang: str = Field(description="BCP-47 language code")


class KlatResponse(BaseModel):
    sentence: str = Field(description="Text response")
    audio: Dict[Literal["male", "female"], Optional[str]] = Field(
        description="Mapping of gender to b64-encoded audio")


class AudioInputResponseData(BaseModel):
    parser_data: dict
    transcripts: List[str]
    skills_recv: bool


class NodeAudioInput(BaseMessage):
    msg_type: Literal["neon.audio_input"] = "neon.audio_input"
    data: AudioInputData


class NodeTextInput(BaseMessage):
    class UtteranceInputData(BaseModel):
        utterances: List[str] = Field(description="List of input utterance(s)")
        lang: str = Field(description="BCP-47 language")

    msg_type: Literal["recognizer_loop:utterance"] = "recognizer_loop:utterance"
    data: UtteranceInputData


class NodeGetStt(BaseMessage):
    msg_type: Literal["neon.get_stt"] = "neon.get_stt"
    data: AudioInputData


class NodeGetTts(BaseMessage):
    class TextInputData(BaseModel):
        text: str = Field(description="String text input")
        lang: str = Field(description="BCP-47 language code")

    msg_type: Literal["neon.get_tts"] = "neon.get_tts"
    data: TextInputData


class NodeKlatResponse(BaseMessage):
    msg_type: Literal["klat.response"] = "klat.response"
    data: Dict[str, KlatResponse] = Field(
        description="dict of BCP-47 language: KlatResponse")


class NodeAudioInputResponse(BaseMessage):
    msg_type: Literal["neon.audio_input.response"] = "neon.audio_input.response"
    data: AudioInputResponseData


class NodeGetSttResponse(BaseMessage):
    msg_type: Literal["neon.get_stt.response"] = "neon.get_stt.response"
    data: AudioInputResponseData


class NodeGetTtsResponse(BaseMessage):
    msg_type: Literal["neon.get_tts.response"] = "neon.get_tts.response"
    data: Dict[str, KlatResponse] = (
        Field(description="dict of BCP-47 language: KlatResponse"))


class CoreWWDetected(BaseMessage):
    msg_type: Literal["neon.ww_detected"] = "neon.ww_detected"
    # TODO: Define/implement schema in neon-speech service
    data: dict


class CoreIntentFailure(BaseMessage):
    msg_type: Literal["complete_intent_failure"] = "complete_intent_failure"
    data: dict  # Empty dict


class CoreErrorResponse(BaseMessage):
    class KlatErrorData(BaseModel):
        error: str = "unknown error"
        data: dict = {}

    msg_type: Literal["klat.error"] = "klat.error"
    data: KlatErrorData


class CoreClearData(BaseMessage):
    class ClearDataData(BaseModel):
        username: str
        data_to_remove: List[UserData]

    msg_type: Literal["neon.clear_data"] = "neon.clear_data"
    data: ClearDataData


class CoreAlertExpired(BaseMessage):
    class AlertData(BaseModel):
        alert_type: AlertType
        priority: Annotated[int, Field(gt=1, lt=10)]
        alert_name: str
        context: MessageContext
        next_expiration_time: Optional[datetime]
        repeat_frequency: Optional[timedelta]
        repeat_days: Optional[List[Weekdays]]
        end_repeat: Optional[datetime]
        audio_file: Optional[str] = None
        script_filename: Optional[str] = None

    msg_type: Literal["neon.alert_expired"] = "neon.alert_expired"
    data: AlertData


__all__ = [NodeAudioInput.__name__, NodeTextInput.__name__, NodeGetStt.__name__,
           NodeGetTts.__name__, NodeKlatResponse.__name__,
           NodeAudioInputResponse.__name__, NodeGetSttResponse.__name__,
           NodeGetTtsResponse.__name__, CoreWWDetected.__name__,
           CoreIntentFailure.__name__, CoreErrorResponse.__name__,
           CoreClearData.__name__, CoreAlertExpired.__name__]
