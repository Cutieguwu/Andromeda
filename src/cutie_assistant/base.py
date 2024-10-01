#!~/.pyenv/versions/3.11.6/bin/python
#
# Copyright (c) 2024 Cutieguwu | Olivia Brooks
#
# -*- coding: utf-8 -*-
# @Title: Base Classes
# @Author: Cutieguwu | Olivia Brooks
# @Description: Base classes to inherit from for functions in CutieAssistant.
#
# @Script: base.py
# @Date Created: 22 Jul, 2024
# @Last Modified: 24 Jul, 2024
# @Last Modified by: Cutieguwu | Olivia Brooks
# --------------------------------------------

from time import time
from json import load as load_json
from os.path import dirname
from tomllib import load as load_toml
from enum import Enum


class Plugin():
    def __init__(self, plugin, assistant, plugin_file):
        self.assistant = assistant

        plugin_path = dirname(plugin_file)

        self.EXPERIMENTAL_FEATURES = [].clear()                                         # Reduce memory allocation instead of using None

        self._load_plugin_properties(plugin_path)
        self._load_keywords(plugin_path)
        self._register(plugin.__module__)

        self.is_active_background = False
    
    def _get_compatability(self) -> Enum:
        """
        Checks to ensure that the plugin is compatible with the assistant.
        """

        version_max = self.ASSISTANT_VERSION_SUPPORT["max"]
        version_min = self.ASSISTANT_VERSION_SUPPORT["min"]

        if version_max is None:
            if version_min is None or self.assistant.VERSION > version_min:
                return PluginSupport.supported_unknown_future

            elif self.assistant.VERSION < version_min:
                return PluginSupport.unsupported_old

        elif self.assistant.VERSION > version_max:
            return PluginSupport.unsupported_new
        
        else:
            return PluginSupport.supported
            

    def _load_keywords(self, path):
        """
        Loads keywords from file.
        """

        with open(path  + "/keywords.json") as f:
            self.KEYWORDS = load_json(f)
    
    def _load_plugin_properties(self, path):
        """
        Loads the plugin properties from properties.toml
        """

        with open(path + "/properties.toml", "rb") as f:
            properties = load_toml(f)

        self.NAME = properties["plugin"]["name"]
        self.VERSION = properties["plugin"]["version"]

        self.ASSISTANT_VERSION_SUPPORT:dict = {}

        for ver in ["min", "max"]:
            try:
                self.ASSISTANT_VERSION_SUPPORT[ver] = properties["assistant"]["version"][ver]
            except KeyError:
                self.ASSISTANT_VERSION_SUPPORT[ver] = None

        self.IS_SUPPORTED = self._get_compatability()

        try:
            self.EXPERIMENTAL_FEATURES = properties["assistant"]["features"]
        except KeyError:
            pass
    
    def _register(self, plugin_name):
        """
        Adds `self` as plugin for `self.parent`
        """

        self.assistant.plugins[plugin_name] = self

class Trigger:
    def reset(self):
        """
        Resets the trigger.
        """

        if self.lifespan == 1:
            raise TriggerLifespanException
        elif self.lifespan != -1:
            self.lifespan = self.lifespan - 1

        self.build()

class Task:
    def __init__(self, assistant):
        self.assistant = assistant

        self._register()

    def remove(self):
        """
        Removes the task.
        """

        self.assistant.tracked_tasks.remove(self)

    def check(self):
        """
        Checks the task and runs and resets, or removes as needed.
        """

        try:
            self.run()
            self.trigger.reset()
        except TriggerLifespanException:
            self.remove()
    
    def _register(self):
        """
        Registers the task with the assistant.
        """

        self.assistant.tracked_tasks.append(self)

class WaitTimeTrigger():
    def __init__(self, wait_duration, lifespan = 1):

        self.build()
        self.wait_duration = wait_duration
        self.lifespan = lifespan

    def check(self):
        """
        returns `True` if trigger condition is met.
        """

        return True if time() - self.wait_duration >= self.wait_duration else False
    
    def build(self):
        """
        Builds trigger condition.
        """

        self.start_time = time()

class TriggerLifespanException(Exception):
    def __init__(self):
        self.message = "Lifespan of a trigger was spent."

class PluginSupport(Enum):
    """
    `supported` Enabled; Stable. Plugin is compatible with the assistant.\n
    `supported_unknown_future` Enabled; Potentially Unstable. Plugin support is unknown; no max version was set in its properties.\n
    `unsupported_new` Disabled; Stable. Plugin is too new; will not function with the assistant.\n
    `unsupported_old` Disabled; Stable. Plugin is too old and will not function with the assistant.\n
    `overridden` Enabled; Potentially Unstable. Only available if plugin is determined as `unsupported_old` so that if max version set and unmaintained, can be made to work.
    """

    supported = None
    supported_unknown_future = None
    unsupported_new = None
    unsupported_old = None
    overridden = None
