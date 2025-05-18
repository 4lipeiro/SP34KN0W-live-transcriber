import curses
import os
from datetime import datetime
from threading import Lock

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

    def __init__(self, debug_mode=False):
        self.debug_mode = debug_mode
        self.width = min(os.get_terminal_size().columns, 100)
        self.height = os.get_terminal_size().lines
        self.transcript = []
        self.debug_lines = []
        self.info_message = ""
        self.paused = False
        self.show_timestamps = True
        self.lock = Lock()
        self._main_thread = None
        self._running = False
        self._transcriber = None

    def start(self, transcriber=None):
        self._transcriber = transcriber
        self._running = True
        curses.wrapper(self._main_loop)

    def stop(self):
        self._running = False

    def refresh(self):
        # Will be handled by curses wrapper
        pass

    def _draw_header(self, stdscr):
        now = datetime.now().strftime("%Y-%m-%d")
        latency = "N/A"
        title = "SP34KN0W Live Transcriber"
        width = self.width
        stdscr.attron(curses.A_REVERSE)
        try:
            stdscr.addstr(0, 0, f" {now} ".ljust(width // 3)[:width // 3])
            stdscr.addstr(0, width // 3, title.center(width // 3)[:width // 3])
            stdscr.addstr(0, 2 * width // 3, f" Latency: {latency} ".rjust(width // 3 - 1)[:width // 3 - 1])
        except curses.error:
            pass
        stdscr.attroff(curses.A_REVERSE)

    def _draw_footer(self, stdscr):
        width = self.width
        stdscr.attron(curses.A_REVERSE)
        msg = self.info_message if self.info_message else "Ctrl+S: Pause | Ctrl+R: Resume | Ctrl+C: Quit"
        # Truncate to fit the width and avoid writing outside the window
        safe_msg = msg.ljust(width)[:max(0, width-1)]
        try:
            stdscr.addstr(self.height - 1, 0, safe_msg)
        except curses.error:
            pass
        stdscr.attroff(curses.A_REVERSE)

    def display_welcome(self, language_code, mic_device=None, translate=False):
        print(BANNER)
        print(f"Language: {language_code.upper()} | Mic: {mic_device or 'Default'} | Translate: {translate}")

    def display_transcript(self, timestamp, text, is_final=False, translation=None):
        with self.lock:
            line = f"[{timestamp}] {text}" if self.show_timestamps else text
            self.transcript.append(line)
            if translation:
                self.transcript.append(f"  > {translation}")
            if len(self.transcript) > 1000:
                self.transcript = self.transcript[-1000:]
            if self.debug_mode:
                self.debug_lines.append(f"DEBUG: {line}")

    def display_message(self, message):
        with self.lock:
            self.info_message = message

    def display_error(self, message):
        with self.lock:
            self.info_message = f"ERROR: {message}"

    def display_latency(self, current_latency, avg_latency):
        # Not implemented in this stub
        pass

    def set_paused(self, is_paused):
        with self.lock:
            self.paused = is_paused

    def set_show_timestamps(self, show):
        self.show_timestamps = show

    def clear_transcript(self):
        with self.lock:
            self.transcript = []

    def request_confirmation(self, message="Ready to start transcription. Press 'y' to begin or 'n' to cancel: "):
        print(message)
        while True:
            c = input().strip().lower()
            if c == "y":
                return True
            elif c == "n":
                return False

    def _main_loop(self, stdscr):
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(100)
        while self._running:
            self.height, self.width = stdscr.getmaxyx()  # Always get latest size
            stdscr.erase()
            self._draw_header(stdscr)
            if self.debug_mode:
                self._draw_split_debug(stdscr)
            else:
                self._draw_transcript(stdscr)
            self._draw_footer(stdscr)
            stdscr.refresh()
            try:
                key = stdscr.getch()
                if key == 3:  # Ctrl+C
                    self._running = False
                    break
                elif key == 19:  # Ctrl+S
                    if self._transcriber and not self.paused:
                        self._transcriber.pause()
                elif key == 18:  # Ctrl+R
                    if self._transcriber and self.paused:
                        self._transcriber.resume()
            except Exception:
                pass

    def _draw_transcript(self, stdscr):
        with self.lock:
            lines = self.transcript[-(self.height - 2):]
        for idx, line in enumerate(lines):
            if idx + 1 >= self.height - 1:
                break
            try:
                stdscr.addstr(idx + 1, 0, line[:self.width])
            except curses.error:
                pass

    def _draw_split_debug(self, stdscr):
        split = (self.height - 2) // 2
        with self.lock:
            t_lines = self.transcript[-split:]
            d_lines = self.debug_lines[-split:]
        for idx, line in enumerate(t_lines):
            if idx + 1 >= split:
                break
            try:
                stdscr.addstr(idx + 1, 0, line[:self.width])
            except curses.error:
                pass
        for idx, line in enumerate(d_lines):
            if idx + split + 1 >= self.height - 1:
                break
            try:
                stdscr.addstr(idx + split + 1, 0, line[:self.width])
            except curses.error:
                pass