import os
import time
import json
import asyncio
import logging
import pyaudio
import numpy as np
from datetime import datetime, timedelta
from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('sp34kn0w')

def get_available_microphones():
    """Get a list of available microphone devices"""
    p = pyaudio.PyAudio()
    devices = []
    
    try:
        # Check how many audio devices are available
        device_count = p.get_device_count()
        default_input = p.get_default_input_device_info()['index']
        
        # Iterate through devices and find input devices (microphones)
        for i in range(device_count):
            try:
                device_info = p.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:  # Input device
                    devices.append({
                        'index': i,
                        'name': device_info['name'],
                        'channels': device_info['maxInputChannels'],
                        'default': i == default_input
                    })
            except Exception:
                pass  # Skip devices that can't be queried
                
    except Exception as e:
        logger.error(f"Error getting microphone devices: {e}")
    finally:
        p.terminate()
        
    return devices

def ensure_dir_exists(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)

class DeepgramTranscriber:
    """Class for handling Deepgram transcription"""
    
    # Audio settings
    RATE = 16000  # Sample rate
    CHANNELS = 1  # Mono
    
    def __init__(self, api_key, language="it", ui=None, session_name=None, model="nova-2", translate=False, mic_device=None):
        """Initialize the transcriber"""
        self.deepgram = DeepgramClient(api_key)
        self.language = language
        self.ui = ui
        self.model = model
        self.translate = translate
        
        # Microphone setup
        self.mic_device_name = "Default Microphone"
        self.mic_device_index = None
        
        if mic_device is not None:
            self._setup_microphone(mic_device)
            
        # Session management
        if session_name is None:
            session_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.session_name = session_name
        self.sessions_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sessions")
        
        # State variables
        self.running = False
        self.paused = False
        self.pause_event = asyncio.Event()
        self.pause_event.set()  # Not paused initially
        self.connection = None
        self.completion_event = asyncio.Event()
        
        # Track audio position for latency calculation
        self.start_time = 0
        self.audio_cursor = 0
        self.current_timestamp = 0
        self.latency_measurements = []
        
        # Store transcript data
        self.transcript_data = []
    
    def _setup_microphone(self, mic_device):
        """Set up the microphone device"""
        devices = get_available_microphones()
        
        # Check if mic_device is an index (int) or name (str)
        if isinstance(mic_device, int):
            # Try to find the device by index
            for device in devices:
                if device['index'] == mic_device:
                    self.mic_device_index = mic_device
                    self.mic_device_name = device['name']
                    break
            else:
                logger.warning(f"Microphone with index {mic_device} not found. Using default.")
        else:
            # Try to find the device by name (partial match)
            for device in devices:
                if mic_device.lower() in device['name'].lower():
                    self.mic_device_index = device['index']
                    self.mic_device_name = device['name']
                    break
            else:
                logger.warning(f"Microphone '{mic_device}' not found. Using default.")
    
    def _format_timestamp(self, seconds):
        """Format timestamp in MM:SS format"""
        minutes = int(seconds / 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    async def check_microphone(self):
        """Check microphone levels before starting transcription"""
        duration = 3
        logger.info(f"Checking audio levels for {duration} seconds...")
        if self.ui:
            self.ui.display_message(f"Checking microphone levels (please speak now for {duration} seconds)...")
        
        # Default result in case of errors
        result = {
            "level": 0.0,
            "is_low": True,
            "message": "Failed to check audio levels"
        }
            
        try:
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
                    # Convert bytes to int16 array
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    # Get max amplitude
                    level = np.max(np.abs(audio_data))
                    max_level = max(max_level, level)
                    await asyncio.sleep(0.001)
                    
                # Get average level as percentage of max possible (32767)
                percentage = (max_level / 32767) * 100
                
                result = {
                    "level": percentage,
                    "is_low": percentage < 1,
                    "message": ""
                }
                
                if percentage < 1:
                    message = f"WARNING: Very low microphone levels ({percentage:.1f}%). Please speak louder or check microphone."
                    logger.warning(f"Very low audio level detected: {percentage:.1f}%")
                    if self.ui:
                        self.ui.display_error(message)
                    result["message"] = message
                else:
                    message = f"Microphone level: {percentage:.1f}%"
                    logger.debug(f"Audio level detected: {percentage:.1f}%")
                    if self.ui:
                        self.ui.display_message(message)
                    result["message"] = message
                        
            except Exception as e:
                logger.error(f"Error checking audio levels: {e}")
                if self.ui:
                    self.ui.display_error(f"Error checking audio levels: {e}")
                result["message"] = f"Error: {str(e)}"
            finally:
                if 'stream' in locals():
                    stream.stop_stream()
                    stream.close()
                p.terminate()
                
            return result
                    
        except Exception as e:
            logger.error(f"Critical error checking audio: {e}")
            if self.ui:
                self.ui.display_error(f"Critical error checking audio: {e}")
            return result  # Return default result with error info


    async def start(self):
        """Start the transcription process"""
        self.running = True
        self.start_time = time.time()
        
        try:
            # Configure the live transcription options
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
            
            # Add translation if requested
            if self.translate:
                options["translate"] = True
            
            logger.info(f"Starting transcription with options: {options}")
            
            # Create the live transcription connection
            self.connection = self.deepgram.listen.live.v("1")
            
            # Set up event handlers with flexible parameter handling
            self.connection.on(LiveTranscriptionEvents.Open, self._on_open)
            self.connection.on(LiveTranscriptionEvents.Close, self._on_close)
            self.connection.on(LiveTranscriptionEvents.Transcript, self._on_transcript)
            self.connection.on(LiveTranscriptionEvents.UtteranceEnd, self._on_utterance_end)
            self.connection.on(LiveTranscriptionEvents.Error, self._on_error)
            
            # Start the connection with proper await handling
            result = self.connection.start(options)
            if asyncio.iscoroutine(result):
                await result
            
            if self.ui:
                self.ui.display_message("Connected to Deepgram")
            
            # Choose the appropriate microphone streaming method
            if self.mic_device_index is not None:
                await self._stream_microphone_custom()
            else:
                await self._stream_microphone_deepgram()
            
        except Exception as e:
            logger.error(f"Failed to start transcription: {str(e)}", exc_info=True)
            if self.ui:
                self.ui.display_error(f"Failed to start transcription: {str(e)}")
            self.running = False
            self.completion_event.set()
    
    async def stop(self):
        """Stop the transcription process"""
        logger.info("Stopping transcription...")
        
        self.running = False
        
        # Close deepgram connection if active
        if self.connection:
            try:
                # Check if connection.finish() returns a coroutine
                result = self.connection.finish()
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
        
        logger.info("Disconnected from Deepgram")
        if self.ui:
            self.ui.display_message("Disconnected from Deepgram")
        
        # Log latency statistics
        if self.latency_measurements:
            avg_latency = sum(self.latency_measurements) / len(self.latency_measurements)
            min_latency = min(self.latency_measurements)
            max_latency = max(self.latency_measurements)
            logger.info(f"Latency statistics - Avg: {avg_latency:.3f}s, Min: {min_latency:.3f}s, Max: {max_latency:.3f}s")
            if self.ui:
                self.ui.display_message(f"Latency statistics - Avg: {avg_latency:.3f}s, Min: {min_latency:.3f}s, Max: {max_latency:.3f}s")
        
        # Save the transcript
        await self._save_transcript()
        
        # Signal completion
        self.completion_event.set()
    
    def pause(self):
        """Pause the transcription"""
        if not self.paused and self.running:
            logger.info("Transcription paused")
            self.paused = True
            self.pause_event.clear()
            
            if self.ui:
                self.ui.set_paused(True)
            
            # Save current progress to file
            loop = asyncio.get_event_loop()
            loop.create_task(self._save_transcript(append_mode=True))

    def resume(self):
        """Resume the transcription"""
        if self.paused and self.running:
            logger.info("Transcription resumed")
            self.paused = False
            self.pause_event.set()
            
            if self.ui:
                self.ui.set_paused(False)
    
    async def wait_for_completion(self):
        """Wait until the transcription is stopped"""
        await self.completion_event.wait()
    
    def _on_open(self, *args, **kwargs):
        """Handle connection open"""
        logger.info("Connected to Deepgram")
    
    def _on_close(self, *args, **kwargs):
        """Handle connection close"""
        logger.info("Disconnected from Deepgram")
        if self.ui:
            self.ui.display_message("Disconnected from Deepgram")
    
    def _on_error(self, *args, **kwargs):
        """Handle error"""
        error = kwargs.get('error', "Unknown error")
        logger.error(f"Deepgram error: {error}")
        if self.ui:
            self.ui.display_error(f"Deepgram error: {error}")
    
    def _on_utterance_end(self, *args, **kwargs):
        """Handle end of utterance"""
        if 'result' in kwargs:
            result = kwargs['result']
            last_word_end = getattr(result, 'last_word_end', None)
            if last_word_end:
                logger.debug(f"Utterance end at {last_word_end}s")
    
    def _on_transcript(self, *args, **kwargs):
        """Handle incoming transcript"""
        try:
            # In Deepgram SDK v4.1.0, the transcript is in kwargs['result']
            if 'result' in kwargs:
                result = kwargs['result']
                
                # Check if this is a valid result with transcript
                if not hasattr(result, 'channel') or not hasattr(result.channel, 'alternatives'):
                    return
                    
                alternatives = result.channel.alternatives
                if not alternatives or len(alternatives) == 0:
                    return
                    
                text = alternatives[0].transcript
                is_final = result.is_final
                    
                # Skip empty transcripts
                if not text or not text.strip():
                    return
                    
                # Get timing information - convert microseconds to seconds
                start_time = result.start / 1000000 if result.start > 1000 else result.start
                duration = result.duration / 1000000 if result.duration > 1000 else result.duration
                end_time = start_time + duration
                
                # Format timestamp
                timestamp_str = self._format_timestamp(start_time)
                
                # Log transcript data ONLY for debug logging - don't use logger.info for these
                if logging.getLogger().level <= logging.DEBUG:
                    print(f"{datetime.now().strftime('%H:%M:%S')} - DEBUG - Transcript: '{text}' (is_final: {is_final})")
                
                # Get translation if available
                translation = None
                if self.translate and hasattr(alternatives[0], 'translation') and alternatives[0].translation:
                    translation = alternatives[0].translation.text
                
                # Calculate and log latency
                latency = self.audio_cursor - end_time
                self.latency_measurements.append(latency)
                
                if len(self.latency_measurements) % 10 == 0:
                    avg_latency = sum(self.latency_measurements[-10:]) / 10
                    # Log latency stats ONLY in debug mode
                    if logging.getLogger().level <= logging.DEBUG:
                        print(f"{datetime.now().strftime('%H:%M:%S')} - DEBUG - Current latency: {latency:.3f}s, Average (last 10): {avg_latency:.3f}s")
                    if hasattr(self.ui, 'display_latency'):
                        self.ui.display_latency(latency, avg_latency)
                
                # Update timestamp for complete transcripts
                if is_final:
                    self.current_timestamp = end_time
                
                # Store and display transcript
                if is_final:
                    entry = {
                        "text": text,
                        "start": start_time,
                        "end": end_time,
                        "timestamp": timestamp_str
                    }
                    
                    # Add translation if available
                    if translation:
                        entry["translation"] = translation
                        
                    self.transcript_data.append(entry)
                    
                    if self.ui:
                        self.ui.display_transcript(timestamp_str, text, is_final, translation)
                elif self.ui:
                    # Show interim results but don't store them
                    self.ui.display_transcript(timestamp_str, text, is_final, translation)
                    
        except Exception as e:
            logger.error(f"Error processing transcript: {str(e)}", exc_info=True)
            if logging.getLogger().level <= logging.DEBUG:
                try:
                    if 'result' in kwargs:
                        print(f"{datetime.now().strftime('%H:%M:%S')} - DEBUG - Transcript data structure: {dir(kwargs['result'])}")
                except:
                    pass
    
    async def _stream_microphone_custom(self):
        """Stream microphone audio using PyAudio with custom device selection"""
        p = pyaudio.PyAudio()
        stream = None
        
        try:
            # Open the selected device
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
            
            logger.info(f"Custom microphone streaming started: {self.mic_device_name}")
            
            # Stream audio data
            while self.running:
                # Check if paused - if so, wait until resumed
                if self.paused:
                    if stream:
                        # Stop the stream when paused
                        stream.stop_stream()
                        stream = None
                        logger.debug("Microphone stream stopped while paused")
                    
                    # Wait for resume signal
                    await asyncio.sleep(0.2)
                    
                    # If resumed, reopen the stream
                    if not self.paused and self.running:
                        stream = p.open(
                            format=pyaudio.paInt16,
                            channels=self.CHANNELS,
                            rate=self.RATE,
                            input=True,
                            input_device_index=self.mic_device_index,
                            frames_per_buffer=1024
                        )
                        logger.debug("Microphone stream restarted after pause")
                    
                    continue
                
                # Ensure we have a stream
                if stream is None and not self.paused:
                    stream = p.open(
                        format=pyaudio.paInt16,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        input_device_index=self.mic_device_index,
                        frames_per_buffer=1024
                    )
                
                # Only read data and send it if not paused
                if stream and not self.paused:
                    data = stream.read(1024, exception_on_overflow=False)
                    if self.connection and data and self.running:
                        # Don't await the send() method - it's not a coroutine
                        self.connection.send(data)
                    
                    # Track audio cursor for latency calculation
                    chunk_duration = 1024 / self.RATE  # Duration in seconds
                    self.audio_cursor += chunk_duration
                
                await asyncio.sleep(0.001)  # Short sleep to prevent CPU overload
                
        except Exception as e:
            logger.error(f"Error in custom microphone stream: {str(e)}", exc_info=True)
            if self.ui:
                self.ui.display_error(f"Error in microphone stream: {str(e)}")
            self.running = False
            
        finally:
            if stream:
                stream.stop_stream()
                stream.close()
            p.terminate()
            logger.info("Custom microphone streaming stopped")
    
    async def _stream_microphone_deepgram(self):
        """Stream microphone audio using Deepgram's Microphone class"""
        try:
            # Create microphone instance only if not paused
            microphone = None
            if not self.paused:
                microphone = Microphone(
                    push_callback=self.connection.send,
                    rate=self.RATE,
                    channels=self.CHANNELS
                )
                microphone.start()
                
                if self.ui:
                    self.ui.display_message(f"Microphone active: {self.mic_device_name}")
                
                logger.info(f"Microphone streaming started: {self.mic_device_name}")
            
            # Keep running until stopped
            while self.running:
                # Check pause state
                if self.paused:
                    # If paused and mic is active, stop it
                    if microphone:
                        microphone.finish()
                        microphone = None
                        logger.debug("Deepgram microphone stopped while paused")
                    
                    # Wait for resume event with timeout
                    try:
                        await asyncio.wait_for(self.pause_event.wait(), timeout=0.5)
                        
                        # When resumed, create a new microphone
                        if not self.paused and self.running:
                            microphone = Microphone(
                                push_callback=self.connection.send,
                                rate=self.RATE,
                                channels=self.CHANNELS
                            )
                            microphone.start()
                            logger.debug("Deepgram microphone restarted after pause")
                    except asyncio.TimeoutError:
                        # Just continue the loop to check running state
                        pass
                        
                else:
                    # If not paused but no microphone, create one
                    if not microphone:
                        microphone = Microphone(
                            push_callback=self.connection.send,
                            rate=self.RATE,
                            channels=self.CHANNELS
                        )
                        microphone.start()
                    
                    # Still track time for latency calculation
                    await asyncio.sleep(0.1)
                    self.audio_cursor += 0.1  # Approximate time per chunk
                    
        except Exception as e:
            logger.error(f"Error in microphone stream: {str(e)}", exc_info=True)
            if self.ui:
                self.ui.display_error(f"Error in microphone stream: {str(e)}")
            self.running = False
            
        finally:
            # Stop microphone if it was started
            if 'microphone' in locals() and microphone:
                microphone.finish()
                logger.info("Microphone streaming stopped")
    
    async def _save_transcript(self, append_mode=False):
        """Save the transcript to a markdown file"""
        try:
            # Log the transcript data for debugging
            logger.debug(f"Transcript data to save: {len(self.transcript_data)} entries")
            
            if not self.transcript_data:
                logger.warning("No transcript data to save")
                return
                
            # Ensure the directory exists
            ensure_dir_exists(self.sessions_dir)
            
            filename = os.path.join(self.sessions_dir, f"{self.session_name}.md")
            mode = 'a' if append_mode else 'w'
            logger.info(f"Saving transcript to {filename}")
            
            with open(filename, mode, encoding='utf-8') as f:
                if not append_mode:
                    # Write header (only when creating a new file)
                    f.write(f"# Transcription Session: {self.session_name}\n\n")
                    f.write(f"- **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"- **Language:** {self.language}\n")
                    f.write(f"- **Model:** {self.model}\n")
                    f.write(f"- **Microphone:** {self.mic_device_name}\n")
                    f.write(f"- **Translation:** {'Enabled' if self.translate else 'Disabled'}\n\n")
                    
                    # Write latency statistics
                    if self.latency_measurements:
                        avg_latency = sum(self.latency_measurements) / len(self.latency_measurements)
                        min_latency = min(self.latency_measurements)
                        max_latency = max(self.latency_measurements)
                        f.write(f"## Latency Statistics\n\n")
                        f.write(f"- **Average:** {avg_latency:.3f} seconds\n")
                        f.write(f"- **Minimum:** {min_latency:.3f} seconds\n")
                        f.write(f"- **Maximum:** {max_latency:.3f} seconds\n\n")
                    
                    # Start transcript section
                    f.write("## Transcript\n\n")
                else:
                    # In append mode, add a timestamp marker
                    f.write(f"\n--- Saved at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n\n")
                
                # Write transcript entries
                for entry in self.transcript_data:
                    timestamp = f"**[{entry['timestamp']}]** " if self.ui.show_timestamps else ""
                    f.write(f"{timestamp}{entry['text']}\n\n")
                    if "translation" in entry and entry["translation"]:
                        f.write(f"*Translation: {entry['translation']}*\n\n")
                        
            # Verify the file was saved
            if os.path.exists(filename):
                logger.info(f"Transcript successfully saved to {filename}")
                if self.ui and append_mode:
                    self.ui.display_message(f"Transcript snapshot saved to {filename}")
            else:
                logger.error(f"Failed to save transcript to {filename}")
                
        except Exception as e:
            logger.error(f"Error saving transcript: {e}", exc_info=True)