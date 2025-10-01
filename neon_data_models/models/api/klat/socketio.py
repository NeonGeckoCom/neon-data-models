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

import uuid

from time import time
from typing import Optional, Dict, List, Literal, Union, Any
from datetime import datetime
from pydantic import Field, model_validator, model_serializer

from neon_data_models.models.api.llm import LLMPersona
from neon_data_models.enum import CcaiState
from neon_data_models.models.base import BaseModel


class GetSttRequest(BaseModel):
    cid: str = Field(description="Conversation ID associated with the request")
    sid: str = Field(
        description="Client Session ID associated with the request"
    )
    lang: str = Field(
        description="BCP-47 Language code associated with audio",
        default="en-us",
    )
    message_id: str = Field(
        description="Message (Shout) ID associated with the request"
    )
    audio_data: str = Field(
        description="B64-encoded audio file object to transcribe"
    )


class GetSttResponse(BaseModel):
    transcript: str = Field(description="Transcribed text")
    lang: str = Field(
        description="BCP-47 Language code associated with `transcript`",
        default="en-us",
    )
    message_id: str = Field(
        description="Message (Shout) ID associated with the request"
    )
    sid: str = Field(
        description="Client Session ID associated with the request"
    )
    cid: str = Field(description="Conversation ID associated with the request")

    @model_validator(mode="before")
    @classmethod
    def parse_context(cls, values):
        """
        Parse out message_id, sid, and cid from context if not handled by the
        Observer module.
        """
        values.setdefault(
            "message_id", values.get("context", {}).get("message_id")
        )
        values.setdefault("sid", values.get("context", {}).get("sid"))
        values.setdefault("cid", values.get("context", {}).get("cid"))
        return values


class GetTtsRequest(BaseModel):
    cid: str = Field(description="Conversation ID associated with the request")
    sid: str = Field(
        description="Client Session ID associated with the request"
    )
    message_id: str = Field(
        description="Message (Shout) ID associated with the request"
    )
    text: str = Field(description="Text to generate audio for")
    lang: str = Field(
        description="BCP-47 Language code associated with `text`",
        default="en-us",
    )

    @model_validator(mode="before")
    @classmethod
    def validate_inputs(cls, values):
        if "message_text" in values:
            values.setdefault("text", values.pop("message_text"))
        return values


class GetTtsResponse(BaseModel):
    audio_data: str = Field(
        description="B64-encoded WAV audio file object generated from `text`"
    )
    lang: str = Field(
        description="BCP-47 Language code associated with `audio_data`",
        default="en-us",
    )
    gender: Literal["male", "female", "undefined"] = Field(
        description="Gender associated with generated audio",
        default="undefined",
    )
    message_id: str = Field(
        description="Message (Shout) ID associated with the request"
    )
    sid: str = Field(
        description="Client Session ID associated with the request"
    )
    cid: str = Field(description="Conversation ID associated with the request")

    @model_validator(mode="before")
    @classmethod
    def parse_context(cls, values):
        """
        Parse out message_id, sid, and cid from context if not handled by the
        Observer module.
        """
        values.setdefault(
            "message_id", values.get("context", {}).get("message_id")
        )
        values.setdefault("sid", values.get("context", {}).get("sid"))
        values.setdefault("cid", values.get("context", {}).get("cid"))
        return values

    def to_db_query(self) -> Dict[str, Any]:
        return {
            "shout_id": self.message_id,
            "audio_data": self.audio_data,
            "lang": self.lang,
            "gender": self.gender,
        }

    def to_incoming_tts(self) -> Dict[str, Any]:
        return {
            "cid": self.cid,
            "message_id": self.message_id,
            "audio_data": self.audio_data,
            "lang": self.lang,
            "gender": self.gender,
        }


class NewPromptMessage(BaseModel):
    cid: str = Field(description="Conversation ID associated with the prompt")
    user_id: str = Field(
        description="User ID associated with the prompt", alias="userID"
    )
    prompt_id: str = Field(
        description="Unique ID for the prompt", alias="promptID"
    )
    prompt_state: CcaiState = Field(
        description="CCAI state for the prompt",
        default=CcaiState.IDLE,
        alias="promptState",
    )
    context: Dict[str, Any] = Field(
        description="Extra context for the prompt", default={}
    )


