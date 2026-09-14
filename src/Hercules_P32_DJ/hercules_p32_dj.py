# uncompyle6 version 3.9.3
# Python bytecode version base 2.7 (62211)
# Decompiled from: Python 3.14.6 (tags/v3.14.6:c63aec6, Jun 10 2026, 10:26:10) [MSC v.1944 64 bit (AMD64)]
# Embedded file name: /Applications/Ableton Live 9 Suite.app/Contents/App-Resources/MIDI Remote Scripts/Hercules_P32_DJ/hercules_p32_dj.py
# Compiled at: 2017-10-20 06:12:58
from __future__ import with_statement
import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.DeviceComponent import DeviceComponent
from _Framework.MixerComponent import MixerComponent
from _Framework.SliderElement import SliderElement
from _Framework.TransportComponent import TransportComponent
from _Framework.InputControlElement import *
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.SessionComponent import SessionComponent
from _Framework.EncoderElement import *
from .ConfigurableButtonElement import ConfigurableButtonElement

# Canales MIDI (0-based) tal como los emite la P32
CH_GLOBAL = 0
CH_DECK_A = 1
CH_DECK_B = 2

# Rango de notas de los pads por pagina (ambos decks)
PAD_SAMPLER = 36
PAD_SLICER = 52
PAD_LOOP = 68
PAD_HOTCUE = 84
PAD_END = 100

# Luces del teclado cromatico del deck derecho en Modo 2. Las notas van a la pista y ademas
# el script recibe una copia (forward_midi_note con should_consume_event=False) para
# iluminar el pad mas fuerte mientras esta presionado.
# Paginas con este patron: las cuatro del deck derecho (SAMPLER, SLICER, LOOP, HOTCUE).
KEYBOARD_LED_PAGES = (PAD_SAMPLER, PAD_SLICER, PAD_LOOP, PAD_HOTCUE)
KEYBOARD_LED_WHITE = (81, 127)   # violeta: (reposo, presionado)
# Ojo: los valores 40 y 80 no son "mas brillo", el firmware los toma como animacion de expansion.
# 125/126/127 son el rojo/azul/violeta a pleno que ya usa el Modo 1 (grabando/reproduciendo/triggered).
KEYBOARD_LED_BLACK = (41, 126)   # azul
KEYBOARD_LED_C = (1, 125)        # rojo: todas las C
BLACK_KEYS = (1, 3, 6, 8, 10)    # C#, D#, F#, G#, A#

# Poner en True para loguear en Log.txt cada mensaje MIDI que llega al script.
# Con el swallow global activo, casi todo llega: sirve para identificar que emite un boton fisico.
DEBUG_LOG_MIDI = False

def _debug_log(text):
    try:
        import logging
        logging.getLogger('hercules_p32_dj').info(text)
    except Exception:
        pass

def _describe_parameter(parameter):
    try:
        owner = parameter.canonical_parent
        track = getattr(owner, 'canonical_parent', None)
        return '%s @ %s' % (parameter.name, getattr(track, 'name', track))
    except Exception as e:
        return '%r (%s)' % (parameter, e)

class CappedEncoderElement(EncoderElement):
    def __init__(self, msg_type, channel, identifier, map_mode, *a, **k):
        super(CappedEncoderElement, self).__init__(msg_type, channel, identifier, map_mode, *a, **k)
        self._capped_parameter = None
        
    def connect_to(self, parameter):
        self._capped_parameter = parameter
        if DEBUG_LOG_MIDI:
            _debug_log('CappedEncoder ch%d cc%d connect_to %s' % (
                self.message_channel(), self.message_identifier(), _describe_parameter(parameter)))
        if not self.value_has_listener(self._on_custom_value):
            self.add_value_listener(self._on_custom_value)
            
    def release_parameter(self):
        self._capped_parameter = None
        if self.value_has_listener(self._on_custom_value):
            self.remove_value_listener(self._on_custom_value)
        super(CappedEncoderElement, self).release_parameter()
        
    def _on_custom_value(self, value):
        if self._capped_parameter is not None:
            self._capped_parameter.value = (value / 127.0) * 0.85
            if DEBUG_LOG_MIDI and value % 16 == 0:
                _debug_log('CappedEncoder ch%d cc%d: in=%d -> %s ahora=%.3f' % (
                    self.message_channel(), self.message_identifier(), value,
                    _describe_parameter(self._capped_parameter), self._capped_parameter.value))
        elif DEBUG_LOG_MIDI:
            _debug_log('CappedEncoder ch%d cc%d: valor %d sin parametro asignado' % (
                self.message_channel(), self.message_identifier(), value))

