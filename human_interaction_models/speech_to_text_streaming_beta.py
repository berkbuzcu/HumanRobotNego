from __future__ import division

import sys
import itertools

import pyaudio
import queue

from google.api_core import exceptions

from google.cloud import speech_v1 

class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk  # 100 ms.
        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            channels=1,
            rate=self._rate,
            input=True,
            input_device_index=0,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self.closed = True
        try: 
            self._audio_stream.stop_stream()
            self._audio_stream.close()
            self._buff.put(None)
            self._audio_interface.terminate()
        except OSError as e:
            print(e)

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)


class SpeechStreamingRecognizerBeta:
    def __init__(self, domain_keywords):
        self.domain_keywords = domain_keywords
        self.set_stream_config()
        self.finished = False

    def listen_print_loop(self, responses):
        """Iterates through server responses and prints them.

        The responses passed is a generator that will block until a response
        is provided by the server.

        Each response may contain multiple results, and each result may contain
        multiple alternatives.  Here we
        print only the transcription for the top alternative of the top result.

        In this case, responses are provided for interim results as well. If the
        response is an interim one, print a line feed at the end of it, to allow
        the next result to overwrite it, until the response is a final one. For the
        final one, print a newline to preserve the finalized transcription.
        """
        num_chars_printed = 0
        for response in responses:
            if not response.results:
                continue

            # The `results` list is consecutive. For streaming, we only care about
            # the first result being considered, since once it's `is_final`, it
            # moves on to considering the next utterance.
            result = response.results[0]
            if not result.alternatives:
                continue

            # Display the transcription of the top alternative.
            transcript = result.alternatives[0].transcript
            transcript = transcript.replace("for", "four")
            transcript = transcript.replace("For", "four")
            transcript = transcript.replace("tree", "three")

            # Display interim results, but with a carriage return at the end of the
            # line, so subsequent lines will overwrite them.
            #
            # If the previous result was longer than this one, we need to print
            # some extra spaces to overwrite the previous result
            overwrite_chars = " " * (num_chars_printed - len(transcript))

            if not result.is_final:
                sys.stdout.write(transcript + overwrite_chars + "\r")
                sys.stdout.flush()

                num_chars_printed = len(transcript)
            else:
                num_chars_printed = 0
                return transcript + overwrite_chars

    def set_stream_config(self):
        # See http://g.co/cloud/speech/docs/languages
        # for a list of supported languages.
        language_code = "en-US"  # a BCP-47 language tag

        # Prepare context for domain keywords and numbers.
        list_of_numbers = ["one", "two", "three", "four", "zero", "Four", "Zero", "Two", "Three"]
        domain_contexts_element = {"phrases": self.domain_keywords + list_of_numbers + ["boat"], "boost": 5.0} # , "boost": 45.0

        negotiation_phrases = [
            "want",
            #"except the",
            "all the remaining",
            #"except",
            "that's it",
            "and",
            "take",
            "all of them",
            "want",
            "would like to",
            "would like",
            "want to",
            "need to",
            "like to",
            "rest is yours",
            "you can have the rest",
            "rest",
            "offer",
            "accept",
            "give me",
            "all remainings",
            "all remaining",
            #"deal",
            #"yes",
            "agree",
            "everything",
            "you can",
            "I can give",
        ]

        negotiation_contexts_element = {
            "phrases": negotiation_phrases,
            "boost": 2.0,
        }

        speech_contexts = [domain_contexts_element, negotiation_contexts_element]

        self.client = speech_v1.SpeechClient()

        config = speech_v1.types.RecognitionConfig(
            speech_contexts=speech_contexts,
            encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
            # enable_automatic_punctuation=True,
            use_enhanced=True,
            sample_rate_hertz=44100,
            max_alternatives=10,
            language_code=language_code,
        )
        self.streaming_config = speech_v1.types.StreamingRecognitionConfig(
            config=config, interim_results=True
        )

    def terminate_stream(self):
        self.stream.closed = True

    def listen_and_convert_to_text(self):
        with MicrophoneStream(rate=44100, chunk=int(44100 / 10)) as self.stream:
            try:
                audio_generator = self.stream.generator()
                # print("Listening")
                requests = (
                    speech_v1.types.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator
                )
                
                responses = self.client.streaming_recognize(
                    self.streaming_config, requests, timeout=999
                )
                # Now, put the transcription responses to use.
                return self.listen_print_loop(responses)

            except exceptions.DeadlineExceeded as e:
                print("Exception occurred - {}".format(str(e)))
                return "timeouterror"

            except exceptions.Cancelled as e:
                print("Exception occurred - {}".format(str(e)))
                return "finished"


if __name__ == "__main__":
    from utility_space import UtilitySpace
    domain = UtilitySpace("D:\PythonProjects\Human_Robot_Nego\HANT\Domains\Holiday_A\Berk\Agent.xml")
    streamer = SpeechStreamingRecognizerBeta(domain.issue_values_list)
    while(True):
        streamer.listen_and_convert_to_text()