class UserMessage(BaseModel):
    cid: str = Field(description="Conversation ID associated with the message")
    user_id: str = Field(
        description="User ID associated with the message", alias="userID"
    )
    user_nick: Optional[str] = Field(
        description="Username of the sender",
        default=None,
        alias="userDisplayName",
    )
    prompt_id: Optional[str] = Field(
        default=None,
        description="Prompt ID this message is in response to",
        alias="promptID",
    )
    prompt_state: Optional[CcaiState] = Field(
        default=None,
        alias="promptState",
        description="Associated CCAI state if `prompt_id` is defined",
    )
    source: str = Field(description="Service associated with the message")
    message_body: str = Field(
        description="Message content (input string or audio filename)",
        alias="messageText",
    )
    replied_message: Optional[str] = Field(
        default=None,
        description="Message ID this message is a reply to",
        alias="repliedMessage",
    )
    is_bot: Literal["0", "1"] = Field(
        default="0", description="'1' if the message came from a bot, else '0'"
    )
    lang: str = Field(default="en", description="ISO 639-1 Language code")
    attachments: List[str] = Field(
        default=[],
        description="List of string filenames attached to this message",
    )
    context: dict = Field(default={}, description="Optional arbitrary context")
    test: bool = Field(
        default=False,
        description="True if this message is associated with testing",
    )
    is_audio: Literal["0", "1"] = Field(
        default="0",
        description="'1' if messageText represents encoded WAV audio",
        alias="isAudio",
    )
    message_tts: Dict[str, Dict[Literal["male", "female"], str]] = Field(
        default={},
        alias="messageTTS",
        description="TTS Audio formatted as {<language>: {<gender>: "
        "<b64-encoded WAV>}}",
    )
    is_announcement: Literal["0", "1"] = Field(
        default="0",
        description="True if the message is a system announcement",
        alias="isAnnouncement",
    )
    time_created: datetime = Field(
        description="Unix timestamp (epoch seconds)", alias="timeCreated"
    )
    message_id: str = Field(
        description="UUID for this message",
        alias="messageID",
        default_factory=lambda: uuid.uuid4().hex[:10],
    )
    bound_service: str = Field(
        default="", description="Service this message is targeting"
    )

    @model_validator(mode="before")
    @classmethod
    def validate_inputs(cls, values):
        # Prefer the proper `messageText` key, but accept `message_body` for
        # backwards-compat.
        values["messageText"] = values.get("messageText") or values.get(
            "message_body"
        )
        values["is_bot"] = (
            values.get("is_bot")
            or values.get("isBot")
            or values.pop("bot", "0")
        )
        values["promptID"] = values.get("promptID") or values.pop(
            "prompt_id", None
        )
        return values

    class Config:
        use_enum_values = True
        validate_default = True

    def to_db_query(self) -> Dict[str, Any]:
        return {
            "_id": self.message_id,
            "cid": self.cid,
            "user_id": self.user_id,
            "prompt_id": self.prompt_id,
            "message_text": self.message_body,
            "message_lang": self.lang,
            "attachments": self.attachments,
            "replied_message": self.replied_message,
            "is_audio": self.is_audio,
            "is_announcement": self.is_announcement,
            "is_bot": self.is_bot,
            "translations": {},
            "created_on": int(self.time_created.timestamp()),
        }

    def to_new_prompt_message(self) -> NewPromptMessage:
        return NewPromptMessage(
            cid=self.cid,
            user_id=self.user_id,
            prompt_id=self.prompt_id,
            prompt_state=self.promptState,
            context=self.context,
        )


class NewCcaiPrompt(BaseModel):
    prompt_text: str = Field(
        description="Text of the prompt"
    )  # TODO: Check if formatted to remove prefix
    cid: str = Field(description="Conversation ID associated with the prompt")
    prompt_id: str = Field(
        description="Unique ID for the prompt"
    )  # TODO: Check for default value creation in Klat server
    created_on: int = Field(
        descrtion="Epoch seconds of prompt creation",
        default_factory=lambda: int(time()),
    )
    context: Dict[str, Any] = Field(
        description="Extra context for the prompt", deprecated=True, default={}
    )

    @model_validator(mode="before")
    @classmethod
    def validate_inputs(cls, values):
        # Handle an invalid input context as a valid empty dict
        # for backwards compatibility
        if values.get("context", {}) is None:
            values["context"] = {}
        return values

    def to_db_query(self) -> Dict[str, Any]:
        return {
            "_id": self.prompt_id,
            "cid": self.cid,
            "is_completed": "0",
            "data": {"prompt_text": self.prompt_text},
            "created_on": self.created_on,
            "context": self.context,
        }


