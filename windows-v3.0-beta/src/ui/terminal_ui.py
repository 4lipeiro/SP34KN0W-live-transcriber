import os
import sys
import re
import time
import curses
import shutil
from datetime import datetime
from threading import Thread, Lock

# ASCII Banner
BANNER = r'''
    
    ███████ ██████  ██████  ██   ██ ██   ██       ███    ██  ██████  ██     ██ 
    ██      ██   ██      ██ ██   ██ ██  ██        ████   ██ ██  ████ ██     ██ 
    ███████ ██████   █████  ███████ █████   █████ ██ ██  ██ ██ ██ ██ ██  █  ██ 
         ██ ██           ██      ██ ██  ██        ██  ██ ██ ████  ██ ██ ███ ██ 
    ███████ ██      ██████       ██ ██   ██       ██   ████  ██████   ███ ███  
                                                                               
                                                                      
'''

# Define ANSI color codes
class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    
    @staticmethod
    def colored(text, color):
        return f"{color}{text}{Colors.RESET}"
    
class TerminalUI:
    """Simple terminal UI for displaying transcripts and messages"""
    
    def __init__(self):
        """Initialize the terminal UI"""
        self.width = min(shutil.get_terminal_size().columns, 100)
        self.show_timestamps = True
        self.bilingual_mode = False
        self.is_paused = False
        self.use_side_by_side = True  # Default to side-by-side display
        
        
        # Current interim transcript being displayed
        self.current_interim = {}
        self.current_translation_interim = {}
        
        # Status information
        self.current_latency = 0
        self.avg_latency = 0
        
        # Thread for UI updates
        self.update_thread = None
        self.running = False
        
        # Keep track of last printed transcript
        self.last_interim_text = {}  # timestamp -> text
        
        # Clear the terminal
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def start(self):
        """Start the UI"""
        self.running = True
        print("\n" + "=" * self.width)
        print("SP34K-N0W TRANSCRIBER".center(self.width))
        print("=" * self.width)
        
        # Start status update thread
        self.update_thread = Thread(target=self._status_updater)
        self.update_thread.daemon = True
        self.update_thread.start()
    
    def stop(self):
        """Stop the UI"""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=0.5)
    
    def _status_updater(self):
        """Thread that updates the status information periodically"""
        while self.running:
            # Update status line with latency every 5 seconds
            status = []
            
            # Add pause/recording status
            if self.is_paused:
                status.append("⏸️ PAUSED")
            else:
                status.append("🎙️ RECORDING")
                
            # Add latency
            status.append(f"Latency: {self.current_latency:.3f}s (Avg: {self.avg_latency:.3f}s)")
            
            # Print status with proper cursor position
            status_line = " | ".join(status)
            if len(status_line) > self.width:
                status_line = status_line[:self.width-3] + "..."
            
            # Only print status every 5 seconds to avoid cluttering
            time.sleep(5)
    
    def display_welcome(self, language_code, mic_device=None, translate=False):
        """Display welcome message with ASCII banner"""
        # Save UI settings
        self.bilingual_mode = translate
        
        # Clear terminal first
        os.system('cls' if os.name == 'nt' else 'clear')
        
        language_names = {
            "it": "Italian",
            "en": "English",
            "fr": "French",
            "es": "Spanish",
            "de": "German",
            "zh": "Chinese",
            "ja": "Japanese",
            "ru": "Russian"
        }
        language = language_names.get(language_code, language_code)
        
        # Print ASCII banner
        print(BANNER)
        print("=" * 80)
        print(f"Active language: {language}")
        
        # Display microphone device if available
        if mic_device:
            print(f"Microphone: {mic_device}")
        else:
            print("Microphone: Default")
        
        # Display translation status if specified
        if translate:
            print("Translation: Enabled (to English)")
        
        print("=" * 80)
        print()
        
    def set_display_mode(self, use_side_by_side=True):
        """Set whether to use side-by-side or inline display mode"""
        self.use_side_by_side = use_side_by_side

    def display_transcript(self, timestamp, text, is_final=False, translation=None):
        """Display a transcript entry with the selected display method"""
        if self.use_side_by_side:
            # If translation is enabled, use the bilingual alternative
            if self.bilingual_mode:
                self.bilingual_display_transcript(timestamp, text, is_final, translation)
            else:
                self.side_by_side_display_transcript(timestamp, text, is_final, translation)
        else:
            self.inline_display_transcript(timestamp, text, is_final, translation)

    def inline_display_transcript(self, timestamp, text, is_final=False, translation=None):
        """Display a transcript entry with optional translation"""
        prefix = "📝 " if is_final else "🔄 "
        timestamp_str = f"[{timestamp}] " if self.show_timestamps else ""
        
        # Handle updating interim results
        if not is_final:
            if timestamp in self.last_interim_text:
                # Only print if different from the last version
                if self.last_interim_text[timestamp] != text:
                    print(f"\r{' ' * 100}", end='\r')  # Clear line
                    print(f"{prefix}{timestamp_str}{text}", end='\r')
                    self.last_interim_text[timestamp] = text
            else:
                print(f"{prefix}{timestamp_str}{text}", end='\r')
                self.last_interim_text[timestamp] = text
        else:
            # For final results, print on a new line
            print(f"\r{' ' * 100}", end='\r')  # Clear line
            print(f"{prefix}{timestamp_str}{text}")
            
            # If translation is available, print it too
            if translation:
                print(f"🌐 {timestamp_str}{translation}")
                
            # Remove from interim tracking
            self.last_interim_text.pop(timestamp, None)
            
    def side_by_side_display_transcript(self, timestamp, text, is_final=False, translation=None):
        """Display a transcript entry with optional translation in a two-column layout"""
        timestamp_str = f"[{timestamp}] " if self.show_timestamps else ""
        
        # Get terminal width and calculate column widths
        term_width = shutil.get_terminal_size().columns
        left_col_width = term_width // 2 - 2
        right_col_width = term_width - left_col_width - 3  # 3 for separator
        
        # Handle results based on type
        if not is_final:
            # Only print interim on the left if different from last version
            if timestamp not in self.last_interim_text or self.last_interim_text[timestamp] != text:
                # Format for left column (interim)
                interim_text = f"🔄 {timestamp_str}{text}"
                if len(interim_text) > left_col_width:
                    interim_text = interim_text[:left_col_width-3] + "..."
                else:
                    interim_text = interim_text.ljust(left_col_width)
                    
                # Print without final column content
                print(f"\r{interim_text} │ ", end='')
                self.last_interim_text[timestamp] = text
        else:
            # For final results, print on the right column
            final_text = f"📝 {timestamp_str}{text}"
            if len(final_text) > right_col_width:
                final_text = final_text[:right_col_width-3] + "..."
                
            # Print a full line with both columns
            # Left side empty (or with last interim if available)
            left_side = " " * left_col_width
            for last_ts, last_text in self.last_interim_text.items():
                # Use the most recent interim as the left content
                interim_prefix = "🔄 "
                last_ts_str = f"[{last_ts}] " if self.show_timestamps else ""
                left_content = f"{interim_prefix}{last_ts_str}{last_text}"
                if len(left_content) > left_col_width:
                    left_content = left_content[:left_col_width-3] + "..."
                left_side = left_content.ljust(left_col_width)
                break
                
            # Print the full line with both columns
            print(f"\r{left_side} │ {final_text}")
            
            # If translation is available, print it below aligned with right column
            if translation:
                trans_text = f"🌐 {timestamp_str}{translation}"
                if len(trans_text) > right_col_width:
                    trans_text = trans_text[:right_col_width-3] + "..."
                print(f"{' ' * (left_col_width + 3)}{trans_text}")
                
            # Remove from interim tracking
            self.last_interim_text.pop(timestamp, None)
            
    def bilingual_display_transcript(self, timestamp, text, is_final=False, translation=None):
        """
        Left column: original via inline_display_transcript()
        Right column: translation, printed with indentation
        """
        # 1. Print original using your inline logic (no translation)
        self.inline_display_transcript(timestamp, text, is_final, None)

        # 2. If it's a final result and we have a translation, print it on the right
        if is_final and translation:
            cols = shutil.get_terminal_size().columns
            left_w = cols // 2
            indent = left_w + 3  # gap + separator

            ts = f"[{timestamp}] " if self.show_timestamps else ""
            trans_line = f"🌐 {ts}{translation}"

            # Truncate if too long
            max_right = cols - indent - 1
            if len(trans_line) > max_right:
                trans_line = trans_line[:max_right-3] + "…"

            # Print with spaces
            print(" " * indent + trans_line)

    
    def display_message(self, message):
        """Display a status message"""
        # Only print if not already logged via logger
        if not message.startswith('\n'):  # Skip messages that start with newline
            print(f"ℹ️  {message}")

    def display_error(self, message):
        """Display an error message"""
        # Use stderr for errors
        print(f"❌ ERROR: {message}", file=sys.stderr)
    
    def display_latency(self, current_latency, avg_latency):
        """Update latency information"""
        self.current_latency = current_latency
        self.avg_latency = avg_latency
        print(f"\r✅ Latency: {current_latency:.3f}s (Avg: {avg_latency:.3f}s)", end='\r')
    
    def set_paused(self, is_paused):
        """Update the paused state with colored output"""
        self.is_paused = is_paused
        self.display_status_banner()
        
        if is_paused:
            message = Colors.colored("⏸️  Press Ctrl+R to resume transcription", Colors.YELLOW)
            print(f"{message}\n")
        else:
            message = Colors.colored("▶️  Press Ctrl+S to pause transcription", Colors.GREEN)
            print(f"{message}\n")
        
    def set_show_timestamps(self, show):
        """Set whether to show timestamps"""
        self.show_timestamps = show
    
    def request_confirmation(self, message="Ready to start transcription. Press 'y' to begin or 'n' to cancel: "):
        """Ask for user confirmation before starting"""
        response = input(message)
        return response.lower() == 'y'
    
    def display_status_banner(self):
        """Display a status banner with current state"""
        width = min(shutil.get_terminal_size().columns, 100)
        
        if self.is_paused:
            status = Colors.colored(" PAUSED ", Colors.YELLOW + Colors.BOLD)
            banner = f"{'=' * ((width - 8) // 2)}{status}{'=' * ((width - 8) // 2)}"
            print(f"\n{banner}")
        else:
            status = Colors.colored(" RECORDING ", Colors.GREEN + Colors.BOLD)
            banner = f"{'=' * ((width - 11) // 2)}{status}{'=' * ((width - 11) // 2)}"
            print(f"\n{banner}")