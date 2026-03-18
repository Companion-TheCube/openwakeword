# OpenWakeWord

This directory contains TheCube's first-party wake word detection app bundle. It is based on the upstream [openWakeWord](https://github.com/dscripka/openWakeWord) project and is packaged here as a managed app that `CubeCore` launches through the app runtime.

## What It Is In This Repo

This is not just a loose Python script folder anymore. In the current system it is:

* app ID: `com.thecube.openwakeword`
* manifest-driven app bundle: `openwakeword/manifest.json`
* runtime type: Python
* runtime distribution: managed `venv`
* launch entrypoint: `openww.py`

In a normal local/dev run, the bundle is copied under:

* `build/bin/apps/openwakeword`

`CubeCore` then:

1. discovers the manifest
2. prepares the Python runtime
3. generates `launch-policy.json`
4. starts the app through `systemd`
5. invokes the standalone `CubeAppLauncher`

In dev mode this typically ends up under a transient user unit such as:

* `thecube-app@com.thecube.openwakeword.service`

## Role In The Audio Pipeline

`openww.py` listens on a Unix socket and performs wake word inference on incoming PCM audio blocks.

The current integration is:

* `WakeWordClient` in Core connects to `/tmp/openww`
* Core streams 16-bit PCM audio blocks into that socket
* `openww.py` replies with short control messages such as `DETECTED____` and `NOT_DETECTED`

Current implementation detail:

* the socket path is still hardcoded to `/tmp/openww` in both `openwakeword/openww.py` and `src/audio/wakeWordClient.cpp`

That works, but it is not the preferred long-term design. The app platform now provides `THECUBE_RUNTIME_DIR`, and this app should eventually move to an app-private runtime socket instead of host `/tmp`.

## Files In This Directory

Important files:

* `manifest.json`: app manifest consumed by `AppsManager`
* `openww.py`: socket-based detector used by Core
* `detect_from_microphone.py`: standalone microphone test utility
* `hey_*.onnx`: bundled wake word models
* `install.sh`: ad hoc standalone setup helper, mainly useful for manual debugging

## Normal Launch Path

For normal TheCube runtime use, do not treat `install.sh` or direct `python openww.py` execution as the primary path.

The intended path is:

* `CubeCore` owns manifest parsing and runtime preparation
* `AppsManager` installs the Python package named in the manifest into a managed venv
* `CubeCore` generates a resolved launch policy
* `CubeAppLauncher` applies environment and Landlock
* `systemd` supervises the process

The practical source-of-truth for this flow is:

* `src/apps/the_cube_app_launch_and_sandboxing_plan.md`

## Manifest And Sandbox Notes

The current manifest declares a sandboxed Python app. Filesystem access is resolved from manifest permissions into the generated launch policy.

Important operational details:

* the script currently uses `/tmp/openww`, so the app still needs host tmp access
* the manifest currently grants `system://tmp`
* the manifest also grants `system://proc`

Current known edge:

* Python venv interpreters and ONNX runtime dependencies often resolve through host paths such as `/usr`, `/lib`, or `/lib64`
* under Landlock, those paths must be granted explicitly through the manifest if the app needs them

So if `openwakeword` launches correctly without Landlock but fails under Landlock, inspect the generated launch policy and the manifest's `system://...` permissions first.

## Standalone Debugging

Direct script execution is still useful for debugging.

### Socket-based detector

```bash
python openww.py [options]
```

Current options:

* `--chunk_size <samples>` default `1280`
* `--model_path <path[,path...]>`
* `--inference_framework <onnx|tflite>` default `onnx`
* `--socket_path <path>` default `/tmp/openww`
* `--detection_threshold <0.0-1.0>` default `0.3`

Example:

```bash
python openww.py \
  --model_path hey_cube.onnx,hey_cuba.onnx,hey_cube2.onnx,hey_cue.onnx \
  --detection_threshold 0.5
```

### Microphone utility

```bash
python detect_from_microphone.py [options]
```

This path is for direct local testing and is not how `CubeCore` uses the app in normal operation.

## Manual Setup Helper

`install.sh` creates a local virtual environment in this directory and installs the upstream `openwakeword` Python package.

That script is useful for quick standalone experimentation, but it is not the production TheCube app-runtime path. In the managed app model, runtime preparation is owned by `AppsManager`.

## Bundled Models

This directory currently includes:

* `hey_cuba.onnx`
* `hey_cube.onnx`
* `hey_cube2.onnx`
* `hey_cue.onnx`

## Known Gaps

Current follow-up items for this app:

* move the socket off `/tmp/openww` and into `THECUBE_RUNTIME_DIR`
* narrow and document the exact host-path grants needed under Landlock
* keep this README aligned with the app manifest and generated-policy workflow instead of treating the app as a standalone script first

## Attribution

This app is based on and uses code from the upstream [openWakeWord](https://github.com/dscripka/openWakeWord) project by David Scripka.

* Original project: https://github.com/dscripka/openWakeWord
* Original license: Apache License 2.0
* Upstream example used as a base: `detect_from_microphone.py`

## License

This directory continues to operate under the Apache License 2.0 terms used by the upstream project and this fork. See [LICENSE](LICENSE).
