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

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Literal
from neon_hana.schema.node_model import NodeData


class NodeInputContext(BaseModel):
    node_data: Optional[NodeData] = Field(description="Node Data")


class AudioInputData(BaseModel):
    audio_data: str = Field(description="base64-encoded audio")
    lang: str = Field(description="BCP-47 language code")


class TextInputData(BaseModel):
    text: str = Field(description="String text input")
    lang: str = Field(description="BCP-47 language code")


class UtteranceInputData(BaseModel):
    utterances: List[str] = Field(description="List of input utterance(s)")
    lang: str = Field(description="BCP-47 language")


class KlatResponse(BaseModel):
    sentence: str = Field(description="Text response")
    audio: dict = {Field(description="Audio Gender",
                         type=Literal["male", "female"]):
                   Field(description="b64-encoded audio", type=str)}


class TtsResponse(KlatResponse):
    translated: bool = Field(description="True if sentence was translated")
    phonemes: List[str] = Field(description="List of phonemes")
    genders: List[str] = Field(description="List of audio genders")


class KlatResponseData(BaseModel):
    responses: dict = {Field(type=str,
                             description="BCP-47 language"): KlatResponse}


class NodeAudioInput(BaseModel):
    msg_type: str = "neon.audio_input"
    data: AudioInputData
    context: NodeInputContext


class NodeTextInput(BaseModel):
    msg_type: str = "recognizer_loop:utterance"
    data: UtteranceInputData
    context: NodeInputContext


class NodeGetStt(BaseModel):
    msg_type: str = "neon.get_stt"
    data: AudioInputData
    context: NodeInputContext


class NodeGetTts(BaseModel):
    msg_type: str = "neon.get_tts"
    data: TextInputData
    context: NodeInputContext


class NodeKlatResponse(BaseModel):
    msg_type: str = "klat.response"
    data: dict = {Field(type=str, description="BCP-47 language"): KlatResponse}
    context: dict


class NodeAudioInputResponse(BaseModel):
    msg_type: str = "neon.audio_input.response"
    data: dict = {"parser_data": Field(description="Dict audio parser data",
                                       type=dict),
                  "transcripts": Field(description="Transcribed text",
                                       type=List[str]),
                  "skills_recv": Field(description="Skills service acknowledge",
                                       type=bool)}
    context: dict


class NodeGetSttResponse(BaseModel):
    msg_type: str = "neon.get_stt.response"
    data: dict = {"parser_data": Field(description="Dict audio parser data",
                                       type=dict),
                  "transcripts": Field(description="Transcribed text",
                                       type=List[str]),
                  "skills_recv": Field(description="Skills service acknowledge",
                                       type=bool)}
    context: dict


class NodeGetTtsResponse(BaseModel):
    msg_type: str = "neon.get_tts.response"
    data: KlatResponseData
    context: dict


class CoreWWDetected(BaseModel):
    msg_type: str = "neon.ww_detected"
    data: dict
    context: dict


class CoreIntentFailure(BaseModel):
    msg_type: str = "complete.intent.failure"
    data: dict
    context: dict


class CoreErrorResponse(BaseModel):
    msg_type: str = "klat.error"
    data: dict
    context: dict


class CoreClearData(BaseModel):
    msg_type: str = "neon.clear_data"
    data: dict
    context: dict


class CoreAlertExpired(BaseModel):
    msg_type: str = "neon.alert_expired"
    data: dict
    context: dict
