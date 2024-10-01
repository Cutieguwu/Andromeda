#!~/.pyenv/versions/3.11.6/bin/python
#
# Copyright (c) 2024 Cutieguwu | Olivia Brooks
#
# -*- coding: utf-8 -*-
# @Title: Personal Assistant
# @Author: Cutieguwu | Olivia Brooks
# @Description: Personal Assistant.
#
# @Script: main.py
# @Date Created: 22 Jul, 2024
# @Last Modified: 22 Jul, 2024
# @Last Modified by: Cutieguwu | Olivia Brooks
# --------------------------------------------

from cutie_assistant import Assistant

if __name__ == "__main__":
    try:
        assistant = Assistant()
        assistant.run()
    except KeyboardInterrupt:
        pass