import sys
import os
import logging
from pathlib import Path
from typing import List, Dict
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Add src to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from moviepy.editor import concatenate_videoclips, VideoClip
from src.image.image_grabber import ImageGrabber
from src.text.text_processor import TextProcessor
from src.audio.audio import WaveNetTTS
from src.video.video_segment import VideoSegment

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TextToVideo:
    def __init__(self, text: str, output_file: str, segment_length: int = 100, image_size: tuple = (1920, 1080)):
        self.text = text
        self.output_file = output_file
        self.video_segments: List[VideoClip] = []
        self.segment_length = segment_length
        self.image_size = image_size
        
        # Initialize components
        self.image_grabber = ImageGrabber(resize=True, size=image_size)
        self.tts = WaveNetTTS()
        self.text_processor = TextProcessor()
        
        # Ensure NLTK data is downloaded
        self._download_nltk_data()

    @staticmethod
    def _download_nltk_data():
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)

    def _extract_keywords(self, text: str, num_keywords: int = 3) -> List[str]:
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(text.lower())
        filtered_tokens = [w for w in word_tokens if w.isalnum() and w not in stop_words]
        
        freq_dist = nltk.FreqDist(filtered_tokens)
        return [word for word, _ in freq_dist.most_common(num_keywords)]

    def _create_segments(self) -> List[Dict]:
        self.text_processor.process_text(self.text)
        segments = self.text_processor.get_video_segments()
        processed_segments = []

        for i, segment in enumerate(segments, start=1):
            keywords = self._extract_keywords(segment.text)
            processed_segments.append({
                "text": segment.text,
                "voiceover_text": segment.voiceover_text,
                "image_keyword": segment.image_keyword or " ".join(keywords),
                "segment_number": i,
                "images_number": segment.images_number
            })

        return processed_segments

    def process_video_elements(self):
        segments = self._create_segments()
        download_folder = Path("downloads")
        download_folder.mkdir(exist_ok=True)

        for segment in segments:
            try:
                video_segment = VideoSegment(**segment)
                video_clip = video_segment.generate_segment(
                    self.tts, 
                    self.image_grabber, 
                    str(download_folder), 
                    self.image_size
                )
                self.video_segments.append(video_clip)
                logger.info(f"Processed segment {segment['segment_number']}")
            except Exception as e:
                logger.error(f"Error generating video segment {segment['segment_number']}: {str(e)}")
                raise

    def save_video(self):
        if not self.video_segments:
            raise ValueError("No video elements to save.")

        try:
            final_clip = concatenate_videoclips(self.video_segments, method="compose")
            final_clip.write_videofile(self.output_file, codec='libx264')
            logger.info(f"Video saved as {self.output_file}")
        except Exception as e:
            logger.error(f"Error saving video: {str(e)}")
            raise

    def generate_video(self):
        logger.info("Starting video generation process")
        try:
            self.process_video_elements()
            self.save_video()
            logger.info("Video generation completed successfully")
        except Exception as e:
            logger.error(f"Video generation failed: {str(e)}")
            raise

    def cleanup(self):
        # Add any cleanup operations here, e.g., deleting temporary files
        pass

if __name__ == "__main__":
    # Example usage
    input_text = "Your input text here"
    output_file = "output_video.mp4"
    
    try:
        ttv = TextToVideo(input_text, output_file)
        ttv.generate_video()
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        ttv.cleanup()