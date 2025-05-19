class Config:
    # Deepgram configuration
    DEEPGRAM_URL = "wss://api.deepgram.com/v1/listen"
    
    # Language-specific model mapping
    LANGUAGE_MODELS = {
        "it": "nova-2",   # Italian uses nova-2
        "en": "nova-3",
        "fr": "nova-2",
        "es": "nova-2",
        "de": "nova-3",
        "zh": "nova-2",
        "ja": "nova-2",
        "ru": "nova-2"
    }
    
    # Default model for any unlisted language
    DEFAULT_MODEL = "nova-2"
    
    # Transcription settings
    DEFAULT_LANGUAGE = "it"
    ENCODING = "linear16"  # Raw PCM audio
    SAMPLE_RATE = 16000   # 16 kHz
    CHANNELS = 1          # Mono audio
    
    # UI Settings
    TERMINAL_WIDTH = 80
    
    # Supported languages with ISO codes
    SUPPORTED_LANGUAGES = {
        "it": "Italian",
        "en": "English",
        "fr": "French",
        "es": "Spanish",
        "de": "German",
        "zh": "Chinese",
        "ja": "Japanese",
        "ru": "Russian"
    }
    
    # Technical terms glossary file
    TECH_GLOSSARY_PATH = "data/tech_glossary.json"