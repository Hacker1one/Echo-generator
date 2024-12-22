from flask import Flask, request, send_file, render_template
import os
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'mp3', 'wav'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'file' not in request.files:
        return 'No file uploaded', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No file selected', 400
    
    if file and allowed_file(file.filename):
        try:
            matlab_path = "/Applications/MATLAB_R2024b.app/bin/matlab"
            
            alpha = float(request.form.get('alpha', 0.5))
            delay = float(request.form.get('delay', 2.0))
            
            filename = secure_filename(file.filename)
            input_path = os.path.join(os.path.abspath(app.config['UPLOAD_FOLDER']), filename)
            file.save(input_path)
            
            output_filename = 'output_' + filename
            output_path = os.path.join(os.path.abspath(app.config['OUTPUT_FOLDER']), output_filename)
            
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            matlab_cmd = f'cd("{current_dir}"); echo_process("{input_path}","{output_path}",{alpha},{delay})'
            
            process = subprocess.Popen([
                matlab_path,
                '-nodisplay',
                '-nosplash',
                '-nodesktop',
                '-r',
                f'try; {matlab_cmd}; catch e; disp(e.message); end; quit;'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                print("MATLAB Output:", stdout.decode())
                print("MATLAB Error:", stderr.decode())
                return f'MATLAB Error: {stderr.decode()}', 500
            
            if not os.path.exists(output_path):
                return 'Output file not generated', 500
                
            return send_file(output_path, as_attachment=True)
            
        except FileNotFoundError as e:
            return str(e), 500
        except Exception as e:
            return f'Error processing audio: {str(e)}', 500
    
    return 'Invalid file type', 400

if __name__ == '__main__':
    app.run(debug=True)