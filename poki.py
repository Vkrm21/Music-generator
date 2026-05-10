import torch
import numpy as np
import scipy.io.wavfile as wavfile
from scipy.signal import resample, butter, lfilter
from diffusers import AudioLDMPipeline
from datetime import datetime
import os
import glob
import random

class VolcanoHuggingFacePro:

    def __init__(self, model_id="cvssp/audioldm-s-full-v2"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if self.device == "cuda" else torch.float32

        print(f"🌋 Initializing Engine [{model_id}] on {self.device}...")

        self.pipe = AudioLDMPipeline.from_pretrained(
            model_id,
            torch_dtype=self.torch_dtype
        ).to(self.device)

    def apply_studio_mastering(self, audio):
        nyq = 0.5 * 44100

        # High-pass filter
        b, a = butter(5, 35 / nyq, btype='high')
        audio = lfilter(b, a, audio)

        # Transient boost
        envelope = np.abs(audio)
        audio = audio * (1 + 0.25 * envelope)

        # Saturation
        saturated = np.tanh(audio * 1.5)
        audio = (audio * 0.7) + (saturated * 0.3)

        # Stereo width
        delay = 441
        stereo = np.stack([audio, np.roll(audio, delay)], axis=1)

        # Limiter
        stereo = np.tanh(stereo * 2.2)

        return (stereo * 32767).astype(np.int16)

    def get_dna_context(self, base_path):
        all_wavs = glob.glob(os.path.join(base_path, "**", "*.wav"), recursive=True)

        if not all_wavs:
            return "hard trap rhythm", "vocal adlib"

        loops = [f for f in all_wavs if "Loop" in f]
        vox = [f for f in all_wavs if any(k in f for k in ["Vox", "Vocal", "Chop"])]

        r_dna = os.path.basename(random.choice(loops if loops else all_wavs)).split('.')[0]
        v_dna = os.path.basename(random.choice(vox if vox else all_wavs)).split('.')[0]

        return r_dna, v_dna

    def generate(self, pack_path, style_prompt):
        r_dna, v_dna = self.get_dna_context(pack_path)

        print(f"🔥 Generating...")
        print(f"🥁 Rhythm: {r_dna}")
        print(f"🎤 Vox: {v_dna}")

        prompt = (
            f"{style_prompt}, trap beat, hard 808s, punchy kick, rolling hi-hats, "
            f"dark melody, cinematic, studio quality, inspired by {r_dna} and {v_dna}"
        )

        # Controlled randomness
        generator = torch.Generator(device=self.device).manual_seed(
            random.randint(0, 100000)
        )

        with torch.no_grad():
            audio = self.pipe(
                prompt,
                num_inference_steps=150,
                guidance_scale=7.5,
                audio_length_in_s=12,
                generator=generator
            ).audios[0]

        # Resample to 44.1kHz
        num_samples = int(len(audio) * 44100 / 16000)
        audio = resample(audio, num_samples).astype(np.float32)

        # Mastering
        final_audio = self.apply_studio_mastering(audio)

        filename = f"volcano_{datetime.now().strftime('%M%S')}.wav"
        wavfile.write(filename, 44100, final_audio)

        return filename


if __name__ == "__main__":
    studio = VolcanoHuggingFacePro()

    pack_path = r"C:\Users\remie\OneDrive\Documents\Gen ai\Oversampled - VOLCANO"

    print("\n--- VOLCANO AI GENERATOR ---")
    style = input("Enter style: ")

    try:
        out = studio.generate(pack_path, style)
        print(f"\n✅ Done: {out}")
    except Exception as e:
        print(f"\n❌ Error: {e}")