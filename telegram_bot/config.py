# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os
from dataclasses import dataclass


@dataclass
class Config:
    telegram_token: str


def get_config() -> Config:
    config = Config(
        telegram_token=_get_string_from_env("TELEGRAM_API_BOT"),
    )
    return config


def _get_string_from_env(name: str) -> str:
    try:
        return os.environ[name]
    except KeyError:
        raise EnvironmentError(f"Environment variable {name} must be set")