class CcaiPromptCompleted(BaseModel):
    winner: str = Field(description="Winning response text")
    prompt_id: str = Field(description="Unique ID for the prompt")
    request_id: str = Field(
        description="ID of the database transaction request"
    )
    context: Dict[str, Any] = Field(
        description="Extra context for the prompt", default={}
    )

    @model_validator(mode="before")
    @classmethod
    def validate_inputs(cls, values):
        values.setdefault(
            "prompt_id",
            values.get("context", {}).get("prompt", {}).get("prompt_id"),
        )
        return values

    def to_db_query(self) -> Dict[str, Any]:
        return {
            "prompt_id": self.prompt_id,
            "prompt_context": self.context,
        }


class GetPromptData(BaseModel):
    nick: str = Field(description="Nickname of user requesting prompt data")
    cid: str = Field(description="Conversation ID associated with the prompt")
    limit: int = Field(
        default=5,
        description="Maximum number of prompts to return if `prompt_id` "
        "is unset",
    )
    prompt_id: Optional[str] = Field(
        default=None, description="Optional prompt ID to get data for"
    )

    def to_db_query(self) -> Dict[str, Any]:
        assert self.prompt_id is not None, "prompt_id must be defined"
        return {
            "cid": self.cid,
            "limit": self.limit,
            "prompt_ids": [self.prompt_id],
            "fetch_user_data": True,
        }


class PromptData(BaseModel):
    class _PromptData(BaseModel):
        id: str = Field(alias="_id", description="Unique ID for the prompt")
        is_completed: Literal["0", "1"] = Field(
            description="'1' if a response to the prompt has been determined"
        )
        proposed_responses: Dict[str, str] = Field(
            default={},
            description="Dict of participant name to proposed response",
        )
        submind_opinions: Dict[str, str] = Field(
            default={},
            description="Dict of participant name to opinion response",
        )
        votes: Dict[str, str] = Field(
            default={}, description="Dict of participant name to vote"
        )
        participating_subminds: List[str] = Field(
            default=[],
            description="List of subminds that participated in this prompt",
        )

        @model_serializer
        def alias_serialize(self):
            return {
                "_id": self.id,
                "is_completed": self.is_completed,
                "proposed_responses": self.proposed_responses,
                "submind_opinions": self.submind_opinions,
                "votes": self.votes,
                "participating_subminds": self.participating_subminds,
            }

    data: Union[_PromptData, List[_PromptData]] = Field(
        description="Prompt data"
    )
    receiver: str = Field(
        description="Nickname of user requesting prompt data"
    )
    cid: str = Field(description="Conversation ID associated with the prompt")
    request_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique ID of the request to identify the response",
    )


class AuthExpired(BaseModel):
    body: str = Field(description="HTTP error response body")
    status: int = Field(description="HTTP response status code")
    handler: str = Field(description="Name of the requested function")


class ConfiguredPersonasChanged(BaseModel):
    personas: Dict[str, List[LLMPersona]] = Field(
        description="Dict of LLM name to list of supported personas"
    )
    update_time: int = Field(
        description="Unix timestamp when the change occurred"
    )


class BanSubmindFromConversation(BaseModel):
    # This model is used to both ban and revoke a ban
    cid: str = Field(description="Conversation ID to (un-)ban submind from")
    nick: str = Field(description="Username of the submind to (un-)ban")


__all__ = [
    GetSttRequest.__name__,
    GetSttResponse.__name__,
    GetTtsRequest.__name__,
    GetTtsResponse.__name__,
    UserMessage.__name__,
    NewPromptMessage.__name__,
    GetPromptData.__name__,
    NewCcaiPrompt.__name__,
    CcaiPromptCompleted.__name__,
    PromptData.__name__,
    AuthExpired.__name__,
    BanSubmindFromConversation.__name__,
]
