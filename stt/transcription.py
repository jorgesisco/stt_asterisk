# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from queue import Queue
from threading import Thread

from google.cloud import speech
from google.cloud.speech import RecognitionConfig, StreamingRecognitionConfig, StreamingRecognizeRequest

from .output import Output

LINEAR16 = RecognitionConfig.AudioEncoding.LINEAR16
MULAW = RecognitionConfig.AudioEncoding.MULAW

_GOOGLE_SPEECH_CREDS_FILENAME = '/app/softphone_app/pysterisk/helpers/credentials.json'
_DONE = object()


class Transcriber:

    def __init__(self, language, codec, sample_rate):
        self._streaming_config = StreamingRecognitionConfig(
        config=RecognitionConfig(
            encoding=codec,
            sample_rate_hertz=sample_rate,
            language_code=language,
        ),
)

        self._client = speech.SpeechClient.from_service_account_file(
            filename=_GOOGLE_SPEECH_CREDS_FILENAME,
        )
        self._queue = Queue()
        self._thread = Thread(target=self._transcribe)
        self._output = Output()

    def start(self):
        self._thread.start()

    def stop(self):
        self._queue.put_nowait(_DONE)
        self._thread.join()

    def push(self, data):
        self._queue.put_nowait(data)

    def _transcribe(self):
        step = 64 * 1024
        transcribe_threshold = step
        buffer = b''
        while True:
            data = self._queue.get()
            try:
                if data == _DONE:
                    return
                buffer += data
                written = len(buffer)
                if written >= transcribe_threshold:
                    transcribed = self._do_transcription(buffer)
                    transcribe_threshold = written + step
                    self._output.write(transcribed)
            finally:
                self._queue.task_done()

    def _do_transcription(self, data):
        logging.debug(f'Sending {len(data)} to the speech API')
        request = StreamingRecognizeRequest(audio_content=data)
        output = '\n'

        responses = self._client.streaming_recognize(self._streaming_config, [request])
        for response in responses:
            for result in response.results:
                if not result.is_final:
                    continue
            output += f'{result.alternatives[0].transcript}'

        logging.debug(f'final output: {output}')
        return output
