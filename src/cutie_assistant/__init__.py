#!~/.pyenv/versions/3.11.6/bin/python
#
# Copyright (c) 2024 Cutieguwu | Olivia Brooks
#
# -*- coding: utf-8 -*-
# @Title: CutieAssistant
# @Author: Cutieguwu | Olivia Brooks
# @Description: Personal Voice Assistant
#
# @Script: __init__.py
# @Date Created: 12 Jul, 2024
# @Last Modified: 22 Jul, 2024
# @Last Modified by: Cutieguwu | Olivia Brooks
# --------------------------------------------

from .utils import install_dependencies, contains_keywords, clean_query, get_threads, convert_to_flac, get_audio_file_name, _load_plugins


install_dependencies({"icecream", "SpeechRecognition", "coqui-tts", "openai-whisper", "pyaudio", "soundfile", "torch", "python-vlc"})

from icecream import ic
from TTS.api import TTS
from torch.cuda import is_available as cuda_available
import speech_recognition as sr
from speech_recognition import WaitTimeoutError
import vlc
from time import sleep
from os import remove as remove_file
from .base import Task, WaitTimeTrigger


ic.configureOutput("INFO | ")

class Assistant:
    """
    Personal Assistant
    """

    def __init__(self):
        print("INFO | Starting...")

        self.VERSION = [0, 0, 0]

        self.tracked_tasks = []
        self.plugins = {}

        print("INFO | Loading discovered plugins...")
        _load_plugins(self)
        print("INFO | Done.")

        ic(self.plugins)

        self._set_tts()

        self._set_mic_source()

        self.assistantOn = True

        print("INFO | Started.")

    def run(self):
        """
        Main run loop.
        """

        while self.assistantOn:
            self.run_checks()

            query = self.listen()

            if query != ("" or None) and contains_keywords(["execute"], query):
                self.check_query(query)

    def speak(self, response_map:dict):
        """
        Assistant Responses.
        """

        try:
            match response_map["response_type"]:
                case "rare":
                    output_path = "temp/output.wav"
                    raise FileNotFoundError                                             # rare types are saved as output.wav

                case "asset":
                    audio_path = "assets/effects/"

                case _:                                                                 # common and builtin types.
                    audio_path = f"cache/responses/{response_map['response_type']}/"
            
            audio_path = f"{audio_path}{get_audio_file_name(response_map)}"
            output_path = f"{audio_path}.wav"

            with open(f"{audio_path}.flac"):
                playback_path = f"{audio_path}.flac"
        
        except FileNotFoundError:

            print("INFO | Generating response as none was found...")

            self.TTS.tts_to_file(text=response_map["response"], speaker_wav="assets/speakers/venti.wav", file_path=output_path, language=self.TTS_LANGUAGE)

            print("INFO | Done.")

            if output_path != "temp/output.wav":
                print("INFO | Response is not rare.\nINFO | Converting to flac...")
                convert_to_flac(output_path)
                print("INFO | Done.")
                playback_path = f"{audio_path}.flac"
            else:
                playback_path = output_path

        media_player = vlc.MediaPlayer(playback_path)

        media_player.play()
        sleep(media_player.get_length() / 1000)

        if response_map["response_type"] == "common":
            TimedCache(self, playback_path)
    
    def listen(self):
        """
        Listens for a command set.
        """

        try:
            recognizer = sr.Recognizer()

            with sr.Microphone(device_index=self.MICROPHONE_INDEX) as microphone:
                recognizer.pause_threshold = 1
                print("INFO | Adjusting for ambient noise...")
                recognizer.adjust_for_ambient_noise(microphone)
                print("INFO | Done.")
                print("INFO | Recording...")
                audio = recognizer.listen(microphone, timeout=2, phrase_time_limit=5)
                print("INFO | Done.")

            print("INFO | Recognizing...")
            try:
                if self.TTS_LANGUAGE == "en":
                    query = recognizer.recognize_whisper(audio, model="small.en", language="en")
                else:
                    query = recognizer.recognize_whisper(audio, model="small", language="en")
                ic(query)

                print("INFO | Done.")
                return clean_query(query)
            
            except Exception as err:
                ic(err)
        except WaitTimeoutError:
            print("INFO | Heard nothing.")
        except AttributeError:
            print("Failed to open microphone.")

    def check_query(self, query:str):
        """
        Checks the query and calls an appropriate function.
        """

        pass

    def run_checks(self):
        """
        Runs some checks.
        """

        self.check_tasks()

    def check_tasks(self):
        """
        Checks and executes triggered tasks.
        """
        
        if len(self.tracked_tasks) == 0:
            return
        
        for t in self.tracked_tasks:
            t.check()
    
    def _set_tts(self):
        """
        Autoconfigures the TTS engine.
        """

        self.TTS_DEVICE = "cuda" if cuda_available() else "cpu"
        if self.TTS_DEVICE != "cuda":
            self.CPU_THREADS = get_threads()
            ic(f"{self.TTS_DEVICE} - {self.CPU_THREADS}")
        else:
            ic(self.TTS_DEVICE)

        self.TTS_LANGUAGE = "en"

        print("INFO | Loading Model...")
        self.TTS = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.TTS_DEVICE)
        print("INFO | Loaded Model.")

    def _set_mic_source(self):
        """
        Configures the microphone source.
        """

        print("--------------------------------------------")
        for index, device in enumerate(sr.Microphone.list_microphone_names()):            # Listing only working breaks on most systems.
            print("Microphone(device_index={0}) - '{1}' ".format(index, device))

        print("--------------------------------------------")
        self.MICROPHONE_INDEX = int(input("Enter Microphone Index: "))

class TimedCache(Task):
    def __init__(self, assistant, path, days:float = 30.0, lifespan=1):
        Task.__init__(self, assistant)

        self.path = path
        self.trigger = WaitTimeTrigger(days * 86400, lifespan)
    
    def run(self):
        """
        Runs the task's function.
        """

        remove_file(self.path)
