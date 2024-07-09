import logging
import os
import random
from typing import List, Dict, Tuple
import requests
from PIL import Image
from moviepy.editor import (
    ImageClip,
    concatenate_videoclips,
    CompositeVideoClip,
    AudioFileClip
)
from pydub import AudioSegment
import sys

# Ensure the src directory is in the sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.image.image_grabber import ImageGrabber 
from src.audio.audio import WaveNetTTS

logger = logging.getLogger(__name__)

class VideoSegment:
    IMAGE_FORMAT_RGB = "RGB"
    IMAGE_FORMAT_JPEG = "JPEG"

    def __init__(self, text: str, voiceover_text: List[Dict], image_keyword: str, segment_number: int, images_number: int = 5):
        self.segment_number = segment_number
        self.text = text
        self.voiceover_text = voiceover_text
        self.image_keyword = image_keyword
        self.images_number = images_number

    def _download_images(self, urls: List[str], keyword: str, download_folder: str) -> List[str]:
        images = []
        os.makedirs(os.path.join(download_folder, keyword), exist_ok=True)
        for url in urls:
            try:
                download_path = os.path.join(download_folder, keyword, f"image_{len(images) + 1}.jpg")
                if not os.path.exists(download_path):
                    response = requests.get(url)
                    response.raise_for_status()
                    with open(download_path, "wb") as file:
                        file.write(response.content)
                images.append(download_path)
            except requests.exceptions.RequestException as e:
                logger.error(f"Error downloading image from {url}: {e}")
            except OSError as e:
                logger.error(f"Filesystem error while saving image: {e}")
        return images

    def _resize_images(self, images: List[str], size: Tuple[int, int]) -> List[str]:
        resized_images = []
        for image_path in images:
            try:
                with Image.open(image_path) as img:
                    img = img.convert(self.IMAGE_FORMAT_RGB)
                    img = self._resize_image(img, size)
                    save_path = self._get_save_path(image_path)
                    img.save(save_path, self.IMAGE_FORMAT_JPEG)
                    resized_images.append(save_path)
            except (OSError, IOError) as e:
                logger.error(f"Error resizing image {image_path}: {e}")
        return resized_images

    def _resize_image(self, image: Image.Image, size: Tuple[int, int]) -> Image.Image:
        return image.resize(size, Image.LANCZOS)  # LANCZOS is a high-quality downsampling filter

    def _get_save_path(self, image_path: str) -> str:
        return os.path.splitext(image_path)[0] + "_resized.jpg"

    def generate_segment(self, tts: WaveNetTTS, gid: ImageGrabber, download_folder: str, size: Tuple[int, int]) -> CompositeVideoClip:
        image_urls = gid.search_images(self.image_keyword)
        random_image_urls = random.sample(image_urls, min(self.images_number, len(image_urls)))

        images = self._download_images(random_image_urls, self.image_keyword, download_folder)
        resized_images = self._resize_images(images, size)

        image_clips = [ImageClip(image).set_duration(5) for image in resized_images]  # Set each image duration to 5 seconds

        audio_clips = []
        segment_duration = 0

        for voiceover in self.voiceover_text:
            try:
                audio_path = tts.generate_tts(voiceover["text"], voiceover["voice"])
                audio_clip = AudioSegment.from_wav(audio_path)
                duration = len(audio_clip) / 1000  # Convert from milliseconds to seconds
                segment_duration += duration
                audio_clips.append(audio_path)
            except Exception as e:
                logger.error(f"Error generating audio for voiceover: {e}")

        if audio_clips:
            final_audio_path = os.path.join(download_folder, f"final_audio_{self.segment_number}.wav")
            combined_audio = AudioSegment.empty()
            for audio_path in audio_clips:
                combined_audio += AudioSegment.from_wav(audio_path)
            combined_audio.export(final_audio_path, format="wav")
        else:
            final_audio_path = None

        # Adjust the duration of image clips to match the audio duration
        for clip in image_clips:
            clip.duration = segment_duration / len(image_clips)

        final_clip = concatenate_videoclips(image_clips, method="compose")

        if final_audio_path:
            final_audio = AudioFileClip(final_audio_path)
            final_clip = final_clip.set_audio(final_audio)

        final_clip = final_clip.set_duration(segment_duration)
        final_clip = final_clip.set_fps(24)

        return CompositeVideoClip([final_clip])