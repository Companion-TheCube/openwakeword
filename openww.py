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
import sounddevice as sd


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
    default="/tmp/openww",
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

def recv_all(sock, num_bytes):
    buf = bytearray()
    while len(buf) < num_bytes:
        chunk = sock.recv(num_bytes - len(buf))
        if not chunk:
            raise ConnectionError("Socket closed")
        buf.extend(chunk)
    return bytes(buf)

# check to see if we are on windows
SOCKET_TYPE = socket.AF_UNIX
# Get microphone stream
# FORMAT = pyaudio.paInt16
CHANNELS = 1
CHUNK = args.chunk_size
SOCK = os.path.abspath(args.socket_path)
# audio = pyaudio.PyAudio()
#mic_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

if os.path.exists(SOCK):
    os.unlink(SOCK)

# print the socket path
print(f"Socket path: {SOCK}")
server_socket = socket.socket(SOCKET_TYPE, socket.SOCK_STREAM)
server_socket.bind("/tmp/openww")
server_socket.listen(1)

# Load model(s). If the path is a directory, load all models in the directory.
if args.model_path != "":
    # if path contains a comma, split it into a list
    if "," in args.model_path:
        args.model_path = args.model_path.split(",")
    # else just make it a list
    else:
        args.model_path = [args.model_path]
    # Load all models
    owwModel = Model(wakeword_models=args.model_path, inference_framework=args.inference_framework)
else:
    owwModel = Model(inference_framework=args.inference_framework)

n_models = len(owwModel.models.keys())

# Run capture loop continuously, checking for wakewords
if __name__ == "__main__":
    # Generate output string header
    print("\n\n")
    print("#"*100)
    print("Listening for wakewords...")
    print(f"Using {n_models} models:")
    for mdl in owwModel.models.keys():
        print(f"  - {mdl}")
    print("#"*100)
    print("\n"*2)

    # stream = sd.RawOutputStream(
    #     samplerate=16000,
    #     channels=CHANNELS,
    #     dtype='int16',
    #     blocksize=CHUNK
    # )
    # stream.start()

    client_socket, _ = server_socket.accept()
    while True:
        # Get audio
        #audio = np.frombuffer(mic_stream.read(CHUNK), dtype=np.int16)

        # read the audio from the socket as base64 encoded string.
        try:
            # audio = client_socket.recv(CHUNK * 2, socket.MSG_WAITALL)
            # print("Waiting for audio...")
            # Set a timeout for the socket
            client_socket.settimeout(1)
            # Receive the audio data
            # recv_all will block until it receives the specified number of bytes
            # or the socket is closed.
            audio = recv_all(client_socket, CHUNK * 2)
            # client_socket.sendall(b"ACK_________")
        except socket.timeout:
            # if the socket times out, continue
            print("Socket timeout")
            continue
        except socket.error as e:
            # if the socket is closed, break
            print(f"Socket error: {e}")
            break
        if not audio:
            print("No audio received")
            continue

        # bytes_per_frame = sd.query_hostapis()[sd.default.hostapi]['default_output_device']  # not strictly needed
        # frame_bytes = CHUNK * CHANNELS * 2  # 2 bytes per int16 sample

        # stream.write(audio)

        # audio is base64 encoded, decode it
        # audio = base64.b64decode(audio)
        # if the length of the audio is not equal to the chunk size, skip it.
        if len(audio) != CHUNK * 2:
            print(f"Audio length (ERR): {len(audio)}")
            continue
        # print(f"Audio length: {len(audio)}")

        # convert byte array to numpy array
        audio = np.frombuffer(audio, dtype=np.int16)
        
        # print(f"Audio shape: {audio.shape}")
        # Feed to openWakeWord model
        prediction = owwModel.predict(audio)
        for mdl in owwModel.prediction_buffer.keys():
            # print(f"Model: {mdl}")
            # Add scores in formatted table
            scores = list(owwModel.prediction_buffer[mdl])
            # print(f"Scores: {scores}")
            # print(f"Scores: {scores[-1]}")
            if scores[-1] >= 0.2:
                client_socket.sendall(b"DETECTED____")
                print(f"Detected wakeword '{mdl}' with score {scores[-1]}")
            else:
                client_socket.sendall(b"NOT_DETECTED")
    # stream.close()
    client_socket.close()