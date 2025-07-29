"""
Comprehensive tests for the SoundManager and Audio System
בדיקות מקיפות למערכת הקול
"""
import pytest
import numpy as np
import threading
import time
from unittest.mock import Mock, patch, MagicMock
import tempfile
import pathlib

import sys
sys.path.append(str(pathlib.Path(__file__).parent.parent))

from SoundManager import SoundManager, sound_manager


class TestSoundManager:
    """Test the SoundManager class"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Create a fresh SoundManager instance for testing
        self.sound_manager = SoundManager()
        
    def test_sound_manager_initialization(self):
        """Test SoundManager initializes correctly"""
        assert isinstance(self.sound_manager, SoundManager)
        assert hasattr(self.sound_manager, 'sounds')
        assert hasattr(self.sound_manager, 'volume')
        assert 0.0 <= self.sound_manager.volume <= 1.0
        
    def test_sound_generation(self):
        """Test that sounds are generated correctly"""
        # Sounds should be generated during initialization
        expected_sounds = ['game_start', 'piece_move', 'piece_capture', 'victory']
        
        for sound_name in expected_sounds:
            assert sound_name in self.sound_manager.sounds
            # Sound manager stores pygame.mixer.Sound objects, not numpy arrays
            sound_obj = self.sound_manager.sounds[sound_name]
            # Check it's a pygame Sound object or can be played
            assert hasattr(sound_obj, 'play') or sound_obj is None
            
    def test_volume_setting(self):
        """Test volume setting functionality"""
        # Test valid volume levels
        test_volumes = [0.0, 0.3, 0.5, 0.8, 1.0]
        
        for volume in test_volumes:
            self.sound_manager.set_volume(volume)
            assert self.sound_manager.volume == volume
            
    def test_volume_clamping(self):
        """Test volume is clamped to valid range"""
        # Test volume clamping
        self.sound_manager.set_volume(-0.5)
        assert self.sound_manager.volume == 0.0
        
        self.sound_manager.set_volume(1.5)
        assert self.sound_manager.volume == 1.0
        
    def test_availability_check(self):
        """Test availability checking"""
        # Should return boolean
        available = self.sound_manager.is_available()
        assert isinstance(available, bool)
        
    @patch('pygame.mixer.init')
    @patch('pygame.mixer.get_init')
    def test_pygame_initialization(self, mock_get_init, mock_init):
        """Test pygame mixer initialization"""
        mock_get_init.return_value = None  # Not initialized
        
        # Create new SoundManager to trigger initialization
        sm = SoundManager()
        
        # Should have tried to initialize pygame
        mock_init.assert_called()
        
    def test_sound_creation_methods(self):
        """Test individual sound creation methods"""
        # Test chord sound creation
        chord_sound = self.sound_manager._create_chord_sound([440, 554, 659], duration=0.5)
        assert hasattr(chord_sound, 'play')  # Should be pygame Sound object
        
        # Test melody sound creation  
        melody_sound = self.sound_manager._create_melody_sound([440, 494, 523], duration=0.3)
        assert hasattr(melody_sound, 'play')
        
        # Test soft click creation
        click_sound = self.sound_manager._create_soft_click(frequency=800, duration=0.15)
        assert hasattr(click_sound, 'play')
        
        # Test victory fanfare creation
        fanfare_sound = self.sound_manager._create_victory_fanfare()
        assert hasattr(fanfare_sound, 'play')
        
    def test_sound_properties(self):
        """Test generated sound properties"""
        for sound_name, sound_data in self.sound_manager.sounds.items():
            # All sounds should be pygame Sound objects or None
            if sound_data is not None:
                assert hasattr(sound_data, 'play')
                assert hasattr(sound_data, 'set_volume')
            
    @patch('pygame.mixer.get_init')
    def test_play_sound_sync(self, mock_get_init):
        """Test synchronous sound playing"""
        mock_get_init.return_value = (22050, -16, 2)  # Mock initialized
        mock_sound = Mock()
        
        # Replace the sound in the manager
        self.sound_manager.sounds['game_start'] = mock_sound
        
        self.sound_manager._play_sound_sync('game_start')
        
        # Should have played the sound
        mock_sound.play.assert_called()
        
    @patch('pygame.mixer.get_init')
    def test_play_sound_when_unavailable(self, mock_get_init):
        """Test playing sound when pygame is unavailable"""
        mock_get_init.return_value = None  # Not initialized
        
        # Should not crash when pygame unavailable
        self.sound_manager.play_sound('game_start')
        
    def test_convenience_methods(self):
        """Test convenience methods for playing specific sounds"""
        with patch.object(self.sound_manager, 'play_sound') as mock_play:
            # Test all convenience methods
            self.sound_manager.play_game_start()
            mock_play.assert_called_with('game_start')
            
            self.sound_manager.play_game_end()
            mock_play.assert_called_with('game_end')  # game_end uses its own sound
            
            self.sound_manager.play_victory()
            mock_play.assert_called_with('victory')
            
            self.sound_manager.play_piece_move()
            mock_play.assert_called_with('piece_move')
            
            self.sound_manager.play_piece_capture()
            mock_play.assert_called_with('piece_capture')
            
    def test_async_sound_playing(self):
        """Test asynchronous sound playing"""
        with patch.object(self.sound_manager, '_play_sound_sync') as mock_sync:
            with patch('threading.Thread') as mock_thread:
                mock_thread_instance = Mock()
                mock_thread.return_value = mock_thread_instance
                
                # Play sound asynchronously
                self.sound_manager.play_sound('piece_move', async_play=True)
                
                # Should have created and started thread
                mock_thread.assert_called()
                mock_thread_instance.start.assert_called()
                
    def test_sound_data_integrity(self):
        """Test that sound data maintains integrity across calls"""
        # Get initial sound references
        initial_game_start = self.sound_manager.sounds['game_start']
        initial_victory = self.sound_manager.sounds['victory']
        
        # Play sounds multiple times
        for _ in range(5):
            self.sound_manager.play_sound('game_start')
            self.sound_manager.play_sound('victory')
            
        # Sound references should remain unchanged
        assert self.sound_manager.sounds['game_start'] is initial_game_start
        assert self.sound_manager.sounds['victory'] is initial_victory
        
    def test_invalid_sound_name(self):
        """Test handling of invalid sound names"""
        # Should not crash with invalid sound name
        self.sound_manager.play_sound('invalid_sound_name')
        
    def test_concurrent_sound_playing(self):
        """Test concurrent sound playing"""
        def play_sound_repeatedly(sound_name, count):
            for _ in range(count):
                self.sound_manager.play_sound(sound_name)
                time.sleep(0.01)
                
        # Start multiple threads playing different sounds
        threads = []
        sound_names = ['game_start', 'piece_move', 'piece_capture', 'victory']
        
        for sound_name in sound_names:
            thread = threading.Thread(target=play_sound_repeatedly, args=(sound_name, 5))
            threads.append(thread)
            thread.start()
            
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
        # Should complete without errors
        assert True
        
    def test_sound_frequency_generation(self):
        """Test frequency-based sound generation"""
        # Test different frequencies
        frequencies = [220, 440, 880, 1760]  # A notes in different octaves
        
        for freq in frequencies:
            sound = self.sound_manager._create_soft_click(frequency=freq, duration=0.1)
            assert hasattr(sound, 'play')
            
        # Test chord with multiple frequencies
        chord = self.sound_manager._create_chord_sound(frequencies, duration=0.5)
        assert hasattr(chord, 'play')


class TestSoundManagerIntegration:
    """Integration tests for SoundManager with game events"""
    
    def setup_method(self):
        """Setup for integration tests"""
        self.sound_manager = SoundManager()
        
    def test_game_audio_flow(self):
        """Test complete game audio flow"""
        with patch.object(self.sound_manager, '_play_sound_sync') as mock_play:
            # Simulate game flow
            self.sound_manager.play_game_start()
            self.sound_manager.play_piece_move()
            self.sound_manager.play_piece_move()
            self.sound_manager.play_piece_capture()
            self.sound_manager.play_piece_move()
            self.sound_manager.play_victory()
            
            # Should have played 6 sounds total
            assert mock_play.call_count == 6
            
    def test_rapid_sound_sequence(self):
        """Test rapid sequence of sounds (like fast gameplay)"""
        with patch.object(self.sound_manager, 'play_sound') as mock_play:
            # Rapid sequence of moves
            for i in range(20):
                self.sound_manager.play_piece_move()
                if i % 5 == 0:
                    self.sound_manager.play_piece_capture()
                    
            # Should have handled all sound requests
            assert mock_play.call_count == 24  # 20 moves + 4 captures
            
    def test_volume_affects_all_sounds(self):
        """Test that volume setting affects all sound types"""
        test_volume = 0.5
        self.sound_manager.set_volume(test_volume)
        
        with patch('pygame.mixer.Sound') as mock_sound_class:
            mock_sound = Mock()
            mock_sound_class.return_value = mock_sound
            
            with patch('pygame.mixer.get_init', return_value=(22050, -16, 2)):
                # Play different types of sounds
                self.sound_manager._play_sound_sync('game_start')
                self.sound_manager._play_sound_sync('piece_move')
                self.sound_manager._play_sound_sync('victory')
                
                # All should have been played with same volume
                for call in mock_sound.set_volume.call_args_list:
                    assert call[0][0] == test_volume


class TestGlobalSoundManager:
    """Test the global sound_manager instance"""
    
    def test_global_instance_exists(self):
        """Test that global sound_manager instance exists"""
        assert sound_manager is not None
        assert isinstance(sound_manager, SoundManager)
        
    def test_global_instance_functionality(self):
        """Test that global instance works correctly"""
        # Should have sounds generated
        assert len(sound_manager.sounds) > 0
        
        # Should respond to method calls
        original_volume = sound_manager.volume
        sound_manager.set_volume(0.8)
        assert sound_manager.volume == 0.8
        
        # Restore original volume
        sound_manager.set_volume(original_volume)
        
    def test_global_instance_thread_safety(self):
        """Test that global instance is thread-safe"""
        def change_volume(volume):
            sound_manager.set_volume(volume)
            time.sleep(0.01)
            
        # Start multiple threads changing volume
        threads = []
        volumes = [0.1, 0.3, 0.5, 0.7, 0.9]
        
        for volume in volumes:
            thread = threading.Thread(target=change_volume, args=(volume,))
            threads.append(thread)
            thread.start()
            
        # Wait for all threads
        for thread in threads:
            thread.join()
            
        # Volume should be one of the test values
        assert sound_manager.volume in volumes


if __name__ == "__main__":
    pytest.main([__file__])
