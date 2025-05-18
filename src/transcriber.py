import asyncio
import os
import time
import logging
import pyaudio
import numpy as np
from datetime import datetime
from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('sp34kn0w')

def ensure_dir_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

def get_available_microphones():
    p = pyaudio.PyAudio()
    device_list = []
    default_index = None
    try:
        default_index = p.get_default_input_device_info().get('index', None)
    except Exception:
        pass
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info.get('maxInputChannels', 0) > 0:
            device_list.append({
                'index': i,
                'name': info['name'],
                'channels': info['maxInputChannels'],
                'default': (i == default_index)
            })
    p.terminate()
    return device_list

class DeepgramTranscriber:
    def __init__(self, api_key, language="it", ui=None, session_name=None, model="nova-2", translate=False, mic_device=None):
        self.api_key = api_key
        self.language = language
        self.ui = ui
        self.session_name = session_name or datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.model = model
        self.translate = translate

        self.mic_device_index = None
        self.mic_device_name = "Default Microphone"
        if mic_device is not None:
            devices = get_available_microphones()
            if isinstance(mic_device, int):
                for device in devices:
                    if device['index'] == mic_device:
                        self.mic_device_index = mic_device
                        self.mic_device_name = device['name']
                        break
            else:
                for device in devices:
                    if mic_device.lower() in device['name'].lower():
                        self.mic_device_index = device['index']
                        self.mic_device_name = device['name']
                        break

        self.deepgram = DeepgramClient(api_key)
        self.running = False
        self.completion_event = asyncio.Event()
        self.connection = None

        self.CHANNELS = 1
        self.RATE = 16000

        self.transcript_data = []
        self.current_timestamp = 0
        self.audio_cursor = 0
        self.latency_measurements = []

        self.paused = False
        self.pause_event = asyncio.Event()
        self.pause_event.set()

        self.sessions_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sessions")
        ensure_dir_exists(self.sessions_dir)

    async def start(self):
        self.running = True
        self.start_time = time.time()
        try:
            options = LiveOptions(
                language=self.language,
                encoding="linear16",
                channels=self.CHANNELS,
                sample_rate=self.RATE,
                model=self.model,
                smart_format=True,
                interim_results=True,
                utterance_end_ms=1000
            )
            if self.translate:
                options["translate"] = True

            #logger.info(f"Starting transcription with options: {options}")
            self.connection = self.deepgram.listen.live.v("1")
            self.connection.on(LiveTranscriptionEvents.Open, self._on_open)
            self.connection.on(LiveTranscriptionEvents.Close, self._on_close)
            self.connection.on(LiveTranscriptionEvents.Transcript, self._on_transcript)
            self.connection.on(LiveTranscriptionEvents.UtteranceEnd, self._on_utterance_end)
            self.connection.on(LiveTranscriptionEvents.Error, self._on_error)

            result = self.connection.start(options)
            if asyncio.iscoroutine(result):
                await result

            if self.mic_device_index is not None:
                await self._stream_microphone_custom()
            else:
                await self._stream_microphone_deepgram()

        except Exception as e:
            #logger.error(f"Failed to start transcription: {str(e)}", exc_info=True)
            if self.ui:
                self.ui.display_error(f"Failed to start transcription: {str(e)}")
            self.running = False
            self.completion_event.set()
        if self.ui:
            self.ui.stop()

    async def stop(self):
        self.running = False
        if self.connection:
            try:
                result = self.connection.finish()
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                #logger.error(f"Error closing connection: {e}")
                if self.ui:
                    self.ui.display_error(f"Error closing connection: {e}")
            self.connection = None
        self._report_latency_stats()
        await self._save_transcript()
        self.completion_event.set()

    async def wait_for_completion(self):
        await self.completion_event.wait()

    def pause(self):
        if not self.paused and self.running:
            #logger.info("Transcription paused")
            self.paused = True
            self.pause_event.clear()
            if self.ui:
                self.ui.set_paused(True)
                self.ui.display_message("Transcription paused. Press Ctrl+R to resume.")
            asyncio.create_task(self._save_transcript(append_mode=True))

    def resume(self):
        if self.paused and self.running:
            #logger.info("Transcription resumed")
            self.paused = False
            self.pause_event.set()
            if self.ui:
                self.ui.set_paused(False)
                self.ui.display_message("Transcription resumed")

    async def _stream_microphone_deepgram(self):
        try:
            microphone = Microphone(
                push_callback=self.connection.send,
                rate=self.RATE,
                channels=self.CHANNELS
            )
            if self.ui:
                self.ui.display_message(f"Microphone active: {self.mic_device_name}")
            #logger.info(f"Microphone streaming started: {self.mic_device_name}")
            microphone.start()
            chunk_duration = 0.1
            while self.running:
                if self.paused:
                    microphone.finish()
                    await self.pause_event.wait()
                    if self.running:
                        microphone = Microphone(
                            push_callback=self.connection.send,
                            rate=self.RATE,
                            channels=self.CHANNELS
                        )
                        microphone.start()
                await asyncio.sleep(0.1)
                self.audio_cursor += chunk_duration
        except Exception as e:
            #logger.error(f"Error in microphone stream: {str(e)}", exc_info=True)
            if self.ui:
                self.ui.display_error(f"Error in microphone stream: {str(e)}")
            self.running = False
        finally:
            if 'microphone' in locals():
                microphone.finish()
                #logger.info("Microphone streaming stopped")

    async def _stream_microphone_custom(self):
        p = pyaudio.PyAudio()
        try:
            stream = p.open(
                format=pyaudio.paInt16,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                input_device_index=self.mic_device_index,
                frames_per_buffer=1024
            )
            if self.ui:
                self.ui.display_message(f"Microphone active: {self.mic_device_name}")
            #logger.info(f"Custom microphone streaming started: {self.mic_device_name}")
            while self.running:
                if self.paused:
                    await asyncio.sleep(0.1)
                    continue
                data = stream.read(1024, exception_on_overflow=False)
                if self.connection and data and self.running:
                    self.connection.send(data)
                chunk_duration = 1024 / self.RATE
                self.audio_cursor += chunk_duration
                await asyncio.sleep(0.001)
        except Exception as e:
            #logger.error(f"Error in custom microphone stream: {str(e)}", exc_info=True)
            if self.ui:
                self.ui.display_error(f"Error in microphone stream: {str(e)}")
            self.running = False
        finally:
            if 'stream' in locals():
                stream.stop_stream()
                stream.close()
            p.terminate()
            #logger.info("Custom microphone streaming stopped")

    async def check_microphone(self):
        duration = 3
        #logger.info(f"Checking audio levels for {duration} seconds...")
        if self.ui:
            self.ui.display_message(f"Checking microphone levels (please speak now for {duration} seconds)...")
        p = pyaudio.PyAudio()
        try:
            stream = p.open(
                format=pyaudio.paInt16,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                input_device_index=self.mic_device_index,
                frames_per_buffer=1024
            )
            max_level = 0
            for _ in range(int(duration * self.RATE / 1024)):
                data = stream.read(1024, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16)
                level = np.max(np.abs(audio_data))
                max_level = max(max_level, level)
                await asyncio.sleep(0.001)
            percentage = (max_level / 32767) * 100
            result = {
                "level": percentage,
                "is_low": percentage < 1,
                "message": ""
            }
            if percentage < 1:
                message = f"WARNING: Very low microphone levels ({percentage:.1f}%). Please speak louder or check microphone."
                #logger.warning(f"Very low audio level detected: {percentage:.1f}%")
                if self.ui:
                    self.ui.display_error(message)
                result["message"] = message
            else:
                message = f"Microphone level: {percentage:.1f}%"
                #logger.info(f"Audio level detected: {percentage:.1f}%")
                if self.ui:
                    self.ui.display_message(message)
                result["message"] = message
            return result
        except Exception as e:
            #logger.error(f"Error checking audio levels: {e}")
            if self.ui:
                self.ui.display_error(f"Error checking audio levels: {e}")
            return {"level": 0, "is_low": True, "message": f"Error: {str(e)}"}
        finally:
            if 'stream' in locals():
                stream.stop_stream()
                stream.close()
            p.terminate()

    def _on_open(self, *args, **kwargs):
        #logger.info("Connected to Deepgram")
        if self.ui:
            self.ui.display_message("Connected to Deepgram")

    def _on_close(self, *args, **kwargs):
        #logger.info("Disconnected from Deepgram")
        if self.ui:
            self.ui.display_message("Disconnected from Deepgram")
        self.running = False

    def _on_transcript(self, *args, **kwargs):
        try:
            result = kwargs.get('result', None)
            if not result or not hasattr(result, 'channel') or not hasattr(result.channel, 'alternatives'):
                return
            alternatives = result.channel.alternatives
            if not alternatives or len(alternatives) == 0:
                return
            text = alternatives[0].transcript
            is_final = result.is_final
            if not text or not text.strip():
                return
            start_time = result.start / 1000000 if result.start > 1000 else result.start
            duration = result.duration / 1000000 if result.duration > 1000 else result.duration
            end_time = start_time + duration
            timestamp_str = self._format_timestamp(start_time)
            translation = None
            if self.translate and hasattr(alternatives[0], 'translation') and alternatives[0].translation:
                translation = alternatives[0].translation.text
            latency = self.audio_cursor - end_time
            self.latency_measurements.append(latency)
            if len(self.latency_measurements) % 10 == 0:
                avg_latency = sum(self.latency_measurements[-10:]) / 10
                #logger.info(f"Current latency: {latency:.3f}s, Average (last 10): {avg_latency:.3f}s")
                if hasattr(self.ui, 'display_latency'):
                    self.ui.display_latency(latency, avg_latency)
            if is_final:
                self.current_timestamp = end_time
            if is_final:
                entry = {
                    "text": text,
                    "start": start_time,
                    "end": end_time,
                    "timestamp": timestamp_str
                }
                if translation:
                    entry["translation"] = translation
                self.transcript_data.append(entry)
            if self.ui:
                self.ui.display_transcript(timestamp_str, text, is_final, translation)
        except Exception as e:
            #logger.error(f"Error processing transcript: {str(e)}", exc_info=True)
            if self.ui:
                self.ui.display_error(f"Error processing transcript: {str(e)}")
    def _on_utterance_end(self, *args, **kwargs):
        data = None
        if len(args) >= 2:
            data = args[1]
        elif 'data' in kwargs:
            data = kwargs['data']
        else:
            return
        if self.ui and data:
            last_word_end = data.get("last_word_end", 0) / 1000000
            self.ui.display_message(f"[Utterance End Detected at {self._format_timestamp(last_word_end)}]")

    def _on_error(self, *args, **kwargs):
        error = None
        if len(args) >= 2:
            error = args[1]
        elif 'error' in kwargs:
            error = kwargs['error']
        else:
            error = "Unknown error"
        #logger.error(f"Deepgram Error: {error}")
        if self.ui:
            self.ui.display_error(f"Deepgram Error: {error}")

    def _format_timestamp(self, seconds):
        minutes = int(seconds / 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def _report_latency_stats(self):
        if not self.latency_measurements:
            return
        avg_latency = sum(self.latency_measurements) / len(self.latency_measurements)
        min_latency = min(self.latency_measurements)
        max_latency = max(self.latency_measurements)
        #logger.info(f"Latency statistics - Avg: {avg_latency:.3f}s, Min: {min_latency:.3f}s, Max: {max_latency:.3f}s")
        if self.ui:
            self.ui.display_message(f"Latency statistics - Avg: {avg_latency:.3f}s, Min: {min_latency:.3f}s, Max: {max_latency:.3f}s")

    async def _save_transcript(self, append_mode=False):
        try:
            if not self.transcript_data:
                #logger.warning("No transcript data to save")
                return
            ensure_dir_exists(self.sessions_dir)
            filename = os.path.join(self.sessions_dir, f"{self.session_name}.md")
            mode = 'a' if append_mode else 'w'
            #logger.info(f"Saving transcript to {filename} (mode: {mode})")
            with open(filename, mode, encoding='utf-8') as f:
                if not append_mode:
                    f.write(f"# Transcription Session: {self.session_name}\n\n")
                    f.write(f"- **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"- **Language:** {self.language}\n")
                    f.write(f"- **Model:** {self.model}\n")
                    f.write(f"- **Microphone:** {self.mic_device_name}\n")
                    f.write(f"- **Translation:** {'Enabled' if self.translate else 'Disabled'}\n\n")
                    if self.latency_measurements:
                        avg_latency = sum(self.latency_measurements) / len(self.latency_measurements)
                        min_latency = min(self.latency_measurements)
                        max_latency = max(self.latency_measurements)
                        f.write(f"## Latency Statistics\n\n")
                        f.write(f"- **Average:** {avg_latency:.3f} seconds\n")
                        f.write(f"- **Minimum:** {min_latency:.3f} seconds\n")
                        f.write(f"- **Maximum:** {max_latency:.3f} seconds\n\n")
                    f.write("## Transcript\n\n")
                else:
                    f.write(f"\n--- Saved at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n\n")
                for entry in self.transcript_data:
                    timestamp = f"**[{entry['timestamp']}]** " if hasattr(self.ui, 'show_timestamps') and self.ui.show_timestamps else ""
                    f.write(f"{timestamp}{entry['text']}\n\n")
                    if "translation" in entry and entry["translation"]:
                        f.write(f"*Translation: {entry['translation']}*\n\n")
            if os.path.exists(filename):
                #logger.info(f"Transcript successfully saved to {filename}")
                if self.ui and append_mode:
                    self.ui.display_message(f"Transcript snapshot saved to {filename}")
            else:
                #logger.error(f"Failed to save transcript to {filename}")
                if self.ui:
                    self.ui.display_error(f"Failed to save transcript to {filename}")
        except Exception as e:
            if self.ui:
                self.ui.display_error(f"Error saving transcript: {e}")
            #logger.error(f"Error saving transcript: {e}", exc_info=True)