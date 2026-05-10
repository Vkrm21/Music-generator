from flask import Flask, request, jsonify, send_file, render_template_string
import os
from musicgen import ProMusicGen
import threading
import time

app = Flask(__name__)

# Global generator instance
generator = None
generation_lock = threading.Lock()

def init_generator():
    global generator
    with generation_lock:
        if generator is None:
            generator = ProMusicGen()

@app.route('/')
def index():
    # Read the HTML file and serve it
    with open('promusicgen_frontend.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    return render_template_string(html_content)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        temperature = float(data.get('temperature', 1.0))
        max_tokens = int(data.get('max_tokens', 2048))
        top_k = int(data.get('top_k', 250))
        top_p = float(data.get('top_p', 0.95))
        versions = int(data.get('versions', 1))

        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400

        init_generator()

        results = []
        for i in range(versions):
            with generation_lock:
                filename = generator.generate_custom(
                    user_prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_k=top_k,
                    top_p=top_p
                )
            results.append({
                'filename': filename,
                'meta': f"32kHz · 16-bit · stereo · ~{max_tokens//64}s"  # Approximate duration
            })

        return jsonify({'tracks': results})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    try:
        return send_file(filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)