class hercules_p32_dj(ControlSurface):
    def _do_toggle_session_view(self, value):
        if value > 0:
            app_view = self.application().view
            if app_view.is_view_visible('Session'):
                app_view.show_view('Arranger')
            else:
                app_view.show_view('Session')

    def _do_tap_tempo(self, value):
        if value > 0:
            self.song().tap_tempo()

    def _do_locator(self, value):
        if value > 0:
            self.song().set_or_delete_cue()
            self.show_message('Locator Set/Deleted')

    def _do_undo(self, value):
        if value > 0 and self.song().can_undo:
            self.song().undo()
            self.show_message('Undo')

    def _do_redo(self, value):
        if value > 0 and self.song().can_redo:
            self.song().redo()
            self.show_message('Redo')



    def __init__(self, c_instance):
        global _map_modes
        global active_mode
        super(hercules_p32_dj, self).__init__(c_instance)
        with self.component_guard():
            _map_modes = Live.MidiMap.MapMode
            self.current_track_offset = 0
            self.current_scene_offset = 0
            num_tracks = 7
            num_returns = 24
            self.mixer = MixerComponent(num_tracks, num_returns)
            self._mode0()
            active_mode = '_mode1'
            self._set_active_mode()
            self._set_track_select_led()
            
            # El swallow de notas no usadas (selectores de pagina, botones libres, etc.)
            # se hace en build_midi_map(): todo lo que no este en _passthrough_notes() se captura.
            self._swallowed_notes = set()
            self._reported_notes = set()

            self.show_message('Hercules P32 DJ Ready')
        return

    def _mode2(self):
        self.show_message('_mode2 is active')
        num_tracks = 4
        num_scenes = 4
        self._session = SessionComponent(num_tracks, num_scenes)
        track_offset = self.current_track_offset
        scene_offset = self.current_scene_offset
        self._session.set_offsets(track_offset, scene_offset)
        self._session._reassign_scenes()
        self.set_highlighting_session_component(self._session)
        self._session.set_mixer(self.mixer)
        if hasattr(self._session, 'add_offset_listener'):
            self._session.add_offset_listener(self._on_session_offset_changed)
        session_buttons = [
         48, 49, 50, 51, 44, 45, 46, 47, 40, 41, 42, 43, 36, 37, 38, 39]
        session_channels = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        session_types = [MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, 
         MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, 
         MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, 
         MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, MIDI_NOTE_TYPE]
        session_is_momentary = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self._pads = [ButtonElement(session_is_momentary[index], session_types[index], session_channels[index], session_buttons[index]) for index in range(num_tracks * num_scenes)]
        self._grid = ButtonMatrixElement(rows=[self._pads[index * num_tracks:index * num_tracks + num_tracks] for index in range(num_scenes)])
        self._session.set_clip_launch_buttons(self._grid)
        # Stop Clip: botones ON/ON/ON/MACRO bajo los knobs (notas 3-6). MACRO derecho = Stop All.
        stop_all_button = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, CH_DECK_B, 6)
        self._session.set_stop_all_clips_button(stop_all_button)
        stop_track_buttons = [3, 4, 5, 6]
        stop_track_channels = [CH_DECK_A] * 4
        self._track_stop_buttons = [ConfigurableButtonElement(1, MIDI_NOTE_TYPE, stop_track_channels[index], stop_track_buttons[index]) for index in range(num_tracks)]
        self._session.set_stop_track_clip_buttons(tuple(self._track_stop_buttons))
        self._session._enable_skinning()
        self._session.set_stop_clip_triggered_value(127)
        self._session.set_stop_clip_value(81)
        for index in range(num_tracks):
            self._track_stop_buttons[index].set_on_off_values(81, 0)
        stop_all_button.set_on_off_values(127, 0)
        for scene_index in range(num_scenes):
            scene = self._session.scene(scene_index)
            scene.set_scene_value(81)
            scene.set_no_scene_value(0)
            scene.set_triggered_value(127)
            for track_index in range(num_tracks):
                clip_slot = scene.clip_slot(track_index)
                clip_slot.set_triggered_to_play_value(41)
                clip_slot.set_triggered_to_record_value(30)
                clip_slot.set_record_button_value(10)
                clip_slot.set_stopped_value(81)
                clip_slot.set_started_value(126)
                clip_slot.set_recording_value(125)

        self.session_right = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 5, 42)
        self._session.set_track_bank_right_button(self.session_right)
        self.session_right.add_value_listener(self._reload_active_devices, identify_sender=False)
        self.session_left = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 5, 40)
        self._session.set_track_bank_left_button(self.session_left)
        self.session_left.add_value_listener(self._reload_active_devices, identify_sender=False)
        self.session_down = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 5, 37)
        self._session.set_scene_bank_down_button(self.session_down)
        self.session_down.add_value_listener(self._reload_active_devices, identify_sender=False)
        self.session_up = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 5, 45)
        self._session.set_scene_bank_up_button(self.session_up)
        self.session_up.add_value_listener(self._reload_active_devices, identify_sender=False)
        self.refresh_state()
        self._mode2_devices()
        self._light_mode2_keyboard(True)
        self.add_device_listeners()
        self.request_rebuild_midi_map()
        self.mode_2_to_1 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 0, 1)
        self.mode_2_to_1.add_value_listener(self._activate_mode1, identify_sender=False)
        return

    def _send_raw(self, status, data1, data2):
        msg = (status, data1, data2)
        if DEBUG_LOG_MIDI:
            self.log_message('P32 MIDI out: %s' % (msg,))
        if hasattr(self, '_send_midi'):
            self._send_midi(msg)
        elif hasattr(self, 'send_midi'):
            self.send_midi(msg)

    def _keyboard_led_value(self, note, pressed):
        pitch = note % 12
        if pitch == 0:
            pair = KEYBOARD_LED_C
        elif pitch in BLACK_KEYS:
            pair = KEYBOARD_LED_BLACK
        else:
            pair = KEYBOARD_LED_WHITE
        return pair[1] if pressed else pair[0]

    def _keyboard_notes(self):
        keys = set()
        for page_start in KEYBOARD_LED_PAGES:
            for note in range(page_start, page_start + 16):
                keys.add((CH_DECK_B, note))
        return keys

    def _light_mode2_keyboard(self, on):
        """Ilumina (o apaga) las paginas libres del deck derecho como un teclado."""
        status = 0x90 | CH_DECK_B
        for ch, note in sorted(self._keyboard_notes()):
            self._send_raw(status, note, self._keyboard_led_value(note, False) if on else 0)

    def _remove_mode2(self):
        self._light_mode2_keyboard(False)
        self._remove_mode2_devices()
        self.remove_device_listeners()
        self._session.set_clip_launch_buttons(None)
        self.set_highlighting_session_component(None)
        self._session.set_stop_all_clips_button(None)
        self._session.set_stop_track_clip_buttons(None)
        self._track_stop_buttons = None
        self.session_right.remove_value_listener(self._reload_active_devices)
        self._session.set_track_bank_right_button(None)
        self.session_left.remove_value_listener(self._reload_active_devices)
        self._session.set_track_bank_left_button(None)
        self.session_down.remove_value_listener(self._reload_active_devices)
        self._session.set_scene_bank_down_button(None)
        self.session_up.remove_value_listener(self._reload_active_devices)
        self._session.set_scene_bank_up_button(None)
        if getattr(self, '_session', None) is not None:
            if hasattr(self._session, 'remove_offset_listener') and hasattr(self._session, 'offset_has_listener'):
                if self._session.offset_has_listener(self._on_session_offset_changed):
                    self._session.remove_offset_listener(self._on_session_offset_changed)
            self.current_track_offset = self._session._track_offset
            self.current_scene_offset = self._session._scene_offset
            self._session.set_mixer(None)
        self._session = None
        self.mode_2_to_1.remove_value_listener(self._activate_mode1)
        self.mode_2_to_1 = None
        return

    def _mode2_devices(self):
        # Los knobs de EQ del centro quedan libres tambien en Modo 2 (antes: envios A/B/C
        # de la pista seleccionada en el deck izquierdo y volumen de retornos en el derecho).
        return

    def _remove_mode2_devices(self):
        return


    def _setup_loop_controls(self):
        self._loop_buttons = []
        for deck, channel in enumerate([1, 2]):
            for col in range(4):
                track_index = deck * 4 + col
                note_row1 = 80 + col
                note_row2 = 76 + col
                note_row3 = 72 + col
                note_row4 = 68 + col
                
                b1 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, channel, note_row1)
                b2 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, channel, note_row2)
                b3 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, channel, note_row3)
                b4 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, channel, note_row4)
                
                cb1 = lambda value, btn=b1, t=track_index: self._on_loop_toggle(value, btn, t)
                cb2 = lambda value, btn=b2, t=track_index: self._on_loop_halve(value, btn, t)
                cb3 = lambda value, btn=b3, t=track_index: self._on_loop_double(value, btn, t)
                cb4 = lambda value, btn=b4, t=track_index: self._on_loop_beatjump(value, btn, t)
                
                b1.add_value_listener(cb1, identify_sender=False)
                b2.add_value_listener(cb2, identify_sender=False)
                b3.add_value_listener(cb3, identify_sender=False)
                b4.add_value_listener(cb4, identify_sender=False)
                
                # Turn on dim lights initially
                b1.send_value(1) # Dim Red
                b2.send_value(81) # Dim Purple
                b3.send_value(81) # Dim Purple
                b4.send_value(41) # Dim Blue
                
                self._loop_buttons.append((b1, cb1))
                self._loop_buttons.append((b2, cb2))
                self._loop_buttons.append((b3, cb3))
                self._loop_buttons.append((b4, cb4))

    def _teardown_loop_controls(self):
        if hasattr(self, '_loop_buttons') and self._loop_buttons:
            for item in self._loop_buttons:
                try:
                    if isinstance(item, tuple):
                        btn, cb = item
                        try:
                            btn.remove_value_listener(cb)
                        except Exception:
                            pass
                        btn.send_value(0)
                        btn.disconnect()
                    else:
                        item.send_value(0)
                        item.disconnect()
                except Exception:
                    pass
            self._loop_buttons = []

    def _get_playing_clip(self, track_index):
        offset = 0
        if getattr(self, '_session', None) is not None:
            offset = self._session._track_offset
        actual_idx = offset + track_index
        if actual_idx < len(self.song().tracks):
            track = self.song().tracks[actual_idx]
            for slot in track.clip_slots:
                if slot.has_clip and slot.clip.is_playing:
                    return slot.clip
        return None

    def _on_loop_toggle(self, value, btn, track_index):
        btn.send_value(40 if value > 0 else 1)
        if value > 0:
            clip = self._get_playing_clip(track_index)
            if clip:
                clip.looping = not clip.looping

    def _on_loop_halve(self, value, btn, track_index):
        btn.send_value(127 if value > 0 else 81)
        if value > 0:
            clip = self._get_playing_clip(track_index)
            if clip and clip.looping:
                length = clip.loop_end - clip.loop_start
                if length > 0.125:
                    clip.loop_end = clip.loop_start + (length / 2.0)

    def _on_loop_double(self, value, btn, track_index):
        btn.send_value(127 if value > 0 else 81)
        if value > 0:
            clip = self._get_playing_clip(track_index)
            if clip and clip.looping:
                length = clip.loop_end - clip.loop_start
                new_end = clip.loop_start + (length * 2.0)
                try:
                    end_marker = clip.end_marker
                except Exception:
                    end_marker = None
                if end_marker is not None and not clip.is_midi_clip:
                    new_end = min(new_end, end_marker)
                if new_end > clip.loop_end:
                    clip.loop_end = new_end

    def _on_loop_beatjump(self, value, btn, track_index):
        btn.send_value(80 if value > 0 else 41)
        if value > 0:
            clip = self._get_playing_clip(track_index)
            if clip and clip.looping:
                length = clip.loop_end - clip.loop_start
                clip.loop_end += length
                clip.loop_start += length
                
                # playing_position es de solo lectura; move_playing_pos salta en beats
                try:
                    clip.move_playing_pos(length)
                except Exception:
                    pass

    def _mode1(self):
        self.show_message('_mode1 is active')
        num_tracks = 7
        num_scenes = 4
        self._session = SessionComponent(num_tracks, num_scenes)
        track_offset = self.current_track_offset
        scene_offset = self.current_scene_offset
        self._session.set_offsets(track_offset, scene_offset)
        self._session._reassign_scenes()
        self.set_highlighting_session_component(self._session)
        self._session.set_mixer(self.mixer)
        if hasattr(self._session, 'add_offset_listener'):
            self._session.add_offset_listener(self._on_session_offset_changed)
        session_buttons = [
         48, 49, 50, 51, 48, 49, 50, 44, 45, 46, 47, 44, 45, 46, 
         40, 41, 42, 43, 40, 41, 42, 36, 37, 38, 39, 36, 37, 
         38]
        session_channels = [1, 1, 1, 1, 2, 2, 2, 1, 1, 1, 1, 2, 2, 2, 1, 
         1, 1, 1, 2, 2, 2, 1, 1, 1, 1, 2, 2, 2]
        session_types = [MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, 
         MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, 
         MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, 
         MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, 
         MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, 
         MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, 
         MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, MIDI_NOTE_TYPE]
        session_is_momentary = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 
         1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self._pads = [ButtonElement(session_is_momentary[index], session_types[index], session_channels[index], session_buttons[index]) for index in range(num_tracks * num_scenes)]
        self._grid = ButtonMatrixElement(rows=[self._pads[index * num_tracks:index * num_tracks + num_tracks] for index in range(num_scenes)])
        self._session.set_clip_launch_buttons(self._grid)
        # Stop Clip: botones ON/ON/ON/MACRO bajo los knobs (notas 3-6). MACRO derecho = Stop All.
        stop_all_button = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, CH_DECK_B, 6)
        self._session.set_stop_all_clips_button(stop_all_button)
        stop_track_buttons = [3, 4, 5, 6, 3, 4, 5]
        stop_track_channels = [CH_DECK_A] * 4 + [CH_DECK_B] * 3
        self._track_stop_buttons = [ConfigurableButtonElement(1, MIDI_NOTE_TYPE, stop_track_channels[index], stop_track_buttons[index]) for index in range(num_tracks)]
        self._session.set_stop_track_clip_buttons(tuple(self._track_stop_buttons))
        scene_buttons = [
         51, 47, 43, 39]
        scene_channels = [2, 2, 2, 2]
        scene_types = [MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, MIDI_NOTE_TYPE, MIDI_NOTE_TYPE]
        scene_momentarys = [1, 1, 1, 1]
        self._scene_launch_buttons_raw = [ButtonElement(scene_momentarys[index], scene_types[index], scene_channels[index], scene_buttons[index]) for index in range(num_scenes)]
        self._scene_launch_buttons = ButtonMatrixElement(rows=[self._scene_launch_buttons_raw])
        self._session.set_scene_launch_buttons(self._scene_launch_buttons)
        self._session._enable_skinning()
        self._session.set_stop_clip_triggered_value(127)
        self._session.set_stop_clip_value(81)
        for scene_index in range(num_scenes):
            scene = self._session.scene(scene_index)
            scene.set_scene_value(81)
            scene.set_no_scene_value(0)
            scene.set_triggered_value(127)
            for track_index in range(num_tracks):
                clip_slot = scene.clip_slot(track_index)
                clip_slot.set_triggered_to_play_value(41)
                clip_slot.set_triggered_to_record_value(30)
                clip_slot.set_record_button_value(10)
                clip_slot.set_stopped_value(81)
                clip_slot.set_started_value(126)
                clip_slot.set_recording_value(125)
        for index in range(num_tracks):
            self._track_stop_buttons[index].set_on_off_values(81, 0)
        stop_all_button.set_on_off_values(127, 0)

        self.session_up = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 5, 45)
        self._session.set_scene_bank_up_button(self.session_up)
        self.session_up.add_value_listener(self._reload_active_devices, identify_sender=False)
        self.session_left = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 5, 40)
        self._session.set_track_bank_left_button(self.session_left)
        self.session_left.add_value_listener(self._reload_active_devices, identify_sender=False)
        self.session_right = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 5, 42)
        self._session.set_track_bank_right_button(self.session_right)
        self.session_right.add_value_listener(self._reload_active_devices, identify_sender=False)
        self.session_down = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 5, 37)
        self._session.set_scene_bank_down_button(self.session_down)
        self.session_down.add_value_listener(self._reload_active_devices, identify_sender=False)
        self._session._link()
        self.refresh_state()
        self.arm_specific_4 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 2, 52)
        self.arm_specific_4.set_on_off_values(125, 1)
        self.mixer.channel_strip(4).set_arm_button(self.arm_specific_4)
        self.arm_specific_5 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 2, 53)
        self.arm_specific_5.set_on_off_values(125, 1)
        self.mixer.channel_strip(5).set_arm_button(self.arm_specific_5)
        self.arm_specific_6 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 2, 54)
        self.arm_specific_6.set_on_off_values(125, 1)
        self.mixer.channel_strip(6).set_arm_button(self.arm_specific_6)
        self.solo_specific_4 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 2, 56)
        self.solo_specific_4.set_on_off_values(126, 41)
        self.mixer.channel_strip(4).set_solo_button(self.solo_specific_4)
        self.solo_specific_5 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 2, 57)
        self.solo_specific_5.set_on_off_values(126, 41)
        self.mixer.channel_strip(5).set_solo_button(self.solo_specific_5)
        self.solo_specific_6 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 2, 58)
        self.solo_specific_6.set_on_off_values(126, 41)
        self.mixer.channel_strip(6).set_solo_button(self.solo_specific_6)
        self.mute_specific_4 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 2, 60)
        self.mute_specific_4.set_on_off_values(127, 81)
        self.mixer.channel_strip(4).set_mute_button(self.mute_specific_4)
        self.mixer.channel_strip(4).set_invert_mute_feedback(True)
        self.mute_specific_5 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 2, 61)
        self.mute_specific_5.set_on_off_values(127, 81)
        self.mixer.channel_strip(5).set_mute_button(self.mute_specific_5)
        self.mixer.channel_strip(5).set_invert_mute_feedback(True)
        self.mute_specific_6 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 2, 62)
        self.mute_specific_6.set_on_off_values(127, 81)
        self.mixer.channel_strip(6).set_mute_button(self.mute_specific_6)
        self.mixer.channel_strip(6).set_invert_mute_feedback(True)
        self.trackselect7 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 2, 66)
        self.trackselect7.set_on_off_values(127, 81)
        self.trackselect7.add_value_listener(self.track_select_7, identify_sender=False)
        self.trackselect6 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 2, 65)
        self.trackselect6.set_on_off_values(127, 81)
        self.trackselect6.add_value_listener(self.track_select_6, identify_sender=False)
        self.trackselect5 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 2, 64)
        self.trackselect5.set_on_off_values(127, 81)
        self.trackselect5.add_value_listener(self.track_select_5, identify_sender=False)
        self._mode1_devices()
        self.add_device_listeners()
        self._setup_loop_controls()
        self.request_rebuild_midi_map()
        self.mode_1_to_2 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 0, 1)
        self.mode_1_to_2.add_value_listener(self._activate_mode2, identify_sender=False)
        return

    def _remove_mode1(self):
        # Clear all LEDs on Right Deck (Channel 3 -> Note On 146)
        for note in range(36, 68):
            if hasattr(self, 'send_midi'):
                self.send_midi((146, note, 0))
            elif hasattr(self, '_send_midi'):
                self._send_midi((146, note, 0))
        if hasattr(self, '_pads') and self._pads is not None:
            for pad in self._pads:
                if pad is not None:
                    pad.turn_off()
        if hasattr(self, '_scene_launch_buttons_raw') and self._scene_launch_buttons_raw is not None:
            for pad in self._scene_launch_buttons_raw:
                if pad is not None:
                    pad.turn_off()
        self._remove_mode1_devices()
        self.remove_device_listeners()
        self._session.set_clip_launch_buttons(None)
        self.set_highlighting_session_component(None)
        self._session.set_stop_all_clips_button(None)
        self._session.set_stop_track_clip_buttons(None)
        self._track_stop_buttons = None
        self._scene_launch_buttons = None
        self._session.set_scene_launch_buttons(None)
        self.session_up.remove_value_listener(self._reload_active_devices)
        self._session.set_scene_bank_up_button(None)
        self.session_left.remove_value_listener(self._reload_active_devices)
        self._session.set_track_bank_left_button(None)
        self.session_right.remove_value_listener(self._reload_active_devices)
        self._session.set_track_bank_right_button(None)
        self.session_down.remove_value_listener(self._reload_active_devices)
        self._session.set_scene_bank_down_button(None)
        if getattr(self, '_session', None) is not None:
            if hasattr(self._session, 'remove_offset_listener') and hasattr(self._session, 'offset_has_listener'):
                if self._session.offset_has_listener(self._on_session_offset_changed):
                    self._session.remove_offset_listener(self._on_session_offset_changed)
            self.current_track_offset = self._session._track_offset
            self.current_scene_offset = self._session._scene_offset
            self._session.set_mixer(None)
        self.mixer.channel_strip(4).set_arm_button(None)
        self.mixer.channel_strip(5).set_arm_button(None)
        self.mixer.channel_strip(6).set_arm_button(None)
        self.mixer.channel_strip(4).set_solo_button(None)
        self.mixer.channel_strip(5).set_solo_button(None)
        self.mixer.channel_strip(6).set_solo_button(None)
        self.mixer.channel_strip(4).set_mute_button(None)
        self.mixer.channel_strip(5).set_mute_button(None)
        self.mixer.channel_strip(6).set_mute_button(None)

        for btn_name in ['arm_specific_4', 'arm_specific_5', 'arm_specific_6',
                         'solo_specific_4', 'solo_specific_5', 'solo_specific_6',
                         'mute_specific_4', 'mute_specific_5', 'mute_specific_6']:
            if hasattr(self, btn_name):
                btn = getattr(self, btn_name)
                if btn is not None:
                    try:
                        btn.send_value(0)
                        btn.set_enabled(False)
                        btn.disconnect()
                    except Exception:
                        pass
                    setattr(self, btn_name, None)

        for ts_name, listener in [('trackselect7', self.track_select_7),
                                  ('trackselect6', self.track_select_6),
                                  ('trackselect5', self.track_select_5)]:
            if hasattr(self, ts_name):
                btn = getattr(self, ts_name)
                if btn is not None:
                    try:
                        btn.send_value(0)
                        btn.remove_value_listener(listener)
                        btn.set_enabled(False)
                        btn.disconnect()
                    except Exception:
                        pass
                    setattr(self, ts_name, None)

        self._session._unlink()
        self._session = None
        self.mode_1_to_2.remove_value_listener(self._activate_mode2)
        self._teardown_loop_controls()
        self.mode_1_to_2 = None
        return

    def _mode1_devices(self):
        device_number = 0
        if len(self.mixer.selected_strip()._track.devices) > device_number:
            devices = self.mixer.selected_strip()._track.devices
            self.actual_device = devices[device_number]
            self.device_tracktype_selected__chain_number_1 = DeviceComponent()
            # Los 6 knobs de EQ del centro (CC 4/3/2 de cada deck) quedan LIBRES para mapeo
            # manual. Solo los dos FILTER (CC 1) controlan macros: el 4 (izq) y el 8 (der).
            device_controls = (
             None,
             None,
             None,
             EncoderElement(MIDI_CC_TYPE, 1, 1, _map_modes.absolute),
             None,
             None,
             None,
             EncoderElement(MIDI_CC_TYPE, 2, 1, _map_modes.absolute))
            self.device_tracktype_selected__chain_number_1.set_device(self.actual_device)
            self.device_tracktype_selected__chain_number_1.set_parameter_controls(tuple(device_controls))
            self.device_tracktype_selected__chain_number_1.set_lock_to_device('lock', self.actual_device)
        return

    def _remove_mode1_devices(self):
        device_number = 0
        if hasattr(self, 'device_tracktype_selected__chain_number_1'):
            device_controls = (None, None, None, None, None, None, None, None)
            self.device_tracktype_selected__chain_number_1.set_parameter_controls(tuple(device_controls))
            self.device_tracktype_selected__chain_number_1.set_lock_to_device('', self.actual_device)
            self.device_tracktype_selected__chain_number_1.set_device(None)
        return

    def _mode0(self):
        global direction_tempo_control_updown_mode0
        global direction_tempo_fine_control_updown_mode0
        global lv_tempo_control_updown_mode0
        global lv_tempo_fine_control_updown_mode0
        self.show_message('_mode0 is active')
        self.mixer.set_crossfader_control(EncoderElement(MIDI_CC_TYPE, 0, 1, _map_modes.absolute))
        self.mixer.channel_strip(0).set_volume_control(CappedEncoderElement(MIDI_CC_TYPE, 1, 6, _map_modes.absolute))
        self.mixer.channel_strip(1).set_volume_control(CappedEncoderElement(MIDI_CC_TYPE, 1, 7, _map_modes.absolute))
        self.mixer.channel_strip(2).set_volume_control(CappedEncoderElement(MIDI_CC_TYPE, 1, 8, _map_modes.absolute))
        self.mixer.channel_strip(3).set_volume_control(CappedEncoderElement(MIDI_CC_TYPE, 1, 9, _map_modes.absolute))
        self.mixer.channel_strip(4).set_volume_control(CappedEncoderElement(MIDI_CC_TYPE, 2, 6, _map_modes.absolute))
        self.mixer.channel_strip(5).set_volume_control(CappedEncoderElement(MIDI_CC_TYPE, 2, 7, _map_modes.absolute))
        self.mixer.channel_strip(6).set_volume_control(CappedEncoderElement(MIDI_CC_TYPE, 2, 8, _map_modes.absolute))
        self.mixer.master_strip().set_volume_control(CappedEncoderElement(MIDI_CC_TYPE, 2, 9, _map_modes.absolute))
        self.arm_specific_0 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 1, 52)
        self.arm_specific_0.set_on_off_values(125, 1)
        self.mixer.channel_strip(0).set_arm_button(self.arm_specific_0)
        self.arm_specific_1 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 1, 53)
        self.arm_specific_1.set_on_off_values(125, 1)
        self.mixer.channel_strip(1).set_arm_button(self.arm_specific_1)
        self.arm_specific_2 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 1, 54)
        self.arm_specific_2.set_on_off_values(125, 1)
        self.mixer.channel_strip(2).set_arm_button(self.arm_specific_2)
        self.arm_specific_3 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 1, 55)
        self.arm_specific_3.set_on_off_values(125, 1)
        self.mixer.channel_strip(3).set_arm_button(self.arm_specific_3)
        self.solo_specific_0 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 1, 56)
        self.solo_specific_0.set_on_off_values(126, 41)
        self.mixer.channel_strip(0).set_solo_button(self.solo_specific_0)
        self.solo_specific_1 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 1, 57)
        self.solo_specific_1.set_on_off_values(126, 41)
        self.mixer.channel_strip(1).set_solo_button(self.solo_specific_1)
        self.solo_specific_2 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 1, 58)
        self.solo_specific_2.set_on_off_values(126, 41)
        self.mixer.channel_strip(2).set_solo_button(self.solo_specific_2)
        self.solo_specific_3 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 1, 59)
        self.solo_specific_3.set_on_off_values(126, 41)
        self.mixer.channel_strip(3).set_solo_button(self.solo_specific_3)
        self.mute_specific_0 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 1, 60)
        self.mute_specific_0.set_on_off_values(127, 81)
        self.mixer.channel_strip(0).set_mute_button(self.mute_specific_0)
        self.mixer.channel_strip(0).set_invert_mute_feedback(True)
        self.mute_specific_1 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 1, 61)
        self.mute_specific_1.set_on_off_values(127, 81)
        self.mixer.channel_strip(1).set_mute_button(self.mute_specific_1)
        self.mixer.channel_strip(1).set_invert_mute_feedback(True)
        self.mute_specific_2 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 1, 62)
        self.mute_specific_2.set_on_off_values(127, 81)
        self.mixer.channel_strip(2).set_mute_button(self.mute_specific_2)
        self.mixer.channel_strip(2).set_invert_mute_feedback(True)
        self.mute_specific_3 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 1, 63)
        self.mute_specific_3.set_on_off_values(127, 81)
        self.mixer.channel_strip(3).set_mute_button(self.mute_specific_3)
        self.mixer.channel_strip(3).set_invert_mute_feedback(True)
        self.trackselect4 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 1, 67)
        self.trackselect4.set_on_off_values(127, 81)
        self.trackselect4.add_value_listener(self.track_select_4, identify_sender=False)
        self.trackselect3 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 1, 66)
        self.trackselect3.set_on_off_values(127, 81)
        self.trackselect3.add_value_listener(self.track_select_3, identify_sender=False)
        self.trackselect2 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 1, 65)
        self.trackselect2.set_on_off_values(127, 81)
        self.trackselect2.add_value_listener(self.track_select_2, identify_sender=False)
        self.trackselect1 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 1, 64)
        self.trackselect1.set_on_off_values(127, 81)
        self.trackselect1.add_value_listener(self.track_select_1, identify_sender=False)
        self.transport = TransportComponent()
        self.transport.name = 'Transport'
        lv_tempo_fine_control_updown_mode0 = 0
        direction_tempo_fine_control_updown_mode0 = 'not set'
        self.tempo_fine_control_updown_encoder = EncoderElement(MIDI_CC_TYPE, 4, 10, _map_modes.relative_smooth_two_compliment)
        self.tempo_fine_control_updown_encoder.add_value_listener(self.tempo_fine_control_updown_mode0, identify_sender=False)
        lv_tempo_control_updown_mode0 = 0
        direction_tempo_control_updown_mode0 = 'not set'
        self.tempo_control_updown_encoder = EncoderElement(MIDI_CC_TYPE, 1, 10, _map_modes.relative_smooth_two_compliment)
        self.tempo_control_updown_encoder.add_value_listener(self.tempo_control_updown_mode0, identify_sender=False)
        metronome_button = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, CH_DECK_A, 1)
        metronome_button.name = 'metronome_button'
        self.transport.set_metronome_button(metronome_button)
        # --- New Utility Buttons ---
        self.left_shift_btn = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 1, 7)
        self.left_shift_btn.set_on_off_values(127, 0)
        self.left_shift_btn.send_value(0) # Apagar luz al inicio
        if not self.left_shift_btn.value_has_listener(self._do_toggle_session_view):
            self.left_shift_btn.add_value_listener(self._do_toggle_session_view, identify_sender=False)

        self.right_play_btn = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 2, 10)
        self.right_play_btn.set_on_off_values(127, 0)
        self.right_play_btn.name = 'play_button'
        self.transport.set_play_button(self.right_play_btn)
        
        self.left_play_btn = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 1, 10)
        self.left_play_btn.set_on_off_values(127, 0)
        if not self.left_play_btn.value_has_listener(self._do_locator):
            self.left_play_btn.add_value_listener(self._do_locator, identify_sender=False)

        self.left_cue_btn = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 1, 9)
        self.left_cue_btn.set_on_off_values(127, 0)
        if not self.left_cue_btn.value_has_listener(self._do_undo):
            self.left_cue_btn.add_value_listener(self._do_undo, identify_sender=False)
            
        stop_button = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 2, 9)
        stop_button.set_on_off_values(127, 0)
        stop_button.name = 'stop_button'
        self.transport.set_stop_button(stop_button)

        # Right Sync -> Tap Tempo
        self.right_sync_1 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 2, 8)
        self.right_sync_2 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 2, 11)
        self.right_sync_3 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 2, 12)
        self.transport.set_tap_tempo_button(self.right_sync_1)
        if not self.right_sync_2.value_has_listener(self._do_tap_tempo):
            self.right_sync_2.add_value_listener(self._do_tap_tempo, identify_sender=False)
        if not self.right_sync_3.value_has_listener(self._do_tap_tempo):
            self.right_sync_3.add_value_listener(self._do_tap_tempo, identify_sender=False)

        # Left Sync -> Redo
        self.left_sync_1 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 1, 8)
        self.left_sync_2 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 1, 11)
        self.left_sync_3 = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 1, 12)
        if not self.left_sync_1.value_has_listener(self._do_redo):
            self.left_sync_1.add_value_listener(self._do_redo, identify_sender=False)
        if not self.left_sync_2.value_has_listener(self._do_redo):
            self.left_sync_2.add_value_listener(self._do_redo, identify_sender=False)
        if not self.left_sync_3.value_has_listener(self._do_redo):
            self.left_sync_3.add_value_listener(self._do_redo, identify_sender=False)
        

        # ---------------------------
        record_button = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 0, 2)
        record_button.set_on_off_values(127, 0)
        record_button.name = 'record_button'
        self.transport.set_record_button(record_button)
        overdub_button = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 0, 3)
        overdub_button.set_on_off_values(127, 0)
        overdub_button.name = 'overdub_button'
        self.transport.set_overdub_button(overdub_button)
        self.trackleft = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 1, 15)
        self.trackleft.add_value_listener(self._trackleft_track_nav, identify_sender=False)
        self.trackright = ConfigurableButtonElement(1, MIDI_NOTE_TYPE, 2, 15)
        self.trackright.add_value_listener(self._trackright_track_nav, identify_sender=False)
        return

    def _remove_mode0(self):
        self.mixer.set_crossfader_control(None)
        self.mixer.channel_strip(0).set_volume_control(None)
        self.mixer.channel_strip(1).set_volume_control(None)
        self.mixer.channel_strip(2).set_volume_control(None)
        self.mixer.channel_strip(3).set_volume_control(None)
        self.mixer.channel_strip(4).set_volume_control(None)
        self.mixer.channel_strip(5).set_volume_control(None)
        self.mixer.channel_strip(6).set_volume_control(None)
        self.mixer.master_strip().set_volume_control(None)
        self.mixer.channel_strip(0).set_arm_button(None)
        self.mixer.channel_strip(1).set_arm_button(None)
        self.mixer.channel_strip(2).set_arm_button(None)
        self.mixer.channel_strip(3).set_arm_button(None)
        self.mixer.channel_strip(0).set_solo_button(None)
        self.mixer.channel_strip(1).set_solo_button(None)
        self.mixer.channel_strip(2).set_solo_button(None)
        self.mixer.channel_strip(3).set_solo_button(None)
        self.mixer.channel_strip(0).set_mute_button(None)
        self.mixer.channel_strip(1).set_mute_button(None)
        self.mixer.channel_strip(2).set_mute_button(None)
        self.mixer.channel_strip(3).set_mute_button(None)
        self.trackselect4.send_value(0)
        self.trackselect4.remove_value_listener(self.track_select_4)
        self.trackselect4 = None
        self.trackselect3.send_value(0)
        self.trackselect3.remove_value_listener(self.track_select_3)
        self.trackselect3 = None
        self.trackselect2.send_value(0)
        self.trackselect2.remove_value_listener(self.track_select_2)
        self.trackselect2 = None
        self.trackselect1.send_value(0)
        self.trackselect1.remove_value_listener(self.track_select_1)
        self.trackselect1 = None
        self.tempo_fine_control_updown_encoder.remove_value_listener(self.tempo_fine_control_updown_mode0)
        self.tempo_fine_control_updown_encoder = None
        self.tempo_control_updown_encoder.remove_value_listener(self.tempo_control_updown_mode0)
        self.tempo_control_updown_encoder = None
        self.transport.set_tempo_fine_control(None)
        self.transport.set_tempo_control(None)
        self.transport.set_metronome_button(None)
        self.transport.set_play_button(None)
        self.transport.set_stop_button(None)
        self.transport.set_record_button(None)
        self.transport.set_overdub_button(None)
        self.transport = None
        self.trackleft.remove_value_listener(self._trackleft_track_nav)
        self.trackleft = None
        self.trackright.remove_value_listener(self._trackright_track_nav)
        self.trackright = None
        return

    def add_device_listeners(self):
        for track in self.song().tracks:
            view = track.view
            if not view.selected_device_has_listener(self._reload_active_devices):
                view.add_selected_device_listener(self._reload_active_devices)
        return

    def remove_device_listeners(self):
        # Las pistas creadas con el modo activo no tienen listener: remover sin guard lanza RuntimeError
        for track in self.song().tracks:
            view = track.view
            if view.selected_device_has_listener(self._reload_active_devices):
                view.remove_selected_device_listener(self._reload_active_devices)
        return

    def _reload_active_devices(self, value=None):
        # Puede llegar desde listeners crudos de Live (fuera del guard); el guard es reentrante
        with self.component_guard():
            self._remove_active_devices()
            self._set_active_devices()
            if hasattr(self, '_turn_on_device_select_leds'):
                self._turn_off_device_select_leds()
                self._turn_on_device_select_leds()
            if hasattr(self, '_all_prev_device_leds'):
                self._all_prev_device_leds()
            if hasattr(self, '_all_nxt_device_leds'):
                self._all_nxt_device_leds()
        return

    def _set_active_devices(self):
        if active_mode == '_mode2' and hasattr(self, '_mode2_devices'):
            self._mode2_devices()
        elif active_mode == '_mode1' and hasattr(self, '_mode1_devices'):
            self._mode1_devices()
        elif active_mode == '_mode0' and hasattr(self, '_mode0_devices'):
            self._mode0_devices()
        return

    def _remove_active_devices(self):
        if active_mode == '_mode2' and hasattr(self, '_mode2_devices'):
            self._remove_mode2_devices()
        elif active_mode == '_mode1' and hasattr(self, '_mode1_devices'):
            self._remove_mode1_devices()
        elif active_mode == '_mode0' and hasattr(self, '_mode0_devices'):
            self._remove_mode0_devices()
        return

    def _set_track_select_led(self):
        self._turn_off_track_select_leds()
        offset = 0
        if getattr(self, '_session', None) is not None:
            offset = self._session._track_offset
        num_of_tracks = len(self.song().tracks)
        pos = offset + 6
        pos2 = pos + 1
        if num_of_tracks >= pos2:
            if self.song().view.selected_track == self.song().tracks[pos]:
                if hasattr(self, 'trackselect7') and self.trackselect7 is not None:
                    self.trackselect7.send_value(127)
        pos = offset + 5
        pos2 = pos + 1
        if num_of_tracks >= pos2:
            if self.song().view.selected_track == self.song().tracks[pos]:
                if hasattr(self, 'trackselect6') and self.trackselect6 is not None:
                    self.trackselect6.send_value(127)
        pos = offset + 4
        pos2 = pos + 1
        if num_of_tracks >= pos2:
            if self.song().view.selected_track == self.song().tracks[pos]:
                if hasattr(self, 'trackselect5') and self.trackselect5 is not None:
                    self.trackselect5.send_value(127)
        pos = offset + 3
        pos2 = pos + 1
        if num_of_tracks >= pos2:
            if self.song().view.selected_track == self.song().tracks[pos]:
                if hasattr(self, 'trackselect4') and self.trackselect4 is not None:
                    self.trackselect4.send_value(127)
        pos = offset + 2
        pos2 = pos + 1
        if num_of_tracks >= pos2:
            if self.song().view.selected_track == self.song().tracks[pos]:
                if hasattr(self, 'trackselect3') and self.trackselect3 is not None:
                    self.trackselect3.send_value(127)
        pos = offset + 1
        pos2 = pos + 1
        if num_of_tracks >= pos2:
            if self.song().view.selected_track == self.song().tracks[pos]:
                if hasattr(self, 'trackselect2') and self.trackselect2 is not None:
                    self.trackselect2.send_value(127)
        pos = offset + 0
        pos2 = pos + 1
        if num_of_tracks >= pos2:
            if self.song().view.selected_track == self.song().tracks[pos]:
                if hasattr(self, 'trackselect1') and self.trackselect1 is not None:
                    self.trackselect1.send_value(127)
        return

    def _turn_off_track_select_leds(self):
        num_of_tracks = len(self.song().tracks)
        offset = 0
        if getattr(self, '_session', None) is not None:
            offset = self._session._track_offset
        pos = offset + 6
        pos2 = pos + 1
        if num_of_tracks >= pos2 and hasattr(self, 'trackselect7') and self.trackselect7 is not None:
            self.trackselect7.send_value(81)
        elif num_of_tracks < pos2 and hasattr(self, 'trackselect7') and self.trackselect7 is not None:
            self.trackselect7.send_value(0)
        pos = offset + 5
        pos2 = pos + 1
        if num_of_tracks >= pos2 and hasattr(self, 'trackselect6') and self.trackselect6 is not None:
            self.trackselect6.send_value(81)
        elif num_of_tracks < pos2 and hasattr(self, 'trackselect6') and self.trackselect6 is not None:
            self.trackselect6.send_value(0)
        pos = offset + 4
        pos2 = pos + 1
        if num_of_tracks >= pos2 and hasattr(self, 'trackselect5') and self.trackselect5 is not None:
            self.trackselect5.send_value(81)
        elif num_of_tracks < pos2 and hasattr(self, 'trackselect5') and self.trackselect5 is not None:
            self.trackselect5.send_value(0)
        pos = offset + 3
        pos2 = pos + 1
        if num_of_tracks >= pos2 and hasattr(self, 'trackselect4') and self.trackselect4 is not None:
            self.trackselect4.send_value(81)
        elif num_of_tracks < pos2 and hasattr(self, 'trackselect4') and self.trackselect4 is not None:
            self.trackselect4.send_value(0)
        pos = offset + 2
        pos2 = pos + 1
        if num_of_tracks >= pos2 and hasattr(self, 'trackselect3') and self.trackselect3 is not None:
            self.trackselect3.send_value(81)
        elif num_of_tracks < pos2 and hasattr(self, 'trackselect3') and self.trackselect3 is not None:
            self.trackselect3.send_value(0)
        pos = offset + 1
        pos2 = pos + 1
        if num_of_tracks >= pos2 and hasattr(self, 'trackselect2') and self.trackselect2 is not None:
            self.trackselect2.send_value(81)
        elif num_of_tracks < pos2 and hasattr(self, 'trackselect2') and self.trackselect2 is not None:
            self.trackselect2.send_value(0)
        pos = offset + 0
        pos2 = pos + 1
        if num_of_tracks >= pos2 and hasattr(self, 'trackselect1') and self.trackselect1 is not None:
            self.trackselect1.send_value(81)
        elif num_of_tracks < pos2 and hasattr(self, 'trackselect1') and self.trackselect1 is not None:
            self.trackselect1.send_value(0)
        return

    def track_select_7(self, value):
        if value > 0:
            if getattr(self, '_session', None) is not None:
                move = self._session._track_offset + 7
            else:
                move = 7
            num_of_tracks = len(self.song().tracks)
            if num_of_tracks >= move:
                move = move - 1
                self.song().view.selected_track = self.song().tracks[move]
        return

    def track_select_6(self, value):
        if value > 0:
            if getattr(self, '_session', None) is not None:
                move = self._session._track_offset + 6
            else:
                move = 6
            num_of_tracks = len(self.song().tracks)
            if num_of_tracks >= move:
                move = move - 1
                self.song().view.selected_track = self.song().tracks[move]
        return

    def track_select_5(self, value):
        if value > 0:
            if getattr(self, '_session', None) is not None:
                move = self._session._track_offset + 5
            else:
                move = 5
            num_of_tracks = len(self.song().tracks)
            if num_of_tracks >= move:
                move = move - 1
                self.song().view.selected_track = self.song().tracks[move]
        return

    def track_select_4(self, value):
        if value > 0:
            if getattr(self, '_session', None) is not None:
                move = self._session._track_offset + 4
            else:
                move = 4
            num_of_tracks = len(self.song().tracks)
            if num_of_tracks >= move:
                move = move - 1
                self.song().view.selected_track = self.song().tracks[move]
        return

    def track_select_3(self, value):
        if value > 0:
            if getattr(self, '_session', None) is not None:
                move = self._session._track_offset + 3
            else:
                move = 3
            num_of_tracks = len(self.song().tracks)
            if num_of_tracks >= move:
                move = move - 1
                self.song().view.selected_track = self.song().tracks[move]
        return

    def track_select_2(self, value):
        if value > 0:
            if getattr(self, '_session', None) is not None:
                move = self._session._track_offset + 2
            else:
                move = 2
            num_of_tracks = len(self.song().tracks)
            if num_of_tracks >= move:
                move = move - 1
                self.song().view.selected_track = self.song().tracks[move]
        return

    def track_select_1(self, value):
        if value > 0:
            if getattr(self, '_session', None) is not None:
                move = self._session._track_offset + 1
            else:
                move = 1
            num_of_tracks = len(self.song().tracks)
            if num_of_tracks >= move:
                move = move - 1
                self.song().view.selected_track = self.song().tracks[move]
        return

    def tempo_fine_control_updown_mode0(self, value):
        global direction_tempo_fine_control_updown_mode0
        global lv_tempo_fine_control_updown_mode0
        if value == lv_tempo_fine_control_updown_mode0 and lv_tempo_fine_control_updown_mode0 != 0:
            if direction_tempo_fine_control_updown_mode0 == 'up':
                self._tempo_fine_control_up_value_mode0(1)
            elif direction_tempo_fine_control_updown_mode0 == 'down':
                self._tempo_fine_control_down_value_mode0(1)
            else:
                self._tempo_fine_control_up_value_mode0(1)
        elif value > lv_tempo_fine_control_updown_mode0 and lv_tempo_fine_control_updown_mode0 != 0:
            self._tempo_fine_control_down_value_mode0(1)
            direction_tempo_fine_control_updown_mode0 = 'down'
        elif value < lv_tempo_fine_control_updown_mode0 and lv_tempo_fine_control_updown_mode0 != 0:
            self._tempo_fine_control_up_value_mode0(1)
            direction_tempo_fine_control_updown_mode0 = 'up'
        lv_tempo_fine_control_updown_mode0 = value
        return

    def _tempo_fine_control_up_value_mode0(self, value):
        if value:
            if self.song().tempo < 999:
                self.song().tempo = self.song().tempo + 0.1
        return

    def _tempo_fine_control_down_value_mode0(self, value):
        if value:
            if self.song().tempo > 20:
                self.song().tempo = self.song().tempo - 0.1
        return

    def tempo_control_updown_mode0(self, value):
        global direction_tempo_control_updown_mode0
        global lv_tempo_control_updown_mode0
        if value == lv_tempo_control_updown_mode0 and lv_tempo_control_updown_mode0 != 0:
            if direction_tempo_control_updown_mode0 == 'up':
                self._tempo_control_up_value_mode0(1)
            elif direction_tempo_control_updown_mode0 == 'down':
                self._tempo_control_down_value_mode0(1)
            else:
                self._tempo_control_up_value_mode0(1)
        elif value > lv_tempo_control_updown_mode0 and lv_tempo_control_updown_mode0 != 0:
            self._tempo_control_down_value_mode0(1)
            direction_tempo_control_updown_mode0 = 'down'
        elif value < lv_tempo_control_updown_mode0 and lv_tempo_control_updown_mode0 != 0:
            self._tempo_control_up_value_mode0(1)
            direction_tempo_control_updown_mode0 = 'up'
        lv_tempo_control_updown_mode0 = value
        return

    def _tempo_control_up_value_mode0(self, value):
        if value:
            if self.song().tempo < 999:
                self.song().tempo = self.song().tempo + 1
        return

    def _tempo_control_down_value_mode0(self, value):
        if value:
            if self.song().tempo > 22:
                self.song().tempo = self.song().tempo - 1
        return

    def _on_session_offset_changed(self):
        if getattr(self, '_session', None) is None:
            return
        with self.component_guard():
            self.current_track_offset = self._session._track_offset
            self.current_scene_offset = self._session._scene_offset
            if getattr(self, 'mixer', None) is not None:
                self.mixer.set_track_offset(self._session._track_offset)
            self._set_track_select_led()

    def _ensure_track_in_view(self, track_index):
        if getattr(self, '_session', None) is not None:
            num_tracks = self._session.width() if hasattr(self._session, 'width') else 7
            current_offset = self._session._track_offset
            if track_index < current_offset:
                self._session.set_offsets(track_index, self._session._scene_offset)
            elif track_index >= current_offset + num_tracks:
                self._session.set_offsets(track_index - num_tracks + 1, self._session._scene_offset)

    def _trackleft_track_nav(self, value):
        if value > 0:
            track_idx = self.selected_track_idx() - 1
            if track_idx > 0:
                new_idx = track_idx - 1
                self.song().view.selected_track = self.song().tracks[new_idx]
                self._ensure_track_in_view(new_idx)
        return

    def _trackright_track_nav(self, value):
        if value > 0:
            track_idx = self.selected_track_idx() - 1
            if track_idx < 0:
                return
            num_of_tracks = len(self.song().tracks)
            if track_idx + 1 < num_of_tracks:
                new_idx = track_idx + 1
                self.song().view.selected_track = self.song().tracks[new_idx]
                self._ensure_track_in_view(new_idx)
        return

    def _on_selected_track_changed(self):
        ControlSurface._on_selected_track_changed(self)
        self._display_reset_delay = 0
        value = 'selected track changed'
        if hasattr(self, '_set_track_select_led'):
            self._set_track_select_led()
        if hasattr(self, '_reload_active_devices'):
            self._reload_active_devices(value)
        if hasattr(self, 'update_all_ab_select_LEDs'):
            self.update_all_ab_select_LEDs(1)
        return

    def _is_prev_device_on_or_off(self):
        self._device = self.song().view.selected_track.view.selected_device
        self._device_position = self.selected_device_idx()
        if self._device is None or self._device_position == 0:
            on_off = 'off'
        else:
            on_off = 'on'
        return on_off

    def _is_nxt_device_on_or_off(self):
        self._selected_device = self.selected_device_idx() + 1
        if self._device is None or self._selected_device == len(self.song().view.selected_track.devices):
            on_off = 'off'
        else:
            on_off = 'on'
        return on_off

    def _set_active_mode(self):
        if active_mode == '_mode2':
            self._mode2()
        elif active_mode == '_mode1':
            self._mode1()
        elif active_mode == '_mode0':
            self._mode0()
        if hasattr(self, '_set_track_select_led'):
            self._set_track_select_led()
        if hasattr(self, '_turn_on_device_select_leds'):
            self._turn_off_device_select_leds()
            self._turn_on_device_select_leds()
        if hasattr(self, '_all_prev_device_leds'):
            self._all_prev_device_leds()
        if hasattr(self, '_all_nxt_device_leds'):
            self._all_nxt_device_leds()
        if hasattr(self, 'update_all_ab_select_LEDs'):
            self.update_all_ab_select_LEDs(1)
        return

    def _remove_active_mode(self):
        if active_mode == '_mode2':
            self._remove_mode2()
        elif active_mode == '_mode1':
            self._remove_mode1()
        elif active_mode == '_mode0':
            self._remove_mode0()
        return

    def _activate_mode2(self, value):
        global active_mode
        global shift_previous_is_active
        if value > 0:
            shift_previous_is_active = 'off'
            self._remove_active_mode()
            active_mode = '_mode2'
            self._set_active_mode()
        return

    def _activate_mode1(self, value):
        global active_mode
        global shift_previous_is_active
        if value > 0:
            shift_previous_is_active = 'off'
            self._remove_active_mode()
            active_mode = '_mode1'
            self._set_active_mode()
        return

    def _activate_mode0(self, value):
        global active_mode
        global shift_previous_is_active
        if value > 0:
            shift_previous_is_active = 'off'
            self._remove_active_mode()
            active_mode = '_mode0'
            self._set_active_mode()
        return

    def _activate_shift_mode2(self, value):
        global active_mode
        global previous_shift_mode2
        global shift_previous_is_active
        if value > 0:
            shift_previous_is_active = 'on'
            previous_shift_mode2 = active_mode
            self._remove_active_mode()
            active_mode = '_mode2'
            self._set_active_mode()
        elif shift_previous_is_active == 'on':
            try:
                previous_shift_mode2
            except NameError:
                self.log_message('previous shift mode not defined yet')
            else:
                self._remove_active_mode()
                active_mode = previous_shift_mode2
                self._set_active_mode()

        return

    def _activate_shift_mode1(self, value):
        global active_mode
        global previous_shift_mode1
        global shift_previous_is_active
        if value > 0:
            shift_previous_is_active = 'on'
            previous_shift_mode1 = active_mode
            self._remove_active_mode()
            active_mode = '_mode1'
            self._set_active_mode()
        elif shift_previous_is_active == 'on':
            try:
                previous_shift_mode1
            except NameError:
                self.log_message('previous shift mode not defined yet')
            else:
                self._remove_active_mode()
                active_mode = previous_shift_mode1
                self._set_active_mode()

        return

    def _activate_shift_mode0(self, value):
        global active_mode
        global previous_shift_mode0
        global shift_previous_is_active
        if value > 0:
            shift_previous_is_active = 'on'
            previous_shift_mode0 = active_mode
            self._remove_active_mode()
            active_mode = '_mode0'
            self._set_active_mode()
        elif shift_previous_is_active == 'on':
            try:
                previous_shift_mode0
            except NameError:
                self.log_message('previous shift mode not defined yet')
            else:
                self._remove_active_mode()
                active_mode = previous_shift_mode0
                self._set_active_mode()

        return

    def selected_device_idx(self):
        self._device = self.song().view.selected_track.view.selected_device
        return self.tuple_index(self.song().view.selected_track.devices, self._device)

    def selected_track_idx(self):
        # 1-based; devuelve 0 si la pista seleccionada es un return o el master
        self._track = self.song().view.selected_track
        self._track_num = self.tuple_index(self.song().tracks, self._track) + 1
        return self._track_num

    def tuple_index(self, tuple, obj):
        for i in range(0, len(tuple)):
            if tuple[i] == obj:
                return i

        return -1

    def _passthrough_notes(self):
        """(canal, nota) que deben llegar a la pista armada en el modo activo.
        Todo lo demas lo captura el script para que ningun boton dispare notas."""
        keys = set()
        # Unica excepcion: en Modo 2 el deck derecho es un teclado cromatico.
        # En Modo 1 no pasa ninguna nota (HOTCUE incluido).
        if active_mode == '_mode2':
            # Deck derecho libre: SAMPLER + SLICER + LOOP + HOTCUE = 64 notas cromaticas desde C1
            for note in range(PAD_SAMPLER, PAD_END):
                keys.add((CH_DECK_B, note))
        return keys

    def _note_elements(self):
        # Live 12 expone la lista como self.controls; versiones viejas como self._controls
        controls = getattr(self, 'controls', None) or getattr(self, '_controls', None) or []
        for control in controls:
            if not isinstance(control, InputControlElement):
                continue
            try:
                if control.message_type() != MIDI_NOTE_TYPE:
                    continue
                key = (control.message_channel(), control.message_identifier())
            except Exception:
                continue
            yield control, key

    def build_midi_map(self, midi_map_handle):
        passthrough = self._passthrough_notes()
        # Los elementos viejos de un modo anterior siguen registrados en la superficie y
        # volverian a capturar sus notas: se les apaga el forwarding si la nota debe pasar.
        for control, key in self._note_elements():
            # Un ButtonElement desconectado queda con _undo_step_handler = None y revienta
            # en receive_value si vuelve a recibir MIDI: nunca forwardear esos.
            disconnected = getattr(control, '_undo_step_handler', 1) is None
            if key in passthrough or disconnected:
                control.suppress_script_forwarding = True
                control.script_wants_forwarding = lambda: False
        super(hercules_p32_dj, self).build_midi_map(midi_map_handle)
        # Notas que ya tienen dueño: se leen del registro real de forwarding del framework
        # (claves (status, nota)), no de una lista propia que puede quedar vacia.
        owned = set()
        registry = getattr(self, '_forwarding_registry', None)
        if registry:
            for fkey in list(registry.keys()):
                try:
                    status, ident = fkey[0], fkey[1]
                except Exception:
                    continue
                if (status & 0xF0) in (0x80, 0x90):
                    owned.add((status & 0x0F, ident))
        else:
            for control, key in self._note_elements():
                try:
                    if control.script_wants_forwarding():
                        owned.add(key)
                except Exception:
                    pass
        # Swallow global: cualquier nota que no sea de un elemento activo ni deba pasar a la pista
        handle = self._c_instance.handle()
        swallowed = set()
        for ch in range(16):
            for note in range(128):
                key = (ch, note)
                if key in passthrough or key in owned:
                    continue
                Live.MidiMap.forward_midi_note(handle, midi_map_handle, ch, note)
                swallowed.add(key)
        self._swallowed_notes = swallowed
        # Teclado del Modo 2: forwarding NO exclusivo (should_consume_event=False). La pista
        # recibe la nota y el script una copia, solo para el feedback de luces.
        reported = set()
        if active_mode == '_mode2':
            for ch, note in self._keyboard_notes():
                if (ch, note) not in passthrough:
                    continue
                try:
                    Live.MidiMap.forward_midi_note(handle, midi_map_handle, ch, note, False)
                    reported.add((ch, note))
                except TypeError:
                    # Version de Live sin should_consume_event: sin feedback, la nota pasa igual
                    break
        self._reported_notes = reported
        if DEBUG_LOG_MIDI:
            self._log_cc_registry()

    def _log_cc_registry(self):
        registry = getattr(self, '_forwarding_registry', None) or {}
        lines = []
        for fkey in sorted(registry.keys()):
            try:
                status, ident = fkey[0], fkey[1]
            except Exception:
                continue
            if (status & 0xF0) != 0xB0:
                continue
            control = registry[fkey]
            try:
                info = '%s listeners=%s param=%s' % (
                    type(control).__name__,
                    getattr(control, '_input_signal_listener_count', '?'),
                    getattr(control, '_capped_parameter', None) is not None)
            except Exception as e:
                info = 'err %s' % e
            lines.append('CC ch%d #%d -> %s' % (status & 0x0F, ident, info))
        self.log_message('P32 CC map (%s): %s' % (active_mode, ' | '.join(lines)))

    def receive_midi(self, midi_bytes):
        if DEBUG_LOG_MIDI:
            self.log_message('P32 MIDI in: %s' % (midi_bytes,))
        if len(midi_bytes) == 3 and (midi_bytes[0] & 0xF0) in (0x80, 0x90):
            status, note, velocity = midi_bytes
            key = (status & 0x0F, note)
            if key in getattr(self, '_reported_notes', ()):
                # Copia de una nota del teclado del Modo 2: solo feedback de luz
                pressed = (status & 0xF0) == 0x90 and velocity > 0
                self._send_raw(0x90 | key[0], note, self._keyboard_led_value(note, pressed))
                return
            # Solo se descarta una nota si ningun elemento del script la espera
            finder = getattr(self, 'get_recipient_for_nonsysex_midi_message', None)
            if finder is not None:
                try:
                    if finder(midi_bytes) is None:
                        return
                except Exception:
                    pass
            else:
                key = (midi_bytes[0] & 0x0F, midi_bytes[1])
                if key in getattr(self, '_swallowed_notes', ()):
                    return
        super(hercules_p32_dj, self).receive_midi(midi_bytes)

    def disconnect(self):
        # Sin esto los listeners crudos de Live (selected_device) quedan colgados al cambiar de superficie
        for step in (self._remove_active_mode, self._remove_mode0, self.remove_device_listeners):
            try:
                step()
            except Exception as e:
                self.log_message('disconnect: %s failed: %s' % (getattr(step, '__name__', step), e))
        super(hercules_p32_dj, self).disconnect()
        return
