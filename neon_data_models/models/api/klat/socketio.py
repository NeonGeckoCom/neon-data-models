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

from typing import Optional, Dict, List, Literal

from neon_data_models.models.api.llm import LLMPersona
from pydantic import Field

from neon_data_models.enum import CcaiPromptStates
from neon_data_models.models.base import BaseModel


class GetSttRequest(BaseModel):
    cid: str = Field(description="Conversation ID associated with the request")
    sid: str = Field(
        description="Client Session ID associated with the request")
    message_id: str = Field(
        description="Message (Shout) ID associated with the request")
    audio_data: str = Field(
        description="B64-encoded audio file object to transcribe")


class GetTtsRequest(BaseModel):
    cid: str = Field(description="Conversation ID associated with the request")
    sid: str = Field(
        description="Client Session ID associated with the request")
    message_id: str = Field(
        description="Message (Shout) ID associated with the request")
    text: str = Field(description="Text to generate audio for")
    lang: str = Field(description="BCP-47 Language code associated with `text`")


class NewMessage(BaseModel):
    cid: str = Field(description="Conversation ID associated with the message")
    userID: str = Field(description="User ID associated with the message")
    prompt_id: Optional[str] = Field(
        default=None, description="Prompt ID this message is in response to")
    promptState: CcaiPromptStates = Field(
        default=None,
        description="Associated CCAI state if `prompt_id` is defined")
    source: str = Field(description="Username associated with the message")
    messageText: str = Field(
        description="Message content (input string or audio filename)")
    repliedMessage: Optional[str] = Field(
        default=None, description="Message ID this message is a reply to")
    is_bot: Literal['0', '1'] = Field(
        default='0', description="'1' if the message came from a bot, else '0'")
    lang: str = Field(default='en', description="ISO 639-1 Language code")
    attachments: List[str] = Field(
        default=[],
        description="List of string filenames attached to this message")
    context: dict = Field(default={}, description="Optional arbitrary context")
    test: bool = Field(
        default=False,
        description="True if this message is associated with testing")
    isAudio: Literal['0', '1'] = Field(
        default="0",
        description="'1' if messageText represents encoded WAV audio")
    messageTTS: Dict[str, Dict[Literal['male', 'female'], str]] = Field(
        default={},
        description="TTS Audio formatted as {<language>: {<gender>: "
                    "<b64-encoded WAV>}}")
    isAnnouncement: bool = Field(
        default=False,
        description="True if the message is a system announcement")
    timeCreated: int = Field(description="Unix timestamp (epoch seconds)")
    message_id: str = Field(description="UUID for this message")
    bound_service: str = Field(default="", description="Service this message is targeting")

    class Config:
        use_enum_values = True
        validate_default = True


class PromptData(BaseModel):
    # TODO: Determine and document descriptions and a model for `data`
    data: dict = Field(description="Prompt data")
    receiver: str = Field()
    cid: str = Field(description="Conversation ID associated with the prompt")
    request_id = Field()


class RequestNeonTranslations(BaseModel):
    class CidTranslationRequest(BaseModel):
        lang: str = Field(description="Translation target language")
        source_lang: str = Field(description="Source language of shouts")
        shouts: Dict[str, str] = Field(
            default={}, description="Dict of shout ID to text in `lang`")

    request_id: str = Field(description="UUID for this request")
    data: Dict[str, CidTranslationRequest] = Field(
        description="Mapping of conversation ID to required translation")


class AuthExpired(BaseModel):
    body: str = Field(description="HTTP error response body")
    status: int = Field(description="HTTP response status code")
    handler: str = Field(description="Name of the requested function")


class ConfiguredPersonasChanged(BaseModel):
    personas: Dict[str, List[LLMPersona]] = (
        Field(description="Dict of LLM name to list of supported personas"))
    update_time: int = Field(
        description="Unix timestamp when the change occurred")


class BanSubmindFromConversation(BaseModel):
    # This model is used to both ban and revoke a ban
    cid: str = Field(description="Conversation ID to (un-)ban submind from")
    nick: str = Field(description="Username of the submind to (un-)ban")


__all__ = [GetSttRequest.__name__, GetTtsRequest.__name__, NewMessage.__name__,
           PromptData.__name__, RequestNeonTranslations.__name__,
           AuthExpired.__name__, BanSubmindFromConversation.__name__]