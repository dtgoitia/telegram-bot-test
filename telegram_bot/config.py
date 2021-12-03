# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os
from dataclasses import dataclass


@dataclass
class Config:
    telegram_token: str
    telegram_bot_owner_user_id: int


def get_config() -> Config:
    config = Config(
        telegram_token=_get_string_from_env("TELEGRAM_API_BOT"),
        telegram_bot_owner_user_id=_get_int_from_env("TELEGRAM_BOT_OWNER_USER_ID"),
    )
    return config


def _get_from_env(name: str) -> str:
    try:
        return os.environ[name]
    except KeyError:
        raise EnvironmentError(f"Environment variable {name} must be set")


def _get_int_from_env(name: str) -> int:
    raw_value = _get_from_env(name=name)
    value = int(raw_value)
    return value


def _get_string_from_env(name: str) -> str:
    raw_value = _get_from_env(name=name)
    return raw_value
