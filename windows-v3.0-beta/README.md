# SP34KN0W Live Transcriber - Windows v3.0-Beta

## Project Overview

This tool captures live Italian speech, generates a Deepgram transcript, and—when requested—locally translates the final transcript into English in real time on your NVIDIA GPU.

> ⚠️ **Warning:** This version may not work as expected in all environments, but the English translation feature could be quite useful when working with non-English speech. All translation is done locally on your GPU for better privacy.

It supports:
- **Streaming interim and final transcripts** in the terminal
- **Toggling translation** via a `--translate` flag
- **Two display modes**:
  - Inline or original side-by-side
  - Bilingual mode: original inline + indented English on the right
- **Dual-file output** on session end:
  - Combined bilingual markdown
  - English-only markdown

## Prerequisites

- Windows 10 or later
- Python 3.8+
- NVIDIA GPU (RTX 30xx-series, driver supporting CUDA 12.1)
- A Deepgram API key

## Installation

1. **Clone the repo**  
   ```powershell
   git clone https://github.com/4lipeiro/SP34KN0W-live-transcriber
   cd SP34KN0W-live-transcriber
   ```

2. **Create & activate your environment**

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**

    run
    ```python
    python.exe -m pip install --upgrade pip
    ```
    and then
    ```python
    pip install -r .\requirements.txt
    ```
   > Note: The initial setup may take several minutes as it downloads the translation models (~290MB).

## Configuration

Edit `config.py` to set:

* `DEEPGRAM_API_KEY`
* Default language (`italian`)
* `sessions_dir` (where transcripts are saved)

## Usage

```powershell
# Original-only mode
python main.py --language italian

# Bilingual (Italian + English) mode
python main.py --language italian --translate
```

Press **Ctrl+C** to end the session. Two files will appear in `sessions/`:

* `YYYY-MM-DD_HH-MM-SS.md` (combined transcript + translations)
* `YYYY-MM-DD_HH-MM-SS_en.md` (English-only translation)

## Implementation Details

### 1. CLI Flag

* `main.py` & `config.py` now parse `--translate`
* Passed through to `DeepgramTranscriber.translate` and `TerminalUI.bilingual_mode`

### 2. Translator Initialization

The translator is initialized using the Helsinki-NLP Opus model for Italian to English translation. The system automatically detects if a CUDA-capable GPU is available and uses it for faster translations.

### 3. Translating Final Segments

When a final transcript segment is received, it's automatically passed to the local translator (instead of using Deepgram's cloud translation service), providing more privacy and potentially faster results.

### 4. New Bilingual Display Mode

The terminal UI now includes a new bilingual display mode that shows:
- Original text inline with normal formatting
- Translated English text indented on the right with a globe icon (🌐)

### 5. Dual-File Output

When a transcription session ends:
1. A standard markdown file with both original and translated content is saved
2. An additional English-only file is created with the `_en` suffix

## File Structure

```
├── config.py
├── main.py
├── transcriber.py
├── utils.py
├── src/
│   ├── ui/
│   │   └── terminal_ui.py
│   ├── transcriber.py
│   ├── translator.py
│   └── utils.py
├── sessions/
│   └── YYYY-MM-DD_HH-MM-SS[_en].md
└── requirements.txt
```

## Troubleshooting

* **CUDA errors**: Ensure GPU drivers match your CUDA toolkit.
* **Slow startup**: First run downloads ~290 MB model; afterward it's cached.
* **Windows Defender latency**: Consider excluding your model cache folder.

---

With these updates, SP34KN0W now provides fast, private, offline Italian→English translation alongside the live Deepgram transcript—and saves both versions for easy reference.
