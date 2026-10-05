import io
import wave
import numpy as np

from faster_whisper import WhisperModel


model = WhisperModel(
    "tiny",
    device="cpu",
    compute_type="int8",
    cpu_threads=1,
    num_workers=1
)


def transcribe_audio(audio_file):
    """Convert a recorded WAV file into a text string."""

    # Read the WAV recording directly from memory.
    with wave.open(io.BytesIO(audio_file.getvalue()), "rb") as wav:
        sample_rate = wav.getframerate()
        channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        frames = wav.readframes(wav.getnframes())

    # Streamlit normally records 16-bit PCM audio.
    if sample_width != 2:
        raise ValueError("Expected a 16-bit PCM WAV recording.")

    audio = np.frombuffer(frames, dtype=np.int16)

    # Convert stereo audio to mono if necessary.
    if channels > 1:
        audio = audio.reshape(-1, channels).mean(axis=1)

    # Whisper expects floating-point samples between -1 and 1.
    audio = audio.astype(np.float32) / 32768.0

    if sample_rate != 16000:
        raise ValueError(
            f"Expected 16000 Hz audio, received {sample_rate} Hz."
        )

    segments, info = model.transcribe(
        audio,
        beam_size=5
    )

    transcription = " ".join(
        segment.text.strip() for segment in segments
    )

    return transcription