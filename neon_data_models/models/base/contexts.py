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

from datetime import datetime, timedelta
from typing import Literal, List, Optional

from neon_data_models.models.base import BaseModel


class SessionContext(BaseModel):
    session_id: str = "default"
    active_skills: List[str] = []
    utterance_states: dict = {}
    lang: Optional[str] = None
    context: dict = {}
    site_id: str = "unknown"
    pipeline: List[str] = []
    location: dict = {}
    system_unit: Optional[Literal["imperial", "metric"]] = None
    date_format: Optional[Literal["MDY", "YMD", "YDM", "DMY"]] = None
    time: Optional[Literal[12, 24]] = None
    is_recording: bool = False
    is_speaking: bool = False
    blacklisted_skills: List[str] = []
    blacklisted_intents: List[str] = []

    def model_dump(self, *args, **kwargs) -> dict:
        # Override to explicitly exclude default `None` values so that upstream
        # logic works to read values from global config
        kwargs["exclude_none"] = True
        return BaseModel.model_dump(self, *args, **kwargs)


class TimingContext(BaseModel):
    def __init__(self, **kwargs):
        # Enables backwards-compat. with old context values
        if transcribed := kwargs.pop("transcribed", None):
            kwargs.setdefault("handle_utterance", transcribed)
        if text_parsers := kwargs.pop("text_parsers", None):
            kwargs.setdefault("transform_utterance", text_parsers)
        BaseModel.__init__(self, **kwargs)

    audio_begin: Optional[datetime] = None
    audio_end: Optional[datetime] = None
    client_sent: Optional[datetime] = None
    gradio_sent: Optional[datetime] = None
    handle_utterance: Optional[datetime] = None
    response_sent: Optional[datetime] = None
    speech_start: Optional[datetime] = None

    get_stt: Optional[timedelta] = None
    get_tts: Optional[timedelta] = None
    iris_input_handling: Optional[timedelta] = None
    mq_response_handler: Optional[timedelta] = None
    mq_from_core: Optional[timedelta] = None
    mq_from_client: Optional[timedelta] = None
    mq_input_handler: Optional[timedelta] = None
    client_to_core: Optional[timedelta] = None
    client_from_core: Optional[timedelta] = None
    save_transcript: Optional[timedelta] = None
    transform_audio: Optional[timedelta] = None
    transform_utterance: Optional[timedelta] = None
    wait_in_queue: Optional[timedelta] = None


class KlatContext(BaseModel):
    sid: str
    cid: str
    title: Optional[str] = ""


class MQContext(BaseModel):
    routing_key: Optional[str] = None
    message_id: str
