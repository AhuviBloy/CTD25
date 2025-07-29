"""
Sound Manager - מנהל צלילים למשחק
מנגן צלילים נעימים לפתיחת משחק, סיום משחק, תזוזות ולכידות
"""
import pygame
import numpy as np
import threading
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class SoundManager:
    """
    Manages all game sounds - pleasant tones for game events
    מנהל כל הצלילים של המשחק - צלילים נעימים לאירועי המשחק
    """
    
    def __init__(self):
        self.initialized = False
        self.sounds = {}
        self.volume = 0.7  # Default volume level
        
        try:
            # Initialize pygame mixer for sound
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            self.initialized = True
            
            # Generate pleasant sounds
            self._generate_sounds()
            
            logger.info("SoundManager initialized successfully")
            
        except Exception as e:
            logger.warning(f"Could not initialize sound system: {e}")
            self.initialized = False
    
    def _generate_sounds(self):
        """Generate pleasant musical sounds using sine waves"""
        try:
            sample_rate = 22050
            
            # Game Start Sound - Ascending major chord (C-E-G)
            self.sounds['game_start'] = self._create_chord_sound(
                [261.63, 329.63, 392.00],  # C4, E4, G4
                duration=1.0,
                sample_rate=sample_rate
            )
            
            # Game End Sound - Gentle descending melody
            self.sounds['game_end'] = self._create_melody_sound(
                [523.25, 493.88, 440.00, 392.00],  # C5, B4, A4, G4
                duration=0.3,
                sample_rate=sample_rate
            )
            
            # Victory Sound - Triumphant ascending melody
            self.sounds['victory'] = self._create_victory_fanfare(
                sample_rate=sample_rate
            )
            
            # Piece Move Sound - Soft click tone
            self.sounds['piece_move'] = self._create_soft_click(
                frequency=800,
                duration=0.15,
                sample_rate=sample_rate
            )
            
            # Piece Capture Sound - Success chime (perfect fifth)
            self.sounds['piece_capture'] = self._create_chord_sound(
                [523.25, 783.99],  # C5, G5
                duration=0.4,
                sample_rate=sample_rate
            )
            
            # Cursor Move Sound - Very subtle tick
            self.sounds['cursor_move'] = self._create_soft_click(
                frequency=600,
                duration=0.05,
                sample_rate=sample_rate
            )
            
            # Piece Jump Sound - Higher pitched whoosh
            self.sounds['piece_jump'] = self._create_chord_sound(
                [659.25, 987.77],  # E5, B5 
                duration=0.3,
                sample_rate=sample_rate
            )
            
            logger.info("Generated all game sounds")
            
        except Exception as e:
            logger.error(f"Error generating sounds: {e}")
    
    def _create_chord_sound(self, frequencies, duration=1.0, sample_rate=22050):
        """Create a harmonious chord sound"""
        frames = int(duration * sample_rate)
        arr = np.zeros(frames)
        
        for freq in frequencies:
            # Create sine wave for each frequency
            wave = np.sin(2 * np.pi * freq * np.linspace(0, duration, frames))
            # Apply gentle envelope to avoid clicks
            envelope = np.exp(-3 * np.linspace(0, 1, frames))
            arr += wave * envelope
        
        # Normalize and convert to pygame format
        arr = arr / len(frequencies)  # Average the frequencies
        arr = (arr * 32767 * self.volume).astype(np.int16)
        
        # Create stereo sound
        stereo_arr = np.zeros((frames, 2), dtype=np.int16)
        stereo_arr[:, 0] = arr  # Left channel
        stereo_arr[:, 1] = arr  # Right channel
        
        return pygame.sndarray.make_sound(stereo_arr)
    
    def _create_melody_sound(self, frequencies, duration=0.3, sample_rate=22050):
        """Create a melodic sequence of notes"""
        note_duration = duration
        total_frames = int(len(frequencies) * note_duration * sample_rate)
        arr = np.zeros(total_frames)
        
        for i, freq in enumerate(frequencies):
            start_frame = int(i * note_duration * sample_rate)
            end_frame = int((i + 1) * note_duration * sample_rate)
            frames = end_frame - start_frame
            
            # Create note with fade in/out
            wave = np.sin(2 * np.pi * freq * np.linspace(0, note_duration, frames))
            # Smooth envelope
            fade_frames = frames // 10
            envelope = np.ones(frames)
            envelope[:fade_frames] = np.linspace(0, 1, fade_frames)
            envelope[-fade_frames:] = np.linspace(1, 0, fade_frames)
            
            arr[start_frame:end_frame] = wave * envelope
        
        # Normalize and convert
        arr = (arr * 32767 * self.volume).astype(np.int16)
        
        # Create stereo
        stereo_arr = np.zeros((total_frames, 2), dtype=np.int16)
        stereo_arr[:, 0] = arr
        stereo_arr[:, 1] = arr
        
        return pygame.sndarray.make_sound(stereo_arr)
    
    def _create_soft_click(self, frequency=800, duration=0.15, sample_rate=22050):
        """Create a soft, pleasant click sound"""
        frames = int(duration * sample_rate)
        
        # Create a short burst with quick decay
        wave = np.sin(2 * np.pi * frequency * np.linspace(0, duration, frames))
        # Quick exponential decay for click effect
        envelope = np.exp(-15 * np.linspace(0, 1, frames))
        
        arr = wave * envelope
        arr = (arr * 32767 * self.volume * 0.5).astype(np.int16)  # Softer volume
        
        # Create stereo
        stereo_arr = np.zeros((frames, 2), dtype=np.int16)
        stereo_arr[:, 0] = arr
        stereo_arr[:, 1] = arr
        
        return pygame.sndarray.make_sound(stereo_arr)
    
    def _create_victory_fanfare(self, sample_rate=22050):
        """Create a triumphant victory fanfare"""
        # Victory melody: C-E-G-C (major chord arpeggio)
        victory_notes = [
            261.63,  # C4
            329.63,  # E4  
            392.00,  # G4
            523.25,  # C5
            523.25,  # C5 (hold)
        ]
        
        note_durations = [0.2, 0.2, 0.2, 0.4, 0.6]  # Longer final note
        total_duration = sum(note_durations)
        total_frames = int(total_duration * sample_rate)
        arr = np.zeros(total_frames)
        
        current_frame = 0
        for i, (freq, duration) in enumerate(zip(victory_notes, note_durations)):
            frames = int(duration * sample_rate)
            
            # Create note with gentle attack and decay
            wave = np.sin(2 * np.pi * freq * np.linspace(0, duration, frames))
            
            # Create envelope with attack, sustain, and decay
            attack_frames = frames // 10
            decay_frames = frames // 5
            
            envelope = np.ones(frames)
            # Attack (fade in)
            envelope[:attack_frames] = np.linspace(0, 1, attack_frames)
            # Decay (fade out at end)
            envelope[-decay_frames:] = np.linspace(1, 0.3, decay_frames)
            
            # Make final note fade out completely
            if i == len(victory_notes) - 1:
                final_decay = frames // 3
                envelope[-final_decay:] = np.linspace(0.8, 0, final_decay)
            
            arr[current_frame:current_frame + frames] = wave * envelope * 0.8
            current_frame += frames
        
        # Add some harmonic richness to the final chord
        if total_frames > sample_rate:  # If long enough
            # Add a subtle harmony on the final note
            harmony_start = int(total_frames * 0.7)
            harmony_frames = total_frames - harmony_start
            
            # Add perfect fifth harmony (G5)
            harmony_freq = 783.99  # G5
            harmony_wave = np.sin(2 * np.pi * harmony_freq * 
                                 np.linspace(0, harmony_frames / sample_rate, harmony_frames))
            harmony_envelope = np.exp(-2 * np.linspace(0, 1, harmony_frames))
            
            arr[harmony_start:] += harmony_wave * harmony_envelope * 0.4
        
        # Normalize and convert
        arr = np.clip(arr, -1, 1)  # Prevent clipping
        arr = (arr * 32767 * self.volume).astype(np.int16)
        
        # Create stereo
        stereo_arr = np.zeros((total_frames, 2), dtype=np.int16)
        stereo_arr[:, 0] = arr
        stereo_arr[:, 1] = arr
        
        return pygame.sndarray.make_sound(stereo_arr)
    
    def play_sound(self, sound_name: str, async_play: bool = True):
        """
        Play a sound by name
        async_play: If True, play in background thread (non-blocking)
        """
        if not self.initialized:
            return
            
        if sound_name not in self.sounds:
            logger.warning(f"Sound '{sound_name}' not found")
            return
        
        try:
            if async_play:
                # Play in background thread to avoid blocking game
                thread = threading.Thread(
                    target=self._play_sound_sync, 
                    args=(sound_name,),
                    daemon=True
                )
                thread.start()
            else:
                self._play_sound_sync(sound_name)
                
        except Exception as e:
            logger.error(f"Error playing sound '{sound_name}': {e}")
    
    def _play_sound_sync(self, sound_name: str):
        """Play sound synchronously"""
        try:
            sound = self.sounds[sound_name]
            sound.play()
        except Exception as e:
            logger.error(f"Error in sync sound play: {e}")
    
    def play_game_start(self):
        """Play pleasant game start sound"""
        self.play_sound('game_start')
        logger.info("Playing game start sound")
    
    def play_game_end(self):
        """Play gentle game end melody"""
        self.play_sound('game_end')
        logger.info("Playing game end sound")
    
    def play_victory(self):
        """Play triumphant victory fanfare"""
        self.play_sound('victory')
        logger.info("Playing victory fanfare")
    
    def play_piece_move(self):
        """Play soft piece movement sound"""
        self.play_sound('piece_move')
    
    def play_piece_capture(self):
        """Play success chime for captures"""
        self.play_sound('piece_capture')
        logger.info("Playing piece capture sound")
    
    def play_cursor_move(self):
        """Play subtle cursor movement sound"""
        self.play_sound('cursor_move')
    
    def play_piece_jump(self):
        """Play dramatic jump sound"""
        self.play_sound('piece_jump')
    
    def set_volume(self, volume: float):
        """Set master volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        logger.info(f"Volume set to {self.volume}")
    
    def is_available(self) -> bool:
        """Check if sound system is available"""
        return self.initialized


# Global sound manager instance
sound_manager = SoundManager()
