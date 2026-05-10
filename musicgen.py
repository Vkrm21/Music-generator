import torch
import numpy as np
import scipy.io.wavfile as wavfile
from transformers import AutoProcessor, MusicgenForConditionalGeneration
from datetime import datetime


class ProMusicGen:

    def __init__(self):
        print("🔥 Loading MusicGen Pro...")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.processor = AutoProcessor.from_pretrained("facebook/musicgen-medium")
        self.model = MusicgenForConditionalGeneration.from_pretrained(
            "facebook/musicgen-medium"
        ).to(self.device)

        torch.backends.cudnn.benchmark = True

    # 🎯 Improve prompt quality automatically
    def enhance_prompt(self, user_prompt):
        base = [
            "trap beat",
            "hard 808 bass",
            "fast hi-hats",
            "dark melody",
            "clean mix",
            "studio quality",
            "wide stereo",
            "punchy drums"
        ]
        return user_prompt + ", " + ", ".join(base)

    # 🧱 Fake structure (intro → build → drop)
    def add_structure(self, audio):
        length = len(audio)

        intro = audio[:length // 3] * 0.5
        build = audio[length // 3: 2 * length // 3]
        drop = audio[2 * length // 3:] * 1.2

        return np.concatenate([intro, build, drop])

    # 🎧 Mastering chain
    def apply_mastering(self, audio):
        # Normalize
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = audio / max_val

        # Soft clipping (loudness)
        audio = np.tanh(audio * 2.5)

        # Bass boost (simple)
        bass = np.convolve(audio, np.ones(200) / 200, mode='same')
        audio = audio + 0.3 * bass

        # Stereo widening
        delay = 300
        stereo = np.stack([audio, np.roll(audio, delay)], axis=1)

        # Final limiter
        stereo = np.clip(stereo, -1, 1)

        return (stereo * 32767).astype(np.int16)

    # 🎵 Main generation
    def generate(self, user_prompt):
        return self.generate_custom(user_prompt, temperature=1.0, max_tokens=2048, top_k=250, top_p=0.95)

    def generate_custom(self, user_prompt, temperature=1.0, max_tokens=2048, top_k=250, top_p=0.95):
        print("🎧 Generating...")

        prompt = self.enhance_prompt(user_prompt)

        inputs = self.processor(
            text=[prompt],
            padding=True,
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            audio_values = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=True,
                top_k=top_k,
                top_p=top_p,
                temperature=temperature
            )

        audio = audio_values[0].cpu().numpy()

        # 🔧 Fix shape
        if audio.ndim == 3:
            audio = audio[0]

        if audio.ndim == 2:
            audio = audio.mean(axis=0)

        # 🧱 Add structure
        audio = self.add_structure(audio)

        # 🎧 Mastering
        final_audio = self.apply_mastering(audio)

        filename = f"musicgen_pro_{datetime.now().strftime('%H%M%S')}.wav"

        wavfile.write(filename, 32000, final_audio)

        return filename


if __name__ == "__main__":
    studio = ProMusicGen()

    print("\n--- 🔥 PRO AI MUSIC GENERATOR ---")

    prompt = input("Enter style: ")

    try:
        # Generate multiple versions (pro trick)
        for i in range(3):
            print(f"\n🎵 Version {i+1}")
            out = studio.generate(prompt)
            print(f"✅ Saved: {out}")

    except Exception as e:
        print(f"\n❌ Error: {e}") 