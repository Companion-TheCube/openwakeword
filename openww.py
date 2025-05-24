# This file is based on the "detect_from_microphone.py" file from the OpenWakeWord project.
# The original file can be found at:
# https://github.com/dscripka/openWakeWord/blob/main/examples/detect_from_microphone.py 

# Used with permission from the author as part of the Apache 2.0 license.
# The original file is licensed under the Apache License, Version 2.0 (the "License");

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


# This script as modified:
#
# Copyright 2025 A-McD Technology LLC. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
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
    "--detection_threshold",
    help="Threshold for a positive detection. 0.00 to 1.00",
    type=int,
    default=0.3,
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

CHUNK = args.chunk_size
SOCK = os.path.abspath(args.socket_path)
THRESHOLD = args.detection_threshold

if os.path.exists(SOCK):
    os.unlink(SOCK)

print(f"Socket path: {SOCK}")
server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
server_socket.bind(SOCK)
server_socket.listen(1)

if args.model_path != "":
    if "," in args.model_path:
        args.model_path = args.model_path.split(",")
    else:
        args.model_path = [args.model_path]
    owwModel = Model(wakeword_model_paths=args.model_path)
else:
    owwModel = Model()

n_models = len(owwModel.models.keys())

if __name__ == "__main__":
    print("")
    print("#"*100)
    print("Listening for wakewords...")
    print(f"Using {n_models} models:")
    for mdl in owwModel.models.keys():
        print(f"  - {mdl}")
    print("#"*100)
    print("\n")

    client_socket, _ = server_socket.accept()
    while True:
        try:
            # client_socket.settimeout(1)
            audio = recv_all(client_socket, CHUNK * 2)
        except socket.timeout:
            print("Socket timeout")
            continue
        except socket.error as e:
            print(f"Socket error: {e}")
            break
        if not audio:
            print("No audio received")
            continue
        if len(audio) != CHUNK * 2:
            print(f"Audio length (ERR): {len(audio)}")
            continue
        audio = np.frombuffer(audio, dtype=np.int16)
        prediction = owwModel.predict(audio)
        for mdl in owwModel.prediction_buffer.keys():
            scores = list(owwModel.prediction_buffer[mdl])
            if scores[-1] >= THRESHOLD:
                client_socket.sendall(b"DETECTED____")
            else:
                client_socket.sendall(b"NOT_DETECTED")
    client_socket.close()