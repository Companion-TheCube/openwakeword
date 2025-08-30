# OpenWakeWord

A custom wake word detection system based on the excellent [OpenWakeWord](https://github.com/dscripka/openWakeWord) project by David Scripka.

## Overview

This repository contains modified wake word detection scripts that provide both microphone-based and socket-based wake word detection capabilities. The implementation uses pre-trained ONNX models for efficient wake word recognition.

## Attribution

This project is based on and uses code from the [OpenWakeWord](https://github.com/dscripka/openWakeWord) project by **David Scripka** (@dscripka). We are grateful for David's excellent work in creating an open-source wake word detection system.

- **Original Project**: https://github.com/dscripka/openWakeWord
- **Original Author**: David Scripka
- **Original License**: Apache License 2.0
- **Based on**: `detect_from_microphone.py` example from OpenWakeWord

## Features

- **Socket-based Detection** (`openww.py`): Listens for audio data via Unix socket and provides wake word detection over a network interface
- **Microphone Detection** (`detect_from_microphone.py`): Direct microphone input for real-time wake word detection
- **Multiple Models**: Support for multiple wake word models including "hey cuba", "hey cube", "hey cue"
- **Configurable Thresholds**: Adjustable detection sensitivity
- **ONNX Runtime**: Efficient inference using ONNX models

## Installation

1. Run the installation script:
```bash
chmod +x install.sh
./install.sh
```

This will:
- Create a Python virtual environment
- Install OpenWakeWord and all dependencies
- Set up the environment for wake word detection

2. Activate the virtual environment:
```bash
source bin/activate
```

## Usage

### Socket-based Detection

The `openww.py` script creates a Unix socket server that listens for audio data and performs wake word detection:

```bash
python openww.py [options]
```

**Options:**
- `--chunk_size CHUNK_SIZE`: Audio samples to predict on at once (default: 1280)
- `--model_path MODEL_PATH`: Path to specific model file(s), comma-separated for multiple models
- `--inference_framework FRAMEWORK`: Use 'onnx' or 'tflite' (default: 'onnx')
- `--socket_path SOCKET_PATH`: Unix socket path (default: `/tmp/openww`)
- `--detection_threshold THRESHOLD`: Detection threshold 0.00-1.00 (default: 0.3)

**Example:**
```bash
python openww.py --model_path hey_cube.onnx --detection_threshold 0.5
```

### Microphone Detection

The `detect_from_microphone.py` script provides direct microphone input detection:

```bash
python detect_from_microphone.py [options]
```

**Note**: This script requires PyAudio for microphone access, which may need additional system dependencies.

## Available Models

The repository includes several pre-trained wake word models:
- `hey_cuba.onnx`
- `hey_cube.onnx` 
- `hey_cube2.onnx`
- `hey_cue.onnx`

You can use any of these models or provide your own ONNX-format wake word models.

## Architecture

The socket-based detection system (`openww.py`) is designed to work with external audio sources that provide audio data over a Unix socket. This allows for flexible integration with various audio processing pipelines.

## Dependencies

- Python 3.7+
- OpenWakeWord
- NumPy
- ONNX Runtime
- SciPy
- scikit-learn

## License

This project is licensed under the Apache License 2.0, the same license as the original OpenWakeWord project. See the [LICENSE](LICENSE) file for details.

## Contributing

When contributing to this project, please ensure that any modifications maintain compatibility with the original OpenWakeWord license and properly attribute the original work by David Scripka.

## Acknowledgments

- **David Scripka** (@dscripka) for creating the original OpenWakeWord project
- The OpenWakeWord community for their contributions to open-source wake word detection
- **A-McD Technology LLC** for the modifications and enhancements in this fork

## Support

For issues related to the core OpenWakeWord functionality, please refer to the [original OpenWakeWord repository](https://github.com/dscripka/openWakeWord).

For issues specific to the modifications in this repository, please open an issue in this repository.