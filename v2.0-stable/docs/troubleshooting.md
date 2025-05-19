# Troubleshooting Guide

This guide provides solutions for common issues that may arise when using SP34KN0W Live Transcriber.

## Installation Issues

### PyAudio Installation Failures

**Problem**: Unable to install PyAudio from requirements.txt

**Solutions**:

1. **Install PortAudio first**:
   - Windows: Use prebuilt wheels or `pip install pipwin && pipwin install pyaudio`
   - macOS: `brew install portaudio && pip install pyaudio`
   - Linux: `sudo apt-get install python3-pyaudio` or `sudo apt-get install portaudio19-dev`

2. **Use specific wheel file** (Windows):
   - Download appropriate wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
   - Install with `pip install [wheel-filename]`

3. **Check Python version compatibility**:
   - Ensure you're using a supported Python version (3.6-3.9 for older PyAudio versions)

### Missing Dependencies

**Problem**: Error about missing module or package

**Solutions**:
1. Ensure virtual environment is activated (if using one)
2. Reinstall all dependencies: `pip install -r requirements.txt`
3. Update pip: `pip install --upgrade pip`

## Configuration Issues

### API Key Problems

**Problem**: "DEEPGRAM_API_KEY environment variable not set" error

**Solutions**:
1. Create a `.env` file in the project root with `DEEPGRAM_API_KEY=your_key_here`
2. Set the environment variable manually:
   ```powershell
   $env:DEEPGRAM_API_KEY="your_key_here"
   ```
3. Check that the API key is valid in the Deepgram console

### Language Support Issues

**Problem**: Specified language not recognized or working poorly

**Solutions**:
1. Use `python main.py --list-languages` to see supported languages
2. Try using the language code (e.g., "fr" instead of "French")
3. Check if the language requires a specific model in `config.py`

## Audio and Microphone Issues

### Microphone Not Detected

**Problem**: Default or specified microphone not found

**Solutions**:
1. List available microphones: `python main.py --list-mics`
2. Try specifying microphone by index: `python main.py --mic 1`
3. Check system permissions for microphone access
4. Verify the microphone is plugged in and not in use by another application

### Poor Audio Quality

**Problem**: Transcription accuracy is low or inconsistent

**Solutions**:
1. Check microphone levels and positioning
2. Reduce background noise
3. Use a higher quality microphone
4. Ensure proper microphone selection with `--list-mics` and `--mic`

### No Audio Input Detected

**Problem**: "Audio level is too low" warning appears

**Solutions**:
1. Adjust microphone input volume in system settings
2. Position microphone closer to the speaker
3. Check if microphone is muted
4. Try a different microphone

## Transcription Issues

### High Latency

**Problem**: Large delay between speaking and seeing transcription

**Solutions**:
1. Check your internet connection speed and stability
2. Ensure no other applications are using significant bandwidth
3. Try a different Deepgram model or language setting
4. Consider reducing buffer size in the code (for developers)

### Inaccurate Transcriptions

**Problem**: Poor transcription quality or many errors

**Solutions**:
1. Speak clearly and at a moderate pace
2. Check microphone quality and positioning
3. Verify you're using the correct language setting
4. Try a different Deepgram model
5. For technical terms, consider adding them to the glossary

### Connection Errors

**Problem**: Unable to connect to Deepgram API

**Solutions**:
1. Check internet connection
2. Verify API key is valid
3. Check Deepgram service status
4. Check for firewall or proxy issues
5. Run with `--debug` flag for more detailed error information

## UI and Display Issues

### Terminal Formatting Problems

**Problem**: UI looks distorted or has strange characters

**Solutions**:
1. Use a terminal with Unicode support
2. Check terminal font supports emoji characters
3. Try adjusting terminal window size
4. Verify terminal supports ANSI color codes

### Text Wrapping Issues

**Problem**: Long transcripts don't display properly

**Solutions**:
1. Increase terminal window width
2. The UI automatically adjusts to terminal width (up to 80 chars)

## Session Management Issues

### Session Files Not Saving

**Problem**: Transcription session files not appearing in sessions folder

**Solutions**:
1. Check write permissions for the sessions directory
2. Ensure program is exiting gracefully (use Ctrl+C, not closing terminal)
3. Verify sessions directory exists (should be created automatically)

### Cannot Find Previous Sessions

**Problem**: Unable to locate previous transcription sessions

**Solutions**:
1. Use `python main.py --list-sessions` to see available sessions
2. Check the sessions directory in the project root
3. Verify you're running from the correct directory

## Performance Issues

### High CPU Usage

**Problem**: Application using excessive CPU resources

**Solutions**:
1. Close other CPU-intensive applications
2. Check for background processes that might be interfering
3. Try a different microphone or audio settings
4. Consider using a more powerful device

### Memory Leaks

**Problem**: Application memory usage grows over time

**Solutions**:
1. Restart the application for long sessions
2. Limit session length to a reasonable duration
3. Update to the latest version which may include fixes

## Advanced Troubleshooting

### Debug Mode

For detailed logging and troubleshooting:

```powershell
python main.py --debug
```

For even more verbose output:

```powershell
python main.py --debug --verbose
```

### Checking Version Compatibility

Ensure your Python version and package versions are compatible:

```powershell
python --version
pip list
```

### Generating Error Logs

To save detailed logs for analysis:

```powershell
python main.py --debug 2> error_log.txt
```

## Getting Additional Help

If you continue to experience issues:

1. Check the GitHub Issues page for similar problems and solutions
2. Create a new issue with:
   - Detailed description of the problem
   - Steps to reproduce
   - System information
   - Any error messages (preferably from debug mode)
   - What you've tried already

3. For Deepgram API specific issues, consult:
   - [Deepgram Documentation](https://developers.deepgram.com/docs/)
   - [Deepgram Support](https://deepgram.com/support/)
