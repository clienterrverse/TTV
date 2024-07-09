import re
from typing import List, Dict, Tuple
import os
import sys
import logging

# Ensure the src directory is in the sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.video.video_segment import VideoSegment

logger = logging.getLogger(__name__)

class TextProcessor:
    def __init__(self):
        self.text = ""
        self.video_segments = []
        self.sentences = []

    def process_text(self, text: str):
        self.text = text
        self._process_text_for_images()


    TEXT_TEMPLATES = {
        "image": r"\[IMAGE:\s*(.+?)(\d*?)]",
        "search_voice": r"\[VOICE:\s*(.+?)](.+?)\[\/VOICE]",
    }

    DEFAULT_IMAGE_COUNT = 5
    DEFAULT_VOICE = "DEFAULT"


    def _process_text_for_images(self) -> None:
        """
        Processes the text to extract image keywords and create video segments.
        """
        try:
            image_matches = list(re.finditer(self.TEXT_TEMPLATES["image"], self.text))
            sentences = re.split(self.TEXT_TEMPLATES["image"], self.text)

            for i, match in enumerate(image_matches):
                image_keyword = match.group(1).strip()
                images_number = int(match.group(2) or self.DEFAULT_IMAGE_COUNT)

                if i < len(sentences):
                    sentence = sentences[i].strip()
                    video_segment = self._create_video_segment(sentence, image_keyword, i + 1, images_number)
                    self.video_segments.append(video_segment)
                    self.sentences.append((sentence, image_keyword))

            # Process remaining sentences without image tags
            for sentence in sentences[len(image_matches):]:
                sentence = sentence.strip()
                if sentence:
                    video_segment = self._create_video_segment(sentence, "", len(self.video_segments) + 1, 0)
                    self.video_segments.append(video_segment)
                    self.sentences.append((sentence, ""))

            logger.info(f"Processed {len(self.video_segments)} video segments")
        except Exception as e:
            logger.error(f"Error processing text for images: {e}", exc_info=True)

    def _create_video_segment(self, sentence: str, image_keyword: str, order: int, images_number: int) -> VideoSegment:
        """
        Creates a video segment.

        Args:
            sentence (str): The sentence for the segment.
            image_keyword (str): The keyword for the image search.
            order (int): The order of the segment in the video.
            images_number (int): The number of images to search for.

        Returns:
            VideoSegment: The created video segment.
        """
        try:
            voiceover_segments = self._process_voices(sentence)
            return VideoSegment(sentence, voiceover_segments, image_keyword, order, images_number)
        except Exception as e:
            logger.error(f"Error creating video segment: {e}", exc_info=True)
            return VideoSegment(sentence, [], image_keyword, order, images_number)

    def _process_voices(self, text: str) -> List[Dict[str, str]]:
        """
        Processes the text to extract voice segments.

        Args:
            text (str): The text to process for voice segments.

        Returns:
            List[Dict[str, str]]: A list of dictionaries with voice and text pairs.
        """
        voiceover_segments: List[Dict[str, str]] = []
        try:
            text_segments = re.split(self.TEXT_TEMPLATES["search_voice"], text)
            voice_segments = list(re.finditer(self.TEXT_TEMPLATES["search_voice"], text))

            # Process segments without voice tags
            for segment in text_segments:
                segment = segment.strip()
                if segment:
                    voiceover_segments.append({"voice": self.DEFAULT_VOICE, "text": segment})

            # Process segments with specific voice tags
            for voice_segment in voice_segments:
                voice_tag = voice_segment.group(1).strip()
                voice_text = voice_segment.group(2).strip()
                for segment in voiceover_segments:
                    if segment["text"] == voice_text:
                        segment["voice"] = voice_tag
                        break

            logger.debug(f"Processed {len(voiceover_segments)} voice segments")
        except Exception as e:
            logger.error(f"Error processing voices: {e}", exc_info=True)

        return voiceover_segments

    def get_video_segments(self) -> List[VideoSegment]:
        """
        Returns the list of video segments.
        """
        return self.video_segments