import asyncio
import json
import os
import pyaudio
import wave
from datetime import datetime
from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone
)
from src.utils import ensure_dir_exists

class DeepgramTranscriber:
    def __init__(self, api_key, language="it", ui=None, session_name=None):
        self.api_key = api_key
        self.language = language
        self.ui = ui
        self.session_name = session_name or datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Initialize the Deepgram client with the API key
        self.deepgram = DeepgramClient(api_key)
        self.running = False
        self.completion_event = asyncio.Event()
        self.connection = None
        
        # Audio settings
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        
        # Session data
        self.transcript_data = []
        self.current_timestamp = 0
        
        # Create sessions directory
        self.sessions_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sessions")
        ensure_dir_exists(self.sessions_dir)
        
    async def start(self):
        """Start the transcription process"""
        self.running = True
        
        try:
            # Configure the live transcription options
            options = LiveOptions(
                language=self.language,
                encoding="linear16",
                channels=self.CHANNELS,
                sample_rate=self.RATE,
                model="nova-3",
                smart_format=True,
                interim_results=True,
                utterance_end_ms=1000
            )
            
            # Create the live transcription connection
            self.connection = self.deepgram.listen.live.v("1")
            
            # Set up event handlers
            self.connection.on(LiveTranscriptionEvents.Open, self._on_open)
            self.connection.on(LiveTranscriptionEvents.Close, self._on_close)
            self.connection.on(LiveTranscriptionEvents.Transcript, self._on_transcript)
            self.connection.on(LiveTranscriptionEvents.UtteranceEnd, self._on_utterance_end)
            self.connection.on(LiveTranscriptionEvents.Error, self._on_error)
            
            # Start the connection
            await self.connection.start(options)
            
            # Start audio streaming
            await self._stream_microphone()
            
        except Exception as e:
            if self.ui:
                self.ui.display_error(f"Failed to start transcription: {str(e)}")
            self.running = False
            self.completion_event.set()
    
    async def stop(self):
        """Stop the transcription process"""
        self.running = False
        if self.connection:
            await self.connection.finish()
            self.connection = None
        
        # Save transcript to file
        await self._save_transcript()
        self.completion_event.set()
    
    async def wait_for_completion(self):
        """Wait until the transcription is completed"""
        await self.completion_event.wait()
    
    async def _stream_microphone(self):
        """Stream microphone audio to Deepgram"""
        p = pyaudio.PyAudio()
        
        try:
            stream = p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
            
            if self.ui:
                self.ui.display_message("Microphone is now active and streaming to Deepgram")
            
            while self.running:
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                if self.connection and data and self.running:
                    await self.connection.send(data)
                await asyncio.sleep(0.01)  # Small delay to prevent CPU overuse
                
        except Exception as e:
            if self.ui:
                self.ui.display_error(f"Error in audio stream: {str(e)}")
            self.running = False
            
        finally:
            if 'stream' in locals():
                stream.stop_stream()
                stream.close()
            p.terminate()
    
    # Alternative microphone implementation using Deepgram's built-in Microphone class
async def _stream_microphone_alternative(self):
    """Stream microphone audio to Deepgram using the Microphone class"""
    try:
        # Create microphone instance
        microphone = Microphone(
            self.deepgram,
            self.connection,
            sample_rate=self.RATE,
            channels=self.CHANNELS
        )
        
        if self.ui:
            self.ui.display_message("Microphone is now active and streaming to Deepgram")
        
        # Start streaming from microphone
        await microphone.start()
        
        # Keep running until stopped
        while self.running:
            await asyncio.sleep(0.1)
            
    except Exception as e:
        if self.ui:
            self.ui.display_error(f"Error in microphone stream: {str(e)}")
        self.running = False
        
    finally:
        # Stop microphone if it was started
        if 'microphone' in locals():
            await microphone.stop()
    def _on_open(self):
        """Handle websocket open event"""
        if self.ui:
            self.ui.display_message("Connected to Deepgram")
    
    def _on_close(self):
        """Handle websocket close event"""
        if self.ui:
            self.ui.display_message("Disconnected from Deepgram")
        self.running = False
    
    def _on_transcript(self, transcript):
        """Handle incoming transcript"""
        if not transcript or not transcript.get('channel', {}).get('alternatives'):
            return
        
        # Extract transcript text
        result = transcript['channel']['alternatives'][0]
        text = result.get('transcript', '')
        is_final = transcript.get('is_final', False)
        
        if not text.strip():
            return
        
        # Get timing information
        if 'words' in result and result['words']:
            start = result['words'][0]['start']
            end = result['words'][-1]['end']
            duration = end - start
            # Update timestamp for complete transcripts
            if is_final:
                self.current_timestamp = end
        else:
            start = self.current_timestamp
            duration = 0
        
        # Format timestamp
        timestamp_str = self._format_timestamp(start)
        
        # Store and display transcript
        if is_final:
            self.transcript_data.append({
                "text": text,
                "start": start,
                "end": start + duration,
                "timestamp": timestamp_str
            })
            
            if self.ui:
                self.ui.display_transcript(timestamp_str, text, is_final)
    
    def _on_utterance_end(self, data):
        """Handle utterance end event"""
        if self.ui:
            channel_info = data.get("channel", [0, 1])
            last_word_end = data.get("last_word_end", 0)
            self.ui.display_message(f"[Utterance End Detected at {self._format_timestamp(last_word_end)}]")
    
    def _on_error(self, error):
        """Handle error event"""
        if self.ui:
            self.ui.display_error(f"Deepgram Error: {error}")
    
    def _format_timestamp(self, seconds):
        """Format seconds into MM:SS format"""
        minutes = int(seconds / 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    async def _save_transcript(self):
        """Save the transcript to a markdown file"""
        if not self.transcript_data:
            return
            
        filename = os.path.join(self.sessions_dir, f"{self.session_name}.md")
        
        with open(filename, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"# Transcription Session: {self.session_name}\n\n")
            f.write(f"- **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"- **Language:** {self.language}\n\n")
            f.write("## Transcript\n\n")
            
            # Write transcript entries
            for entry in self.transcript_data:
                f.write(f"**[{entry['timestamp']}]** {entry['text']}\n\n")
                
# Alternative microphone implementation using Deepgram's built-in Microphone class
async def _stream_microphone_alternative(self):
    """Stream microphone audio to Deepgram using the Microphone class"""
    try:
        # Create microphone instance
        microphone = Microphone(
            self.deepgram,
            self.connection,
            sample_rate=self.RATE,
            channels=self.CHANNELS
        )
        
        if self.ui:
            self.ui.display_message("Microphone is now active and streaming to Deepgram")
        
        # Start streaming from microphone
        await microphone.start()
        
        # Keep running until stopped
        while self.running:
            await asyncio.sleep(0.1)
            
    except Exception as e:
        if self.ui:
            self.ui.display_error(f"Error in microphone stream: {str(e)}")
        self.running = False
        
    finally:
        # Stop microphone if it was started
        if 'microphone' in locals():
            await microphone.stop()