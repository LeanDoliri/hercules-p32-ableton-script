# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.14.6 (tags/v3.14.6:c63aec6, Jun 10 2026, 10:26:10) [MSC v.1944 64 bit (AMD64)]
# Embedded file name: /Applications/Ableton Live 9 Suite.app/Contents/App-Resources/MIDI Remote Scripts/Hercules_P32_DJ/__init__.py
# Compiled at: 2017-10-20 06:12:58
from .hercules_p32_dj import hercules_p32_dj

def create_instance(c_instance):
    return hercules_p32_dj(c_instance)
