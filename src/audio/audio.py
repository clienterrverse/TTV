import os
import re
import logging
from typing import Tuple
from gtts import gTTS
from mutagen.mp3 import MP3
from pathlib import Path

# Ensure mkdir function is available in src/utils/common.py
def mkdir(directory: str) -> None:
    """
    Create a directory if it does not exist.

    Args:
        directory (str): The directory path to create.
    """
    try:
        os.makedirs(directory, exist_ok=True)
    except Exception as e:
        logging.error(f"Error creating directory {directory}: {str(e)}")
        raise

class WaveNetTTS:
    def __init__(self, download_location: str = "audio"):
        """
        Initialize the TTS object.

        Args:
            download_location (str, optional): Folder to download audio to. Defaults to "audio".
        """
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        
        self._memory = {}
        self.download_location = download_location
        mkdir(download_location)
        self._load_audio()

    def _load_audio(self) -> None:
        """
        Load existing audio files into memory.
        """
        local_files = {}
        try:
            for file in os.listdir(self.download_location):
                audio_file = os.path.join(self.download_location, file)
                if os.path.isfile(audio_file) and file.endswith(".mp3"):
                    mp3 = MP3(audio_file)
                    text = file[:-4]  # Remove the '.mp3' extension
                    local_files[text] = (audio_file, mp3.info.length)
            self._memory = local_files
        except Exception as e:
            self.logger.error(f"Error loading audio files: {str(e)}")
            raise

    def get_tts(self, text: str) -> Tuple[str, float]:
        """
        Get TTS for a given string and download it to download_location if not already cached.

        Args:
            text (str): Text to turn into speech.

        Returns:
            Tuple[str, float]: Path to saved file and audio length.
        """
        try:
            # Sanitize text to create a valid file name
            safe_text = re.sub(r'\W+', '_', text)

            if safe_text in self._memory:
                self.logger.info(f"Using cached TTS for text: {text}")
                return self._memory[safe_text]

            audio_file = os.path.join(self.download_location, f"{safe_text}.mp3")

            if not os.path.isfile(audio_file):
                self.logger.info(f"Generating new TTS for text: {text}")
                tts = gTTS(text)
                tts.save(audio_file)

            # Get audio length for video duration
            mp3 = MP3(audio_file)
            self._memory[safe_text] = (audio_file, mp3.info.length)
            return self._memory[safe_text]

        except Exception as e:
            self.logger.error(f"Error generating TTS: {str(e)}")
            raise
