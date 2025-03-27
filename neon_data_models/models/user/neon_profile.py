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

import pytz
import datetime

from typing import Optional, List, Literal

from pydantic import Field

from neon_data_models.models.base import BaseModel

from neon_data_models.models.user.database import User


class ProfileUser(BaseModel):
    first_name: str = ""
    middle_name: str = ""
    last_name: str = ""
    preferred_name: str = ""
    full_name: str = ""
    dob: str = "YYYY/MM/DD"
    age: str = ""
    email: str = ""
    username: str = ""
    password: str = ""
    picture: str = Field(default="",
                         description="Fully-qualified URI of a user avatar. "
                                     "(i.e. `https://example.com/avatar.jpg")
    about: str = ""
    phone: str = ""
    phone_verified: bool = False
    email_verified: bool = False


class ProfileSpeech(BaseModel):
    stt_language: str = "en-us"
    alt_languages: List[str] = ['en']
    tts_language: str = "en-us"
    tts_gender: str = "female"
    neon_voice: Optional[str] = ''
    secondary_tts_language: Optional[str] = ''
    secondary_tts_gender: str = "male"
    secondary_neon_voice: str = ''
    speed_multiplier: float = 1.0


class ProfileUnits(BaseModel):
    time: Literal[12, 24] = 12
    date: Literal["MDY", "YMD", "YDM", "DMY"] = "MDY"
    measure: Literal["imperial", "metric"] = "imperial"


class ProfileLocation(BaseModel):
    lat: Optional[float] = None
    lng: Optional[float] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    tz: Optional[str] = None
    utc: Optional[float] = None


class ProfileResponseMode(BaseModel):
    speed_mode: str = "quick"
    hesitation: bool = False
    limit_dialog: bool = False


class ProfilePrivacy(BaseModel):
    save_audio: bool = False
    save_text: bool = False


class UserProfile(BaseModel):
    user: ProfileUser = ProfileUser()
    speech: ProfileSpeech = ProfileSpeech()
    units: ProfileUnits = ProfileUnits()
    location: ProfileLocation = ProfileLocation()
    response_mode: ProfileResponseMode = ProfileResponseMode()
    privacy: ProfilePrivacy = ProfilePrivacy()

    @classmethod
    def from_user_object(cls, user: User):
        user_config = user.neon
        today = datetime.date.today()
        if user_config.user.dob:
            dob = user_config.user.dob
            age = str(today.year - dob.year - (
                    (today.month, today.day) < (dob.month, dob.day)))
            dob = dob.strftime("%Y/%m/%d")
        else:
            age = ""
            dob = "YYYY/MM/DD"
        full_name = " ".join((n for n in (user_config.user.first_name,
                                          user_config.user.middle_name,
                                          user_config.user.last_name) if n))
        user = ProfileUser(about=user_config.user.about,
                           age=age, dob=dob,
                           email=user_config.user.email,
                           email_verified=False,
                           first_name=user_config.user.first_name,
                           full_name=full_name,
                           last_name=user_config.user.last_name,
                           middle_name=user_config.user.middle_name,
                           password=user.password_hash or "",
                           phone=user_config.user.phone,
                           phone_verified=False,
                           picture=user_config.user.avatar_url,
                           preferred_name=user_config.user.preferred_name,
                           username=user.username
                           )
        alt_stt = [lang.split('-')[0] for lang in
                   user_config.language.input_languages[1:]]
        secondary_tts_lang = user_config.language.output_languages[1] if (
                len(user_config.language.output_languages) > 1) else None
        speech = ProfileSpeech(
            alt_languages=alt_stt,
            secondary_tts_gender=user_config.response_mode.tts_gender,
            secondary_tts_language=secondary_tts_lang,
            speed_multiplier=user_config.response_mode.tts_speed_multiplier,
            stt_language=user_config.language.input_languages[0].split('-')[0],
            tts_gender=user_config.response_mode.tts_gender,
            tts_language=user_config.language.output_languages[0])
        units = ProfileUnits(**user_config.units.model_dump())
        utc_hours = (pytz.timezone(user_config.location.timezone or "UTC")
                     .utcoffset(datetime.datetime.now()).total_seconds() / 3600)
        # TODO: Get city, state, country from lat/lon
        location = ProfileLocation(lat=user_config.location.latitude,
                                   lng=user_config.location.longitude,
                                   tz=user_config.location.timezone,
                                   utc=utc_hours)
        response_mode = ProfileResponseMode(
            **user_config.response_mode.model_dump())
        privacy = ProfilePrivacy(**user_config.privacy.model_dump())

        return UserProfile(location=location, privacy=privacy,
                           response_mode=response_mode, speech=speech,
                           units=units, user=user)


__all__ = [ProfileUser.__name__, ProfileSpeech.__name__, ProfileUnits.__name__,
           ProfileLocation.__name__, ProfileResponseMode.__name__,
           ProfilePrivacy.__name__, UserProfile.__name__]
