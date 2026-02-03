# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2026 Neongecko.com Inc.
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
from pydantic import (
    Field,
    model_validator,
    model_serializer,
    ConfigDict,
)

from neon_data_models.enum import CcaiState
from neon_data_models.models.base import BaseModel


class GetSttRequest(BaseModel):
    cid: str = Field(description="Conversation ID associated with the request")
    sid: str = Field(
        description="Shout ID associated with the request",
        alias="message_id"
    )
    user_uid: str = Field(
        description="User UUID associated with the request",
        alias="user_id",
        deprecated=True
    )
    lang: str = Field(
        description="BCP-47 Language code associated with audio",
        default="en-us",
    )


class GetSttResponse(BaseModel):
    transcript: str = Field(description="Transcribed text")
    lang: str = Field(
        description="BCP-47 Language code associated with `transcript`",
        default="en-us",
    )
    sid: str = Field(
        description="Shout ID associated with the request",
        alias="message_id"
    )
    cid: str = Field(description="Conversation ID associated with the request")
    context: Dict[str, Any] = Field(default={}, description="Optional context")

    @model_validator(mode="before")
    @classmethod
    def parse_context(cls, values):
        """
        Parse out message_id, sid, and cid from context if not handled by the
        Observer module.
        """
        values.setdefault("sid", values.get("context", {}).get("sid"))
        values.setdefault("cid", values.get("context", {}).get("cid"))
        return values


class GetTtsRequest(BaseModel):
    cid: str = Field(description="Conversation ID associated with the request")
    sid: str = Field(
        description="Shout ID associated with the request",
        alias="message_id"
    )
    user_uid: str = Field(
        description="User UUID associated with the request",
        alias="user_id",
        deprecated=True
    )
    lang: str = Field(
        description="BCP-47 Language code associated with `text`",
        default="en-us",
    )


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
    sid: str = Field(
        description="Shout ID associated with the request",
        alias="message_id"
    )
    cid: str = Field(description="Conversation ID associated with the request")
    context: Dict[str, Any] = Field(default={}, description="Optional context")

    @model_validator(mode="before")
    @classmethod
    def parse_context(cls, values):
        """
        Parse out sid, and cid from context if not handled by the
        Observer module.
        """
        values.setdefault("sid", values.get("context", {}).get("sid"))
        values.setdefault("cid", values.get("context", {}).get("cid"))
        return values

    def to_db_query(self) -> Dict[str, Any]:
        return {
            "shout_id": self.sid,
            "audio_data": self.audio_data,
            "lang": self.lang,
            "gender": self.gender,
        }

    def to_incoming_tts(self) -> Dict[str, Any]:
        return {
            "cid": self.cid,
            "sid": self.sid,
            "audio_data": self.audio_data,
            "lang": self.lang,
            "gender": self.gender,
        }


class NewPromptMessage(BaseModel):
    """
    Model representing a user message that relates to a CCAI prompt.
    """
    cid: str = Field(description="Conversation ID associated with the prompt and this response")
    user_id: str = Field(
            description="User ID (nick + suffix) associated with this message",
            alias="userID"
            )
    user_uid: str = Field(
        description="User UUID associated with this message"
    )
    prompt_id: str = Field(
        description="Unique ID for the prompt this message relates to", alias="promptID"
    )
    prompt_state: CcaiState = Field(
        description="CCAI state this response is associated with",
        default=CcaiState.IDLE,
        alias="promptState",
    )
    message_text: str = Field(
            description="Submind response content",
            alias="messageText",
            )
    context: Dict[str, Any] = Field(
        description="Extra context for the prompt", default={}
    )

    # Allow creation by name and alias inputs for backwards-compat.
    model_config = ConfigDict(validate_by_alias=True, validate_by_name=True)

    def model_dump(self, **kwargs):
        """
        Override model_dump to include SIO fields for backwards compatibility
        """

        # For backwards-compat with Klat Client, include aliased keys in
        # serialization. In the future, this should be configurable and
        # eventually removed.
        by_alias = {}
        if "by_alias" not in kwargs:
            by_alias = super().model_dump(by_alias=True, **kwargs)

        return {**super().model_dump(**kwargs), **by_alias}


