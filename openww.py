# Copyright 2022 David Scripka. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Imports
import socket
import os
import numpy as np
from openwakeword.model import Model
import argparse
import base64

# Parse input arguments
parser=argparse.ArgumentParser()
parser.add_argument(
    "--chunk_size",
    help="How much audio (in number of samples) to predict on at once",
    type=int,
    default=1280,
    required=False
)
parser.add_argument(
    "--model_path",
    help="The path of a specific model to load",
    type=str,
    default="",
    required=False
)
parser.add_argument(
    "--inference_framework",
    help="The inference framework to use (either 'onnx' or 'tflite'",
    type=str,
    default='onnx',
    required=False
)
parser.add_argument(
    "--socket_path",
    help="The path to the socket that provides the audio.",
    type=str,
    default="\0openww.sock",
    required=False
)
parser.add_argument(
    "--use_ip_socket",
    help="Use an IP socket instead of a Unix socket.",
    action="store_true",
    required=False
)
parser.add_argument(
    "--ip_port",
    help="The port to use if using an IP socket.",
    type=int,
    default=5000,
    required=False
)

args=parser.parse_args()

# check to see if we are on windows
SOCKET_TYPE = socket.AF_UNIX
if os.name == 'nt' or args.use_ip_socket:
    SOCKET_TYPE = socket.AF_INET
PORT = args.ip_port

# Get microphone stream
# FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = args.chunk_size
SOCK = args.socket_path
#audio = pyaudio.PyAudio()
#mic_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

if os.path.exists(SOCK):
    os.remove(SOCK)

# print the socket path
print(f"Socket path: {SOCK}")
server_socket = socket.socket(SOCKET_TYPE, socket.SOCK_STREAM)
if(SOCKET_TYPE == socket.AF_INET):
    server_socket.bind(('', PORT))
else:
    server_socket.bind(SOCK)
server_socket.listen(1)

# Load pre-trained openwakeword models
if args.model_path != "":
    owwModel = Model(wakeword_models=[args.model_path], inference_framework=args.inference_framework)
else:
    owwModel = Model(inference_framework=args.inference_framework)

n_models = len(owwModel.models.keys())

# Run capture loop continuously, checking for wakewords
if __name__ == "__main__":
    # Generate output string header
    print("\n\n")
    print("#"*100)
    print("Listening for wakewords...")
    print("#"*100)
    print("\n"*(n_models*3))

    while True:
        # Get audio
        #audio = np.frombuffer(mic_stream.read(CHUNK), dtype=np.int16)
        client_socket, _ = server_socket.accept()
        # read the audio from the socket as base64 encoded string. 
        audio = client_socket.recv((CHUNK + 2) // 3 * 4).decode("utf-8")
        if not audio:
            continue
        # audio is base64 encoded, decode it
        audio = base64.b64decode(audio)

        # convert byte array to numpy array
        audio = np.frombuffer(audio, dtype=np.int16)
        
        # Feed to openWakeWord model
        prediction = owwModel.predict(audio)
        for mdl in owwModel.prediction_buffer.keys():
            # Add scores in formatted table
            scores = list(owwModel.prediction_buffer[mdl])
            print(f"Model: {mdl}")
            if scores[-1] >= 0.5:
                print(f"Scores: {scores}")
            if "thecube" in mdl.lower():
                if scores[-1] >= 0.5:
                    client_socket.sendall(b"DETECTED")
                else:
                    client_socket.sendall(b"NOT")
