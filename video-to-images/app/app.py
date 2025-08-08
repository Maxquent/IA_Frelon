import os
import zipfile
import shutil
from flask import Flask, render_template, request, redirect, send_file
from werkzeug.utils import secure_filename
import subprocess

app = Flask(__name__)

# Configuration des chemins absolus
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'app/static/uploads')
app.config['IMAGE_FOLDER'] = os.path.join(BASE_DIR, 'app/static/images')
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov', 'mkv'}
app.config['ZIP_FOLDER'] = os.path.join(BASE_DIR, 'app/static/zips')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Créer le répertoire uploads si nécessaire
        upload_folder = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # Extraire les images
        extract_images(file_path)
        # Créer un fichier zip avec les images extraites
        zip_file = create_zip()
        # Supprimer les fichiers temporaires
        cleanup_files()
        
        # Retourner le fichier zip
        return send_file(zip_file, as_attachment=True, download_name='images.zip', mimetype='application/zip')
    return redirect(request.url)


def extract_images(video_path):
    """ Utiliser FFmpeg pour extraire les images de la vidéo """
    os.makedirs(app.config['IMAGE_FOLDER'], exist_ok=True)
    subprocess.run(['ffmpeg', '-i', video_path, '-vf', 'fps=1', os.path.join(app.config['IMAGE_FOLDER'], 'frame_%04d.jpg')])

def create_zip():
    """ Créer un fichier ZIP contenant toutes les images extraites """
    zip_filename = os.path.join(app.config['ZIP_FOLDER'], 'images.zip')
    os.makedirs(app.config['ZIP_FOLDER'], exist_ok=True)
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for root, dirs, files in os.walk(app.config['IMAGE_FOLDER']):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), app.config['IMAGE_FOLDER']))
    return zip_filename

def cleanup_files():
    """ Supprimer les fichiers temporaires après génération du zip """
    shutil.rmtree(app.config['UPLOAD_FOLDER'])
    shutil.rmtree(app.config['IMAGE_FOLDER'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
