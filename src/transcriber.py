import asyncio
import json
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

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('sp34kn0w')

def ensure_dir_exists(path):
    """Ensure a directory exists, creating it if necessary"""
    if not os.path.exists(path):
        os.makedirs(path)

def get_available_microphones():
    """Get a list of available microphone devices"""
    p = pyaudio.PyAudio()
    device_list = []
    
    # Iterate through available devices
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info.get('maxInputChannels') > 0:  # Input device
            device_list.append({
                'index': i,
                'name': device_info['name'],
                'channels': device_info['maxInputChannels'],
                'default': (i == p.get_default_input_device_info().get('index', -1))
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
        
        # Microphone device selection
        self.mic_device_index = None
        self.mic_device_name = "Default Microphone"
        
        if mic_device is not None:
            # If a specific device was requested, try to find it
            try:
                devices = get_available_microphones()
                if isinstance(mic_device, int):
                    # Use device by index
                    for device in devices:
                        if device['index'] == mic_device:
                            self.mic_device_index = mic_device
                            self.mic_device_name = device['name']
                            break
                else:
                    # Search by name (partial match)
                    for device in devices:
                        if mic_device.lower() in device['name'].lower():
                            self.mic_device_index = device['index']
                            self.mic_device_name = device['name']
                            break
            except Exception as e:
                logger.warning(f"Error finding microphone device: {e}")
        
        # Initialize the Deepgram client with the API key
        self.deepgram = DeepgramClient(api_key)
        self.running = False
        self.completion_event = asyncio.Event()
        self.connection = None
        
        # Audio settings
        self.CHANNELS = 1
        self.RATE = 16000
        
        # Session data
        self.transcript_data = []
        self.current_timestamp = 0
        self.audio_cursor = 0
        self.latency_measurements = []
        
        # Create sessions directory
        self.sessions_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sessions")
        ensure_dir_exists(self.sessions_dir)
        
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
            
            # Check audio levels to ensure microphone is working
            await self._check_audio_levels()
            
            # Simulate a transcript to test the display (optional)
            # await self._simulate_test_transcript()
            
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
        self.running = False
        if self.connection:
            try:
                result = self.connection.finish()
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
            self.connection = None
        
        # Report latency statistics
        self._report_latency_stats()
            
        # Save transcript to file
        await self._save_transcript()
        self.completion_event.set()
    
    async def wait_for_completion(self):
        """Wait until the transcription is completed"""
        await self.completion_event.wait()
    
    async def _stream_microphone_deepgram(self):
        """Stream microphone audio using Deepgram's Microphone class"""
        try:
            # Create microphone instance
            microphone = Microphone(
                push_callback=self.connection.send,
                rate=self.RATE,
                channels=self.CHANNELS
            )
            
            if self.ui:
                self.ui.display_message(f"Microphone active: {self.mic_device_name}")
            
            logger.info(f"Microphone streaming started: {self.mic_device_name}")
            
            # Start streaming from microphone
            microphone.start()
            
            # Track audio time
            chunk_duration = 0.1  # Approximate time per chunk in seconds
            
            # Keep running until stopped
            while self.running:
                await asyncio.sleep(0.1)
                self.audio_cursor += chunk_duration
                
        except Exception as e:
            logger.error(f"Error in microphone stream: {str(e)}", exc_info=True)
            if self.ui:
                self.ui.display_error(f"Error in microphone stream: {str(e)}")
            self.running = False
            
        finally:
            # Stop microphone if it was started
            if 'microphone' in locals():
                microphone.finish()
                logger.info("Microphone streaming stopped")
    
    async def _stream_microphone_custom(self):
        """Stream microphone audio using PyAudio with custom device selection"""
        p = pyaudio.PyAudio()
        
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
            if 'stream' in locals():
                stream.stop_stream()
                stream.close()
            p.terminate()
            logger.info("Custom microphone streaming stopped")
            
    async def _check_audio_levels(self, duration=3):
        """Check audio levels to ensure microphone is working"""
        logger.info(f"Checking audio levels for {duration} seconds...")
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
                # Convert bytes to int16 array
                audio_data = np.frombuffer(data, dtype=np.int16)
                # Get max amplitude
                level = np.max(np.abs(audio_data))
                max_level = max(max_level, level)
                await asyncio.sleep(0.001)
                
            # Get average level as percentage of max possible (32767)
            percentage = (max_level / 32767) * 100
            
            if percentage < 1:
                logger.warning(f"Very low audio level detected: {percentage:.1f}%")
                if self.ui:
                    self.ui.display_error(f"WARNING: Very low microphone levels ({percentage:.1f}%). Please speak louder or check microphone.")
            else:
                logger.info(f"Audio level detected: {percentage:.1f}%")
                if self.ui:
                    self.ui.display_message(f"Microphone level: {percentage:.1f}%")
                    
        except Exception as e:
            logger.error(f"Error checking audio levels: {e}")
        finally:
            if 'stream' in locals():
                stream.stop_stream()
                stream.close()
            p.terminate()
    
    async def _simulate_test_transcript(self):
        """Simulate a transcript event to test display functionality"""
        logger.info("Sending simulated transcript to test display...")
        
        # Create a test transcript in the format Deepgram uses
        test_transcript = {
            'type': 'Results',
            'channel': {
                'alternatives': [
                    {
                        'transcript': 'This is a test transcript.',
                        'confidence': 0.95
                    }
                ]
            },
            'is_final': True,
            'start': 0,
            'duration': 2000000  # 2 seconds in microseconds
        }
        
        # Process it using our handler
        self._on_transcript(None, test_transcript)
    
    def _on_open(self, *args, **kwargs):
        """Handle websocket open event"""
        logger.info("Connected to Deepgram")
        if self.ui:
            self.ui.display_message("Connected to Deepgram")
    
    def _on_close(self, *args, **kwargs):
        """Handle websocket close event"""
        logger.info("Disconnected from Deepgram")
        if self.ui:
            self.ui.display_message("Disconnected from Deepgram")
        self.running = False
    
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
                
                # Log the extracted text
                logger.info(f"Transcript: '{text}' (is_final: {is_final})")
                
                # Get translation if available
                translation = None
                if self.translate and hasattr(alternatives[0], 'translation') and alternatives[0].translation:
                    translation = alternatives[0].translation.text
                
                # Calculate and log latency
                latency = self.audio_cursor - end_time
                self.latency_measurements.append(latency)
                
                if len(self.latency_measurements) % 10 == 0:
                    avg_latency = sum(self.latency_measurements[-10:]) / 10
                    logger.info(f"Current latency: {latency:.3f}s, Average (last 10): {avg_latency:.3f}s")
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
            if hasattr(logger, 'debug'):
                try:
                    if 'result' in kwargs:
                        logger.debug(f"Transcript data structure: {dir(kwargs['result'])}")
                except:
                    pass
    
    def _on_utterance_end(self, *args, **kwargs):
        """Handle utterance end event"""
        # Extract data from kwargs or args
        data = None
        if len(args) >= 2:
            data = args[1]
        elif 'data' in kwargs:
            data = kwargs['data']
        else:
            return
            
        if self.ui and data:
            last_word_end = data.get("last_word_end", 0) / 1000000  # convert to seconds
            self.ui.display_message(f"[Utterance End Detected at {self._format_timestamp(last_word_end)}]")
    
    def _on_error(self, *args, **kwargs):
        """Handle error event"""
        # Extract error from kwargs or args
        error = None
        if len(args) >= 2:
            error = args[1]
        elif 'error' in kwargs:
            error = kwargs['error']
        else:
            error = "Unknown error"
            
        logger.error(f"Deepgram Error: {error}")
        if self.ui:
            self.ui.display_error(f"Deepgram Error: {error}")
    
    def _debug_deepgram_response(self, data):
        """Log the structure of a Deepgram response to help debug format issues"""
        try:
            if not data:
                logger.debug("Empty Deepgram response")
                return
                
            # Log the basic structure
            data_type = data.get('type', 'unknown')
            logger.debug(f"Deepgram response type: {data_type}")
            
            # For each key in the response, log its type and first level of content
            for key, value in data.items():
                if key == 'type':
                    continue
                    
                if isinstance(value, dict):
                    logger.debug(f"Key '{key}' is dict with keys: {list(value.keys())}")
                elif isinstance(value, list):
                    logger.debug(f"Key '{key}' is list with {len(value)} items")
                    if value and len(value) > 0:
                        logger.debug(f"First item type: {type(value[0])}")
                else:
                    logger.debug(f"Key '{key}' is {type(value)}: {value}")
                    
        except Exception as e:
            logger.error(f"Error in debug function: {e}")
    
    def _format_timestamp(self, seconds):
        """Format seconds into MM:SS format"""
        minutes = int(seconds / 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def _report_latency_stats(self):
        """Report latency statistics"""
        if not self.latency_measurements:
            return
            
        avg_latency = sum(self.latency_measurements) / len(self.latency_measurements)
        min_latency = min(self.latency_measurements)
        max_latency = max(self.latency_measurements)
        
        logger.info(f"Latency statistics - Avg: {avg_latency:.3f}s, Min: {min_latency:.3f}s, Max: {max_latency:.3f}s")
        
        if self.ui:
            self.ui.display_message(f"Latency statistics - Avg: {avg_latency:.3f}s, Min: {min_latency:.3f}s, Max: {max_latency:.3f}s")
    
    async def _save_transcript(self):
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
            logger.info(f"Saving transcript to {filename}")
            
            with open(filename, 'w', encoding='utf-8') as f:
                # Write header
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
                
                # Write transcript entries
                f.write("## Transcript\n\n")
                for entry in self.transcript_data:
                    f.write(f"**[{entry['timestamp']}]** {entry['text']}\n\n")
                    if "translation" in entry and entry["translation"]:
                        f.write(f"*Translation: {entry['translation']}*\n\n")
                        
            # Verify the file was saved
            if os.path.exists(filename):
                logger.info(f"Transcript successfully saved to {filename}")
            else:
                logger.error(f"Failed to save transcript to {filename}")
                
        except Exception as e:
            logger.error(f"Error saving transcript: {e}", exc_info=True)