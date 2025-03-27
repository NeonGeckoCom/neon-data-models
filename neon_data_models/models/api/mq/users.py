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

from typing import Literal, Optional, Annotated, Union
from pydantic import Field, TypeAdapter, model_validator

from neon_data_models.models.api.jwt import HanaToken
from neon_data_models.models.base.contexts import MQContext
from neon_data_models.models.user.database import User


class CreateUserRequest(MQContext):
    operation: Literal["create"] = "create"
    user: User = Field(description="User object to create")


class ReadUserRequest(MQContext):
    operation: Literal["read"] = "read"
    user_spec: str = Field(description="Username or User ID to read")
    auth_user_spec: str = Field(
        default="", description="Username or ID to authorize database  read. "
                                "If unset, this will use `user_spec`")
    access_token: Optional[HanaToken] = Field(
        None, description="Token associated with `auth_username`")
    password: Optional[str] = Field(None,
                                    description="Password associated with "
                                                "`auth_username`")

    @model_validator(mode="after")
    def validate_params(self) -> 'ReadUserRequest':
        if not self.auth_user_spec:
            self.auth_user_spec = self.user_spec
        if self.access_token and self.access_token.purpose != "access":
            raise ValueError(f"Expected an access token but got: "
                             f"{self.access_token.purpose}")
        return self


class UpdateUserRequest(MQContext):
    operation: Literal["update"] = "update"
    user: User = Field(description="Updated User object to write to database")
    auth_username: str = Field(
        default="", description="Username to authorize database change. If "
                                "unset, this will use `user.username`")
    auth_password: str = Field(
        default="", description="Password (clear or hashed) associated with "
                                "`auth_username`. If unset, this will use "
                                "`user.password_hash`. If changing the "
                                "password, this must contain the existing "
                                "password, with the new password specified in "
                                "`user`")

    @model_validator(mode="after")
    def get_auth_username(self) -> 'UpdateUserRequest':
        if not self.auth_username:
            self.auth_username = self.user.username
        if not self.auth_password:
            self.auth_password = self.user.password_hash
        if not all((self.auth_username, self.auth_password)):
            raise ValueError("Missing auth_username or auth_password")
        return self


class DeleteUserRequest(MQContext):
    operation: Literal["delete"] = "delete"
    user: User = Field(description="Exact User object to remove from the "
                                   "database")


class UserDbRequest:
    """
    Generic class to dynamically build a UserDB CRUD request object based on the
    requested `operation`
    """
    ta = TypeAdapter(Annotated[Union[CreateUserRequest, ReadUserRequest,
                                     UpdateUserRequest, DeleteUserRequest],
                               Field(discriminator='operation')])

    def __new__(cls, *args, **kwargs):
        return cls.ta.validate_python(kwargs)


__all__ = [CreateUserRequest.__name__, ReadUserRequest.__name__,
           UpdateUserRequest.__name__, DeleteUserRequest.__name__,
           UserDbRequest.__name__]
