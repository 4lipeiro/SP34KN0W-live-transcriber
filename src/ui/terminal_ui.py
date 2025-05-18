import os
import sys
import re
import time
import curses
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

class TerminalUI:
    """Enhanced terminal UI for displaying transcripts and messages with advanced layout"""
    
    def __init__(self):
        """Initialize the terminal UI"""
        self.width = min(os.get_terminal_size().columns, 100)
        self.height = os.get_terminal_size().lines
        self.transcript_count = 0
        self.show_timestamps = True
        self.bilingual_mode = False
        self.is_paused = False
        
        # Current interim transcript being displayed
        self.current_interim = {}  # timestamp -> text
        self.current_translation_interim = {}  # timestamp -> text
        
        # Lock for thread-safe updates
        self.display_lock = Lock()
        
        # Curses setup happens in start()
        self.stdscr = None
        self.transcript_window = None
        self.header_window = None
        self.footer_window = None
        
        # Layout dimensions
        self.header_height = 4
        self.footer_height = 3
        
        # Current latency info
        self.current_latency = 0
        self.avg_latency = 0
        
        # Clear the terminal
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def start(self):
        """Start the curses UI"""
        # Initialize curses
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        curses.use_default_colors()
        self.stdscr.keypad(True)
        
        # Initialize color pairs
        curses.init_pair(1, curses.COLOR_GREEN, -1)   # Good status
        curses.init_pair(2, curses.COLOR_YELLOW, -1)  # Warning status
        curses.init_pair(3, curses.COLOR_RED, -1)     # Error status
        curses.init_pair(4, curses.COLOR_CYAN, -1)    # Info
        curses.init_pair(5, curses.COLOR_WHITE, -1)   # Normal text
        curses.init_pair(6, curses.COLOR_MAGENTA, -1) # Translation
        
        # Create windows
        self.header_window = curses.newwin(self.header_height, self.width, 0, 0)
        self.transcript_window = curses.newwin(
            self.height - self.header_height - self.footer_height, 
            self.width, 
            self.header_height, 
            0
        )
        self.footer_window = curses.newwin(
            self.footer_height, 
            self.width, 
            self.height - self.footer_height, 
            0
        )
        
        # Enable scrolling for transcript window
        self.transcript_window.scrollok(True)
        
        # Initial draw
        self._draw_header()
        self._draw_footer()
        self.refresh()
    
    def stop(self):
        """Properly shut down curses"""
        if self.stdscr:
            curses.nocbreak()
            self.stdscr.keypad(False)
            curses.echo()
            curses.endwin()
    
    def refresh(self):
        """Refresh all windows"""
        with self.display_lock:
            self.header_window.refresh()
            self.transcript_window.refresh()
            self.footer_window.refresh()
    
    def _draw_header(self):
        """Draw the header with toolbar"""
        self.header_window.clear()
        
        # Date on left, title in center, latency on right
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        title = "SP34K-N0W TRANSCRIBER"
        
        latency_str = f"Latency: {self.current_latency:.3f}s (Avg: {self.avg_latency:.3f}s)"
        latency_color = 1 if self.current_latency < 0.5 else (2 if self.current_latency < 1.0 else 3)
        
        # First row
        self.header_window.addstr(0, 0, date_str, curses.A_NORMAL)
        self.header_window.addstr(0, (self.width - len(title)) // 2, title, curses.A_BOLD)
        self.header_window.addstr(0, self.width - len(latency_str) - 1, latency_str, curses.color_pair(latency_color))
        
        # Status line
        status = "⏸️ PAUSED - Press Ctrl+R to resume" if self.is_paused else "🎙️ RECORDING"
        self.header_window.addstr(1, (self.width - len(status)) // 2, status, 
                               curses.A_BOLD | (curses.color_pair(2) if self.is_paused else curses.color_pair(1)))
        
        # Separator line
        self.header_window.hline(2, 0, curses.ACS_HLINE, self.width)
        
        # Column headers for bilingual mode
        if self.bilingual_mode:
            col_width = self.width // 2 - 2
            self.header_window.addstr(3, col_width // 2 - 7, "ORIGINAL TEXT", curses.A_BOLD)
            self.header_window.addstr(3, col_width + col_width // 2 - 11, "TRANSLATION (ENGLISH)", curses.A_BOLD)
            self.header_window.vline(3, self.width // 2, curses.ACS_VLINE, 1)
        
        self.header_window.refresh()
    
    def _draw_footer(self):
        """Draw the footer with status information"""
        self.footer_window.clear()
        self.footer_window.hline(0, 0, curses.ACS_HLINE, self.width)
        
        # Controls info
        controls = "Ctrl+S: Pause | Ctrl+R: Resume | Ctrl+C: Exit"
        self.footer_window.addstr(1, (self.width - len(controls)) // 2, controls, curses.A_NORMAL)
        
        self.footer_window.refresh()
    
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
    
    def display_transcript(self, timestamp, text, is_final=False, translation=None):
        """Display a transcript entry with optional translation"""
        if not self.stdscr:
            return  # Curses not initialized yet
        
        with self.display_lock:
            # In bilingual mode, split the screen
            max_width = self.width
            if self.bilingual_mode:
                max_width = self.width // 2 - 2
            
            # Format the message
            prefix = "📝 " if is_final else "🔄 "
            timestamp_str = f"[{timestamp}] " if self.show_timestamps else ""
            
            # If this is an interim update of an existing timestamp
            if not is_final:
                # If we already have an interim result with this timestamp, clear it
                if timestamp in self.current_interim:
                    self._replace_interim(timestamp, text, translation)
                else:
                    # New interim result
                    self._add_new_transcript(timestamp, text, is_final, translation)
                    self.current_interim[timestamp] = text
                    if translation:
                        self.current_translation_interim[timestamp] = translation
            else:
                # Final result - remove from interim tracking if it exists
                if timestamp in self.current_interim:
                    self._replace_interim(timestamp, text, translation)
                    self.current_interim.pop(timestamp, None)
                    self.current_translation_interim.pop(timestamp, None)
                else:
                    # New final result
                    self._add_new_transcript(timestamp, text, is_final, translation)
            
            self.transcript_window.refresh()
            
    def _add_new_transcript(self, timestamp, text, is_final, translation=None):
        """Add a completely new transcript line"""
        max_width = self.width
        if self.bilingual_mode:
            max_width = self.width // 2 - 2
        
        prefix = "📝 " if is_final else "🔄 "
        timestamp_str = f"[{timestamp}] " if self.show_timestamps else ""
        
        # Prepare formatting
        attr = curses.A_BOLD if is_final else curses.A_NORMAL
        
        # If in bilingual mode, place text on left side
        if self.bilingual_mode:
            # Add the transcript to the left column
            self.transcript_window.addstr(prefix + timestamp_str, attr)
            self.transcript_window.addstr(text[:max_width-len(prefix)-len(timestamp_str)] + "\n", attr)
            
            # Add the translation to the right column if available
            if translation:
                # Move cursor to right column, same line
                y, _ = self.transcript_window.getyx()
                self.transcript_window.move(y-1, self.width // 2 + 1)
                self.transcript_window.addstr(prefix, attr)
                self.transcript_window.addstr(translation[:max_width-len(prefix)] + "\n", 
                                           attr | curses.color_pair(6))
            else:
                # No translation, just add a newline to right column
                self.transcript_window.addstr("\n", attr)
        else:
            # Single column mode
            self.transcript_window.addstr(prefix + timestamp_str, attr)
            self.transcript_window.addstr(text[:max_width-len(prefix)-len(timestamp_str)] + "\n", attr)
            
            # Add translation if available
            if translation:
                self.transcript_window.addstr("🌐 " + timestamp_str, attr)
                self.transcript_window.addstr(translation[:max_width-3-len(timestamp_str)] + "\n", 
                                           attr | curses.color_pair(6))
    
    def _replace_interim(self, timestamp, text, translation=None):
        """Replace an existing interim result with updated text"""
        # This is much more complex in curses - for simplicity, we'll just add a new line
        # In a full implementation, we would need to track line positions and use insch/delch
        # For now, we'll simplify by just adding a new line
        self._add_new_transcript(timestamp, text, False, translation)
    
    def display_message(self, message):
        """Display a status message in the footer area"""
        if not self.stdscr:
            # Fall back to standard output if curses is not initialized
            print(f"ℹ️  {message}")
            return
        
        with self.display_lock:
            # Clear the last row of the footer
            self.footer_window.move(2, 0)
            self.footer_window.clrtoeol()
            
            # Display the message
            if len(message) > self.width - 4:
                message = message[:self.width - 7] + "..."
                
            self.footer_window.addstr(2, 2, message, curses.color_pair(4))
            self.footer_window.refresh()
    
    def display_error(self, message):
        """Display an error message in the footer area"""
        if not self.stdscr:
            # Fall back to standard output if curses is not initialized
            print(f"❌ ERROR: {message}", file=sys.stderr)
            return
        
        with self.display_lock:
            # Clear the last row of the footer
            self.footer_window.move(2, 0)
            self.footer_window.clrtoeol()
            
            # Display the error message
            if len(message) > self.width - 10:
                message = message[:self.width - 13] + "..."
                
            self.footer_window.addstr(2, 2, "ERROR: " + message, curses.color_pair(3) | curses.A_BOLD)
            self.footer_window.refresh()
    
    def display_latency(self, current_latency, avg_latency):
        """Update and display latency information"""
        self.current_latency = current_latency
        self.avg_latency = avg_latency
        self._draw_header()
    
    def set_paused(self, is_paused):
        """Update the paused state and refresh header"""
        self.is_paused = is_paused
        self._draw_header()
    
    def set_show_timestamps(self, show):
        """Set whether to show timestamps"""
        self.show_timestamps = show
    
    def clear_transcript(self):
        """Clear the transcript window"""
        if self.transcript_window:
            self.transcript_window.clear()
            self.transcript_window.refresh()
    
    def request_confirmation(self, message="Ready to start transcription. Press 'y' to begin or 'n' to cancel: "):
        """Ask for user confirmation before starting"""
        # If curses is active, stop it temporarily
        curses_active = self.stdscr is not None
        if curses_active:
            self.stop()
        
        # Ask for confirmation
        response = input(message)
        
        # Restart curses if it was active
        if curses_active:
            self.start()
            
        return response.lower() == 'y'