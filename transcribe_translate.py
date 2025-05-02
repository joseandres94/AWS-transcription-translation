import json
import re
import boto3
import sys
import time

## Functions definition
def call_aws_create_bucket(client, name_bucket, region):
    try:
        client.create_bucket(
            Bucket=name_bucket,
            CreateBucketConfiguration={
                'LocationConstraint': region,
            }
        )
    except boto3.exceptions.Boto3Error as e:
        print(f'Boto3 error creating bucket: {e}')
        return False

    except Exception as e:
        print(f'Error creating bucket: {e}')
        return False

    return True

def call_aws_uploadfile(client, name_bucket, name_file):
    try:
        with open(name_file, 'rb') as file:
            client.upload_fileobj(file, name_bucket, name_file)

    except FileNotFoundError:
        print(f'File {name_file} not found.')
        return False

    except boto3.exceptions.Boto3Error as e:
        print(f'Boto3 error updating file: {e}')
        return False

    except Exception as e:
        print(f'Error updating file: {e}')
        return False

    return True

def call_aws_transcript(client, name_job, name_bucket, name_file, lang_code):
    try:
        client.start_transcription_job(
            TranscriptionJobName = name_job,
            LanguageCode = lang_code,
            Media = {
                'MediaFileUri': f's3://{name_bucket}/{name_file}'
            },
            OutputBucketName= name_bucket,
            OutputKey = name_job
        )
    except boto3.exceptions.Boto3Error as e:
        print(f'Boto3 error starting transcription: {e}')
        return False

    except Exception as e:
        print(f'Error starting transcription: {e}')
        return False

    return True

def call_aws_get_transcription(client, name_job, client_s3, name_bucket):
    try:
        initial_time = time.time()
        while 1:
            # Get status
            response = client.get_transcription_job(
                TranscriptionJobName = name_job
            )
            time.sleep(5)

            # Get body
            if response['TranscriptionJob']['TranscriptionJobStatus'] != 'IN_PROGRESS':
                transcription = client_s3.get_object(Bucket = name_bucket, Key= name_job)
                transcription = json.loads(transcription['Body'].read().decode('utf-8'))
                break

            elif ((time.time() - initial_time) > 600):
                return None # Exit after 10 min

    except boto3.exceptions.Boto3Error as e:
        print(f'Boto3 error getting file: {e}')
        return None

    except Exception as e:
        print(f'Error getting file: {e}')
        return None

    return transcription

def call_aws_translate(client, sentence, lang_code, lang_target):
    try:
        response = client.translate_text(
            Text=sentence,
            SourceLanguageCode = lang_code,
            TargetLanguageCode = lang_target,
            Settings={
                'Formality': 'INFORMAL',
                'Profanity': 'MASK',
                'Brevity': 'ON'
            }
        )

    except boto3.exceptions.Boto3Error as e:
        print(f'Boto3 error during translation: {e}')
        return None

    return response

def translation_process(client_translate, transcribe):
    # build array of start times
    times = [item["start_time"] for item in transcribe["results"]["items"] if "start_time" in item]
    transcript = transcribe["results"]["transcripts"][0]["transcript"]
    sentences = re.split(re_sentence, transcript)
    word_ptr = 0
    translated_arr = []

    for sentence in sentences:
        response = call_aws_translate(client_translate, sentence, lang_code, lang_target)
        if response != None:
            translated_text = response['TranslatedText']
            translated_arr.append({"start_time": times[word_ptr], "translated": translated_text})
            word_count = len(re.findall(r'\w+', sentence))
            word_ptr += word_count
        else:
            return None

    return translated_arr


## Main
# Variables definition
name_bucket = f'my-bucket-{int(time.time())}'
name_transcr_job = f'my-transcription-job-{int(time.time())}'
re_sentence = """(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s"""
region = 'eu-central-1'
lang_code = 'pt-BR'
lang_target = 'en-US'

# Check input parameter
if len(sys.argv) <= 1:
    print('Please, introduce name of video to transcribe and translate.')
    sys.exit(1)

else:
    name_file = sys.argv[1] # Input parameter for filename
    #name_file = 'Raf01_320.mov'

    # Define clients
    client_s3 = boto3.client('s3')
    client_transcribe = boto3.client('transcribe')
    client_translate = boto3.client('translate')

    # Create S3 bucket
    bucket_created = call_aws_create_bucket(client_s3, name_bucket, region)

    # Update file
    file_uploaded = call_aws_uploadfile(client_s3, name_bucket, name_file)

    # Transcription
    response = call_aws_transcript(client_transcribe, name_transcr_job, name_bucket, name_file, lang_code)
    if response:
        transcribe = call_aws_get_transcription(client_transcribe, name_transcr_job, client_s3, name_bucket)


    if (response == True and transcribe != None):
        # Translate transcription received
        translated_arr = translation_process(client_translate, transcribe)

        # Save transcription and translation into files
        with open('transcribe.json', 'w', encoding= 'utf-8') as transcribe_file, \
            open('translated.json', 'w', encoding='utf-8') as translated_file:
            transcribe_file.write(json.dumps(transcribe, indent = 2))
            translated_file.write(json.dumps(translated_arr, indent=2))

    # Remove transcription job
    if response:
        try:
            client_transcribe.delete_transcription_job(TranscriptionJobName = name_transcr_job)
        except boto3.exceptions.Boto3Error as e:
            print(f'Boto3 error removing transcription job: {e}')

    # Remove all stored file
    if file_uploaded:
        try:
            # Get list of files in bucket
            list_files = client_s3.list_objects(Bucket = name_bucket)
            if 'Contents' in list_files:
                objects_to_delete = [{'Key': file['Key']} for file in list_files['Contents']]
                delete_payload = {'Objects': objects_to_delete}
                # Delete file
                client_s3.delete_objects(Bucket = name_bucket, Delete = delete_payload)

        except boto3.exceptions.Boto3Error as e:
            print(f'Boto3 error removing stored file in bucket: {e}')

        except Exception as e:
            print(f'Error removing stored file in bucket: {e}')

    # Remove bucket
    if bucket_created:
        try:
            client_s3.delete_bucket(Bucket = name_bucket)
        except boto3.exceptions.Boto3Error as e:
            print(f'Boto3 error removing bucket: {e}')