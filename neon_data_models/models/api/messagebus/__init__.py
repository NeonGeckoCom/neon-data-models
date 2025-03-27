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
"""
Defines models for `Message` objects sent on the Neon messagebus.
"""

from typing import Any, List, Literal, Dict, Optional
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
        # Ensure input values are normalized to valid field names
        if hasattr(values, 'model_dump'):
            values = values.model_dump()
        if 'text' not in values:
            values['text'] = values.get('utterance')
        return values


class TtsResponse(BaseModel):
    sentence: str = Field(description="Text to be spoken")
    translated: bool = Field(
        default=False, 
        description="True if the text has been translated before TTS synthesis")
    phonemes: Optional[str] = Field(
        default=None, description="Phoneme representation of the sentence")
    genders: List[Gender] = Field(
        description="List of genders included in the response `audio` field",
        deprecated=True)
    male: Optional[str] = Field(default=None,
                                 description="Path to audio file in male voice")
    female: Optional[str] = Field(
        default=None, description="Path to audio file in female voice")
    audio: Dict[Gender, str]
    
    @model_validator(mode='after')
    def validate_gender_audio_match(self):
        """Validate that the genders list matches the audio dictionary keys."""
        if not set(self.genders) == set(self.audio.keys()):
            raise ValueError(
                "All genders listed in 'genders' must have corresponding "
                "entries in 'audio'")
        return self


class TtsSpeaker(BaseModel):
    name: str = Field(default="Neon", description="Name of the speaker")
    speaker: Optional[str] = Field(
        default=None, 
        description="Deprecated: Use 'name' instead",
        deprecated=True)
    language: str = Field(default="en-us", description="BCP-47 language code")
    gender: Gender = Field(default="female",
                          description="Requested or synthesized gender")
    voice: Optional[str] = Field(
        default=None, description="Requested or synthesized voice name")
    
    @model_validator(mode='before')
    @classmethod
    def map_speaker_to_name(cls, values):
        if hasattr(values, 'model_dump'):
            values = values.model_dump()
        if 'name' not in values and 'speaker' in values:
            values['name'] = values['speaker']
        return values


class TtsReponseData(BaseModel):
    responses: Dict[str, TtsResponse] = Field(
        description="Dictionary of BCP-47 lang codes to TTS responses")
    speaker: Optional[TtsSpeaker] = Field(
        default=None, description="Optional speaker metadata")


class GetSttData(BaseModel):
    audio_data: str = Field(description="Base64-encoded audio data")
    lang: str = Field(default="en-us",
                      description="BCP-47 language code for STT")

    @model_validator(mode='before')
    @classmethod
    def validate_inputs(cls, values):
        # Ensure input values are normalized to valid field names
        if hasattr(values, 'model_dump'):
            values = values.model_dump()
        if 'audio_data' not in values:
            values['audio_data'] = values.get('message_body')
        return values


class SttReponseData(BaseModel):
    transcripts: List[str]
    parser_data: Dict[str, Any]
    
    @model_validator(mode='after')
    def validate_transcripts_not_empty(self):
        """Validate that the transcripts list is not empty."""
        if not self.transcripts:
            raise ValueError("'transcripts' cannot be an empty list")
        return self


class GetResponseData(BaseModel):
    utterances: List[str] = Field(description="List of input utterance(s)")
    lang: str = Field(default="en-us",
                      description="BCP-47 language code for input/response")

    @model_validator(mode='before')
    @classmethod
    def validate_inputs(cls, values):
        # Ensure input values are normalized to valid field names
        if hasattr(values, 'model_dump'):
            values = values.model_dump()
        if 'utterances' not in values:
            values['utterances'] = [values.pop('messageText', '')]
        return values


class NeonLanguagesData(BaseModel):
    stt: List[str] = Field(description="List of supported STT languages")
    tts: List[str] = Field(description="List of supported TTS languages")
    skills: List[str] = Field(description="List of supported skill languages")


# Message models
class NeonGetTts(BaseMessage):
    msg_type: Literal["neon.get_tts"] = "neon.get_tts"
    data: GetTtsData

    @model_validator(mode='after')
    def ensure_audio_destination(self):
        if "audio" not in self.context.destination:
            self.context.destination = ["audio"]
        return self


class NeonGetStt(BaseMessage):
    msg_type: Literal["neon.get_stt"] = "neon.get_stt"
    data: GetSttData

    @model_validator(mode='after')
    def ensure_audio_destination(self):
        if "audio" not in self.context.destination:
            # Default context is not valid for this request, so override it
            self.context.destination = ["audio"]
        return self


class NeonTextInput(BaseMessage):
    msg_type: Literal["recognizer_loop:utterance"] = "recognizer_loop:utterance"
    data: GetResponseData

    @model_validator(mode='after')
    def ensure_skills_destination(self):
        if "skills" not in self.context.destination:
            self.context.destination.append("skills")
        return self


class NeonAudioInput(BaseMessage):
    msg_type: Literal["neon.audio_input"] = "neon.audio_input"
    data: GetSttData

    @model_validator(mode='after')
    def ensure_audio_destination(self):
        if "audio" not in self.context.destination:
            # Default context is not valid for this request, so override it
            self.context.destination = ["audio"]
        return self


class NeonSttResponse(BaseMessage):
    msg_type: Literal["neon.get_stt.response"] = "neon.get_stt.response"
    data: SttReponseData


class NeonTtsResponse(BaseMessage):
    msg_type: Literal["neon.get_tts.response",
                      "klat.response"] = "neon.get_tts.response"
    data: TtsReponseData


class NeonGetLanguages(BaseMessage):
    msg_type: Literal["neon.languages.get"] = "neon.languages.get"
    

class NeonLanguagesResponse(BaseMessage):
    msg_type: Literal["neon.languages.get.response"] = "neon.languages.get.response"
    data: NeonLanguagesData


__all__ = [NeonGetTts.__name__, NeonGetStt.__name__, NeonTextInput.__name__,
           NeonAudioInput.__name__, NeonSttResponse.__name__,
           NeonTtsResponse.__name__, NeonGetLanguages.__name__,
           NeonLanguagesResponse.__name__]