class UserMessage(BaseModel):
    sid: str = Field(
        description="Shout ID associated with the message",
        alias="messageID"
    )
    cid: str = Field(description="Conversation ID associated with the message")
    user_id: Optional[str] = Field(
        default=None,
        description="User ID (nick + suffix) associated with the user",
        alias="userID",
    )
    user_uid: Optional[str] = Field(default=None, description="User UUID")
    username: Optional[str] = Field(
        description="Username of the sender",
        default=None,
        alias="userDisplayName"
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
    source: str = Field(
        default="unknown", description="Service associated with the message"
    )
    message_body: str = Field(
        description="Message content (input string or audio filename)",
        alias="messageText"
    )
    replied_message: Optional[str] = Field(
        default=None,
        description="Message ID this message is a reply to",
        alias="repliedMessage"
    )
    is_bot: Literal["0", "1"] = Field(
        default="0",
        description="'1' if the message came from a bot, else '0'",
        alias="bot",
    )
    lang: str = Field(default="en", description="ISO 639-1 Language code")
    attachments: List[str] = Field(
        default=[],
        description="List of string filenames attached to this message",
    )
    context: dict = Field(default={}, description="Optional arbitrary context")
    is_audio: bool = Field(
        default=False,
        description="True if message_body represents encoded WAV audio",
    )
    message_tts: Dict[str, Dict[Literal["male", "female"], str]] = Field(
        default={},
        alias="messageTTS",
        description="TTS Audio formatted as {<language>: {<gender>: "
        "<b64-encoded WAV>}}",
    )
    is_announcement: bool = Field(
        description="True if the message is a system announcement",
        default=False,
    )
    time_created: datetime = Field(
        description="Unix timestamp (epoch seconds)",
        alias="timeCreated"
    )
    bound_service: Optional[str] = Field(
        default=None,
        description="Service this message is targeting",
        alias="service_name",
    )

    # Below are observed as used, but purpose is unclear or deprecated
    no_save: bool = Field(default=False, deprecated=True)
    title: str = Field(default="", deprecated=True)
    routing_key: Optional[str] = Field(default=None, deprecated=True)
    bot_type: Optional[Any] = Field(default=None, deprecated=True)
    omit_reply: bool = Field(default=False, deprecated=True)
    to_discussion: bool = Field(default=False, deprecated=True)
    dom: Optional[str] = Field(default=None, deprecated=True)
    test: bool = Field(
        default=False,
        description="True if this message is associated with testing",
        deprecated=True
    )

    @model_validator(mode="before")
    @classmethod
    def validate_inputs(cls, values):
        if values.get("isAnnouncement") and "is_announcement" not in values:
            values["is_announcement"] = values.get("isAnnouncement") == 1
        if values.get("isAudio") and "is_audio" not in values:
            values["is_audio"] = values.get("isAudio") == 1
        if values.get("userDisplayName") and values.get("nick") and \
                values['nick'].startswith(values['userDisplayName']) and \
                values['nick'] != values['userDisplayName']:
            # Patch old behavior and ensure `user_id` is nick + suffix
            values['userID'] = values.pop('nick')
        return values

    @model_validator(mode="after")
    def validate_user_params(self):
        # Client appears to send a UID as a nick
        if self.user_id == self.username and self.user_id is not None:
            raise ValueError(f"user_id should be a nick + suffix, "
                             f"not nick ({self.user_id})")
        if self.username is None:
            if self.user_id is None:
                raise ValueError("Either user_id or username must be defined")
            self.username = self.user_id.split('-')[0] or "guest"
        return self

    class Config:
        use_enum_values = True
        validate_default = True
        # Allow creation by name and alias inputs for backwards-compat.
        validate_by_alias=True
        validate_by_name=True

    def to_db_query(self) -> Dict[str, Any]:
        return {
            "_id": self.sid,
            "cid": self.cid,
            "user_id": self.user_uid,
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
            user_uid=self.user_uid,
            prompt_id=self.prompt_id,
            prompt_state=self.prompt_state,
            context=self.context,
            message_text=self.message_body
        )

    def model_dump(self, **kwargs):
        """
        Override model_dump to include SIO fields for backwards compatibility
        """

        # For backwards-compat with Klat Client, include aliased keys in
        # serialization. In the future, this should be configurable and
        # eventually removed.
        by_alias = {}
        if "by_alias" not in kwargs:
            by_alias = super().model_dump(by_alias=True, **kwargs)
        return {**super().model_dump(**kwargs), **by_alias}


class NewCcaiPrompt(BaseModel):
    prompt_text: str = Field(
            description="Text of the prompt, without the '!PROMPT: ' prefix"
    )
    cid: str = Field(description="Conversation ID associated with the prompt")
    prompt_id: str = Field(description="Unique ID for the prompt")
    created_on: int = Field(
        descrtion="Epoch seconds of prompt creation",
        default_factory=lambda: int(time()),
    )
    context: Dict[str, Any] = Field(
        description="Extra context for the prompt", default={}
    )
    # Completed prompts sent to the client use below fields
    winner: Optional[str] = Field(default=None, description="Winning response User ID")
    participating_subminds: List[str] = Field(
        default=[],
        description="List of subminds by User ID that participated in this prompt",
    )
    proposed_responses: Dict[str, str] = Field(
        default={},
        description="Dict of participating submind User ID to proposed response",
    )
    votes: Dict[str, str] = Field(
        default={},
        description="Dict of participating submind User ID to vote",
    )
    submind_discussion_history: List[Dict[str, str]] = Field(
        default=[],
        description="List of discussoion round dicts of submind User ID to opinion response",
    )

    @model_validator(mode="before")
    @classmethod
    def validate_inputs(cls, values):
        # Handle an invalid input context as a valid empty dict
        # for backwards compatibility
        if values.get("context", {}) is None:
            values["context"] = {}
        if values.get("submind_opinions"):
            values["submind_discussion_history"] = [values.pop("submind_opinions")]
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


class CcaiPromptCompleted(UserMessage):
    winner: str = Field(
        default="",
        description="Winning response text; empty in the event of an error",
    )
    prompt_id: str = Field(
        description="Prompt ID this message is in response to",
    )
    sid: str = Field(
        description="Shout ID associated with the request"
    )
    conversation_context: Dict[str, Any] = Field(
        description="Context of the conversation", default={}
    )

    @model_validator(mode="before")
    @classmethod
    def validate_inputs(cls, values):
        values.setdefault(
            "winner", values.get("context", {}).get("winner", "")
        )
        if values.get("prompt_id") in (None, ""):
            # TODO: Figure out where this is set to an invalid value
            values.pop("prompt_id")
        values.setdefault(
            "prompt_id",
            values.get("context", {}).get("prompt", {}).get("prompt_id"),
        )
        assert values["prompt_id"] != "", (
            f"prompt_id must be defined: {values}"
        )
        return values

    @model_validator(mode="after")
    def validate_fields(self):
        # Client appears to send a UID as a nick
        if self.user_id == self.username:
            # TODO: This is patching backwards-compat.
            self.user_id = None
        if self.username is None:
            self.username = "guest"
        return self

    def to_db_query(self) -> Dict[str, Any]:
        return {
            "prompt_id": self.prompt_id,
            "prompt_context": self.context,
        }

    def model_dump(self, **kwargs):
        """
        Override model_dump to include SIO fields for backwards compatibility
        """

        # For backwards-compat with Klat Client, include aliased keys
        by_alias = {"promptID": self.prompt_id}
        return {**super().model_dump(**kwargs), **by_alias}


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
        is_completed: bool = Field(
            description="true if a response to the prompt has been determined"
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

        @model_validator(mode="before")
        @classmethod
        def normalize_completed(cls, values):
            if "is_completed" in values and isinstance(values["is_completed"], str):
                values["is_completed"] = values["is_completed"] == "1"
            return values

        @model_serializer
        def alias_serialize(self):
            # Alias to match existing MongoDB schema
            return {
                "_id": self.id,
                "is_completed": "1" if self.is_completed else "0",
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
]
