# TTV

TTV is a Python application that processes custom text input to generate videos. It supports various features such as image search, voice-over, and video composition. With TTV, you can easily create video segments based on text input and generate engaging videos with dynamic images and voice narration.


## Features

- **Text Processing**: TTV processes custom text input and splits it into video segments based on the [IMAGE] tag.
- **Image Search**: It searches for images based on keywords specified in the text and selects a random set of images for each video segment.
- **Voice-over**: TTV provides support for voice narration by processing [VOICE] tags in the text and assigning the appropriate voice to each segment.
- **Video Composition**: It combines the selected images and voice-over to generate a final video segment.

## Requirements

- Python 3.7 or higher
- Dependencies (can be installed using `pip install -r requirements.txt`)

## Installation

1. **Clone the repository**: 
   ```bash
   git clone https://github.com/GrishMahat/TTV.git
   ```

2. **Navigate to the project directory**: 
   ```bash
   cd TTV
   ```

3. **Install the dependencies**: 
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Update the text input in the `test_script.txt` file with your desired content**. You can add [IMAGE] tags to specify image keywords and [VOICE] tags to assign specific voices for voice-over.

2. **Run the `main.py` script to process the text and generate the video**:
   ```bash
   python main.py
   ```

3. **The generated video segments will be saved in the `output` directory**. You can customize the output directory by modifying the `output_directory` variable in `main.py`.

## Configuration

You can customize the behavior of TTV by modifying the following variables in `main.py`:

- `IMAGE_SEARCH_COUNT`: Specifies the number of images to be selected for each video segment. You can adjust this value based on your preferences.
- `VIDEO_FPS`: Sets the frames per second (FPS) of the generated video. By default, it is set to 24 FPS, but you can modify it as per your requirements.
- `OUTPUT_DIRECTORY`: Specifies the directory where the generated video segments will be saved. By default, it is set to the `output` directory.

## Contributing

Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request.

### Problems ,Challenges And Current Issues

1. **Image Licensing**: One of the challenges is ensuring that the downloaded images are free to use, as many online images are subject to copyright. Contributors could implement an image licensing check to avoid any legal issues.

2. **Voice Selection**: The project currently supports a default voice. Enhancements could involve allowing users to choose from multiple voices and languages.

3. **Error Handling**: Robust error handling can be improved to handle various exceptions gracefully and provide informative error messages to users.

4. **Performance**: Handling large amounts of text and images efficiently is crucial for the success of the Text to Video (TTV) project. As the project evolves, contributors can focus on the following areas to optimize its performance.

5. **Import Errors**: The project is currently facing import errors, causing problems with accessing necessary modules and dependencies.

6. **Responsive GUI**: The graphical user interface (GUI) is not fully responsive to different screen sizes and may not work well on all devices.


### How to Contribute

If you're interested in contributing to the TTV project, here's how you can get involved:

1. **Bug Fixes**: If you encounter any bugs or unexpected behavior, please open an issue on the GitHub repository.

2. **Feature Requests**: Have an idea for an exciting feature or improvement? Share it in the issues section.

3. **Code Contributions**: Feel free to submit pull requests for bug fixes, optimizations, or new features. Follow the project's coding style and guidelines when contributing.

4. **Documentation**: Good documentation is essential. Help improve the project's documentation to make it more accessible for users and contributors.

5. **Testing**: Rigorous testing ensures reliability. Contribute by writing and running test cases to cover different parts of the code.

6. **Code Reviews**: Reviewing pull requests and providing constructive feedback is a valuable contribution.

By working together, contributors can make TTV more robust, feature-rich, and user-friendly, solving challenges and creating a useful tool for creating videos from text input.

### A Glimpse Inside

- **src**: The source code of TTV.
- **src/api**: Manages API interactions.
- **src/audio**: Handles audio-related tasks.
- **src/image**: Drives image retrieval.
- **src/text**: Contains the text processing logic.
- **src/utils**: Provides utility functions.
- **src/video**: Manages video segment creation.
- **src/TextToVideo.py**: The central script that orchestrates the project.


### 1. Text Processor (`src/text/text_processor.py`):

The Text Processor module is responsible for handling the input text and breaking it down into manageable segments for video generation. Here's what it does:

- **Text Splitting**: It splits the input text into video segments based on specific tags, such as `[IMAGE]` and `[VOICE]`. Each of these tags represents a distinct part of the video.

- **Image Tag Processing**: When it encounters `[IMAGE]` tags, it extracts the image keyword and the number of images specified (defaulting to 5 if not provided). These keywords are used for image searches.

- **Voice-over Segmentation**: The module also deals with voice narration by identifying `[VOICE]` tags and their corresponding text segments. It assigns the appropriate voice to each section.

- **Segment Information**: It gathers essential information from the text, such as the sentences and associated image keywords, and stores them for further processing.

### 2. Image Grabber (`src/image/image_grabber.py`):

The Image Grabber module is responsible for fetching images from the web based on specified keywords. Here's what it does:

- **Image Search**: It performs searches for images on the internet using Google image search. The keywords for these searches are obtained from the Text Processor module.

- **Image Download**: After finding relevant images, it downloads a random set of them to be used in video segments.

### 3. Voice-over (`src/audio/audio.py`):

The Voice-over module deals with generating voice narrations for the video segments. Here's how it functions:

- **Text-to-Speech Conversion**: Using the Google Text-to-Speech (gTTS) library, it converts text segments into audio files. These audio files serve as the voice narrations for the corresponding video segments.

- **Voice Settings**: Currently, it might use a default voice, but there's potential for extending it to support multiple voices or languages.

### 4. Video Segment (`src/video/video_segment.py`):

The Video Segment module handles the actual creation of video segments. Here's what it accomplishes:

- **Text, Image, and Voice Integration**: It combines the extracted text, downloaded images, and generated voice narrations to create a cohesive video segment.

- **Image Selection**: Based on the keywords from the Text Processor, it selects appropriate images from the ones fetched by the Image Grabber.

- **Voice Synchronization**: It ensures that the voice narration aligns correctly with the corresponding text.

- **Segment Composition**: The module composes all these elements into a single video segment.

### 5. Main Script (`main.py`):

The Main Script serves as the entry point to the TTV application. It orchestrates the entire video generation process. Here's its role:

- **Input Handling**: It reads the text input from the `test_script.txt` file, where you can specify the content and segment details using `[IMAGE]` and `[VOICE]` tags.

- **Text Processing**: The main script initiates the Text Processor to split the input text into video segments.

- **Image Download**: It triggers the Image Grabber to search for and download relevant images based on the keywords obtained.

- **Voice-over Generation**: The script uses the Voice-over module to generate voice narrations for the video segments.

- **Video Composition**: Finally, it invokes the Video Segment module to create individual video segments and merges them into a complete video.

### 6. Tests (`tests/`):

This directory contains test files and configurations for testing the project components. It's essential for ensuring the correctness and reliability of the codebase.

These are the primary components of your TTV project, each contributing to different aspects of video generation from custom text input. By working together, they enable users to create engaging videos with dynamic images and voice narration based on their textual content.
