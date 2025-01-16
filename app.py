from flask import Flask, render_template, request, send_file, redirect, url_for
from PIL import Image
import os
import io
from flask import send_from_directory

app = Flask(__name__)
app = Flask(__name__, template_folder="templates", static_folder="static", static_url_path="/")

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['STEGO_FOLDER'] = 'stego_outputs'
app.config['STEGO_EXTRACTS_UPLOAD_FOLDER'] = 'stego_extract_uploads'

# Ensure upload and stego folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['STEGO_FOLDER'], exist_ok=True)
os.makedirs(app.config['STEGO_EXTRACTS_UPLOAD_FOLDER'], exist_ok=True)


def embed_text(image_path, text):
    img = Image.open(image_path)
    encoded = img.copy()
    width, height = img.size
    data_index = 0
    text += '###'  # Delimiter to mark the end of text

    for x in range(width):
        for y in range(height):
            if data_index < len(text):
                r, g, b = img.getpixel((x, y))
                ascii_val = ord(text[data_index])
                encoded.putpixel((x, y), (r, ascii_val, b))
                data_index += 1
    return encoded


def extract_text(image_path):
    img = Image.open(image_path)
    width, height = img.size
    extracted_text = ""

    for x in range(width):
        for y in range(height):
            _, g, _ = img.getpixel((x, y))
            if chr(g) == '#':
                break
            extracted_text += chr(g)
    return extracted_text.strip('#')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/embed', methods=['POST'])
def embed():
    image = request.files['image']
    text = request.form['text']

    if not image or not text:
        return "Error: Image and text are required", 400
    
    
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    image.save(image_path)

    file_name = 'stego_' + os.path.splitext(image.filename)[0]
    file_path = '/stego_outputs/' + f'{file_name}.png'
    print(file_name)
    print(file_path)

    stego_image = embed_text(image_path, text)
    stego_path = os.path.join(app.config['STEGO_FOLDER'], f'{file_name}.png')
    stego_image.save(stego_path)

    return render_template('result.html', file_name=file_name, file_path=file_path)


@app.route('/extract')
def extract_page():
    return render_template('extract.html')


@app.route('/extract_text', methods=['POST'])
def extract_text_view():
    stego_image = request.files['stego_image']

    if not stego_image:
        return "Error: Stego image is required", 400

    image_path = os.path.join(app.config['STEGO_EXTRACTS_UPLOAD_FOLDER'], stego_image.filename)
    stego_image.save(image_path)

    extracted_text = extract_text(image_path)
    return render_template('extracted.html', extracted_text=extracted_text)


@app.route('/stego_outputs/<filename>')
def stego_outputs(filename):
    return send_from_directory(app.config['STEGO_FOLDER'], filename)


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
