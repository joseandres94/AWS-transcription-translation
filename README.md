# AWS Audio/Video Transcription and Translation Script

This repository contains a Python script that automates the process of transcribing the audio from a media file (like `.mov`, `.mp4`, etc.) and translating the resulting transcription into another language using Amazon Web Services (AWS).

Developed as an exercise during the 'Introduction to Machine Learning with AWS' course on Coursera, this project demonstrates the integration of several core AWS services via their APIs. The aim is to showcase the practical application of learned concepts and provide a functional example for others in the community.

## Features

* **File Upload:** Automatically uploads the local media file to an Amazon S3 bucket.
* **Transcription:** Initiates and monitors an AWS Transcribe job to convert speech to text. Includes a timeout for the waiting process.
* **Translation:** Translates the transcribed text sentence by sentence using Amazon Translate.
* **Output Generation:** Saves the original detailed transcription and the translated text into separate JSON files (`transcribe.json` and `translated.json`).
* **Resource Cleanup:** Attempts to remove the created S3 bucket, the uploaded file(s) within it, and the Transcribe job after processing.

## AWS Services Used

* **Amazon Simple Storage Service (S3):** Used for storing the media file before transcription and the transcription output.
* **Amazon Transcribe:** Used for converting the audio from the media file into text.
* **Amazon Translate:** Used for translating the transcribed text into a target language.

All interactions with these services are done through the AWS SDK for Python (Boto3).

## Prerequisites

Before running this script, you need:

1.  **Python 3.8:** Make sure Python is installed on your system.
2.  **AWS Account:** You need an active AWS account.
3.  **AWS CLI Configured:** The AWS Command Line Interface (CLI) should be installed and configured with credentials and a default region (`aws configure`). The script uses your default AWS profile.
4.  **Boto3 Library:** Install the Boto3 library for Python.
5.  **Input Media File:** An audio or video file (e.g., `.mov`, `.mp4`, `.mp3`) compatible with [AWS Transcribe supported formats](https://docs.aws.amazon.com/transcribe/latest/dg/how-input.html).

## Installation

Clone this repository (or copy the script) and install the required Python library:

```bash
git clone https://github.com/joseandres94/AWS-transcription-translation.git
cd AWS-transcription-translation
pip install boto3
```

## How to Run
Execute the script from your terminal, providing the path to your input media file as a command-line argument:
```bash
python3 transcribe_translate.py /path/to/your/input_file.mov
# Example: python3 transcribe_translate.py my_video.mp4
```
The script will then:

1. Create an S3 bucket.
2. Upload your file.
3. Start the transcription job.
4. Wait for the job to complete.
5. Download and process the results.
6. Perform the translation.
7. Save the output files (transcribe.json and translated.json) in the same directory where you run the script.
8. Attempt to clean up the created AWS resources.

## Output Files
transcribe.json: This file contains the complete raw JSON output from the AWS Transcribe service for your media file. It includes segment information, word-level timestamps, confidence scores, and alternative interpretations.
translated.json: This file contains a JSON array. Each element in the array is an object representing a translated sentence, with the following structure:
```bash
{
  "start_time": "...", // The start time (in seconds, as a string) of the first word of the original sentence segment.
  "translated": "..."  // The translated text of the sentence.
}
```

## Important Considerations and Limitations
- Timestamp Accuracy for Translation: The start_time associated with each translated sentence in translated.json is taken directly from the timestamp of the first word of the original sentence segment provided by AWS Transcribe. This is a simplification and does NOT represent the precise start time or duration of the translated sentence itself.
- AWS Costs: Please be aware that using AWS services (S3 storage, Transcribe processing, Translate usage) incurs costs in your AWS account. Review the AWS pricing pages for these services to understand potential charges. The script attempts to clean up resources, but always verify in the AWS console that they have been successfully removed.
- Large Files / Batch Processing: The current script is designed for processing a single file sequentially. For very large files (requiring multipart upload) or processing multiple files, you would need to implement more advanced Boto3 features (like S3 Transfer Manager, SQS/SNS notifications for Transcribe job completion instead of polling, and pagination for S3 object listing beyond 1000 items).

## Acknowledgements
This project is a practical exercise derived from the 'Introduction to Machine Learning with AWS' course offered on Coursera by AWS.

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Author
José Andrés Lorenzo.
https://github.com/joseandres94
