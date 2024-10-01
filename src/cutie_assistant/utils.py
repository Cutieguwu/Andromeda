#!~/.pyenv/versions/3.11.6/bin/python
#
# Copyright (c) 2024 Cutieguwu | Olivia Brooks
#
# -*- coding: utf-8 -*-
# @Title: CutieAssistant System Utilities
# @Author: Cutieguwu | Olivia Brooks
# @Description: Some utilities for running CutieAssistant
#
# @Script: system_utils.py
# @Date Created: 20 Jul, 2024
# @Last Modified: 24 Jul, 2024
# @Last Modified by: Cutieguwu | Olivia Brooks
# --------------------------------------------

from pkg_resources import working_set
from subprocess import run, CalledProcessError
from sys import executable
from icecream import ic
from os import cpu_count
from speech_recognition.audio import get_flac_converter
from json import load
from importlib import import_module
from pkgutil import iter_modules
import plugins


def install_dependencies(dependencies:set):
    """
    Tries to install and import any missing dependencies from set.
    """

    libraries_installed = {
        pkg.key for pkg in working_set
    }

    libraries_missing = list(dependencies - libraries_installed)                        # Lists are faster to iterate over due to lack of hash table.

    try:
        library = "pip"
        if len(libraries_missing) != 0:
            run([executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
            for library in libraries_missing:
                run([executable, "-m", "pip", "install", library], check=True)

    except CalledProcessError:
        print(f"Error | Cannot find or install {library}")
        raise SystemExit
    
def contains_keywords(keywords:list, query:str) -> bool:
    """
    Checks if a string contains one of the given keywords.
    """

    for k in keywords:
        if f" {k} " in f" {query} ":
            return True

    return False

def clean_query(query:str) -> str:
    """
    Cleans a query.
    """

    query_clean = ""

    for c in query.lower():
        if c.isalpha() or c == " ":
            query_clean = query_clean + c

    return query_clean

def run_command(command_list:list):
    """
    Runs a command and returns its output.
    """

    try:
        return run(command_list, capture_output=True, check=True).stdout.decode()
    except Exception as err:
        ic(f"Error | {command_list} raised {err}")
        return err
    
def get_threads() -> int:
    """
    Gets the number of threads on the system.
    If `os.cpu_count` returns `None`, sets thread count to `1`.
    """

    threads = cpu_count()

    return threads if threads is not None else 1

def convert_to_flac(source_path:str):
    """
    Converts an audio file to flac.
    Deletes original.
    """

    run_command(
        [
            get_flac_converter(),
            "--delete-input-file",
            "--best",
            source_path
        ]
    )

def get_response_map(service:str, response:str) -> dict:
    """
    Returns a `dict` of response commonality.
    """

    with open("assets/service_response_map.json", "r") as f:
        response_map = load(f)[service]

    response_map["service"] = service
    response_map["response"] = response

    return response_map

def get_audio_file_name(response_map) -> str:
    """
    Names and formats and audio file name.
    """

    file_name_response = ""

    for c in response_map["response"]:
        if c.isalpha():
            file_name_response = file_name_response + c.lower()
        else:
            file_name_response = file_name_response + "-"
    
    return f'{response_map["service"].upper()}_{file_name_response}'

def _load_plugins(assistant):
    """
    Loads all discovered plugins.
    """

    assistant.plugins = {import_module(name).Plugin(assistant) for finder, name, ispkg in iter_modules(plugins.__path__, plugins.__name__ + ".")}