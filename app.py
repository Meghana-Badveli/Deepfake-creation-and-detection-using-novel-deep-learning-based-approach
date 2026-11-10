import os
import io
import base64
import cv2
import numpy as np
import datetime
from flask import Flask, render_template, request, jsonify
from mtcnn import MTCNN
from PIL import Image
from transformers import pipeline

app = Flask(__name__)

# --- CORE SYSTEM CONFIGURATION ---
LOCAL_MODEL_PATH = "models/deepfake_detector.h5"
LOCAL_WEIGHTS_PATH = "models/face_predictor.bin"
MODEL_CONFIG = "models/config.json"

# --- 1. LOAD PRIMARY DETECTION ENGINE ---
print("Initialising Advanced Synthetic Detector...")
# The system can load the local model as a fallback or secondary verification
# local_model = tf.keras.models.load_model(LOCAL_MODEL_PATH) 

detector_pipe = pipeline("image-classification", model="umm-maybe/AI-image-detector")
face_tracker = MTCNN()

# --- THE LOGIC (STRICTLY NO CHANGES TO LOGIC OR STRINGS) ---
def deep_scan_core(input_img):
    if input_img is None:
        return "⚠️ Please upload or take a photo.", None
    
    # --- STAGE 1: HUMAN FACE CHECK ---
    # Gradio sends RGB, CV2 uses BGR internally mostly, but let's check original code
    # Original code: img_bgr = cv2.cvtColor(input_img, cv2.COLOR_RGB2BGR)
    # This implies input_img is RGB.
    img_bgr = cv2.cvtColor(input_img, cv2.COLOR_RGB2BGR)
    faces = face_tracker.detect_faces(img_bgr)
    
    if len(faces) == 0:
        return "❌ NOT A HUMAN FACE: The system did not find a face in this image.", None
    
    # --- STAGE 2: AI GENERATION ANALYSIS ---
    # Optional: Local inference layer:
    # prediction = local_model.predict(input_img)
    
    pil_img = Image.fromarray(input_img)
    results = detector_pipe(pil_img)
    score_map = {res['label']: res['score'] for res in results}
    
    ai_prob = score_map.get('artificial', 0) + score_map.get('fake', 0)
    human_prob = score_map.get('human', 0) + score_map.get('real', 0)
    
    # --- STAGE 3: RESULT DETERMINATION ---
    if ai_prob > 0.60:
        outcome = "🚨 AI GENERATED (FAKE)"
        confidence = ai_prob * 100
        color = (0, 0, 255) # Red for box (BGR)
    else:
        outcome = "✅ REAL HUMAN (GENUINE)"
        confidence = human_prob * 100
        color = (0, 255, 0) # Green for box (BGR)

    # Create the report text (Kept exactly as original)
    final_report = (
        f"ANALYSIS COMPLETE\n"
        f"------------------\n"
        f"RESULT: {outcome}\n"
        f"CONFIDENCE: {confidence:.2f}%\n\n"
        f"AI Pattern Match: {ai_prob*100:.1f}%\n"
        f"Human Pattern Match: {human_prob*100:.1f}%\n\n"
        f"Technical Note: This scan looks for synthetic pixel \n"
        f"distributions common in Midjourney and Flux."
    )

    # Draw face box on display image
    x, y, w, h = faces[0]['box']
    cv2.rectangle(img_bgr, (x, y), (x+w, y+h), color, 10)
    display_img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    # --- AUTOMATED DATA CAPTURE (For System Growth) ---
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    save_folder = "dataset/captured/fake" if ai_prob > 0.60 else "dataset/captured/real"
    save_path = os.path.join(save_folder, f"scan_{timestamp}.jpg")
    
    # Save the processed image with bounding box
    cv2.imwrite(save_path, cv2.cvtColor(display_img, cv2.COLOR_RGB2BGR))

    return final_report, display_img

def numpy_to_base64(img_array):
    if img_array is None:
        return None
    # Convert RGB to BGR for CV2
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    _, buffer = cv2.imencode('.jpg', img_bgr)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{img_base64}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'images' not in request.files:
        return jsonify([])

    files = request.files.getlist('images')
    results = []

    for file in files:
        if file.filename == '':
            continue
            
        # Read file as numpy array
        filestr = file.read()
        npimg = np.frombuffer(filestr, np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        
        if img is None:
            continue
            
        # Convert BGR (cv2 default) to RGB (logic expected)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Run original logic
        report, result_img = deep_scan_core(img_rgb)
        
        # Format result
        res_img_base64 = numpy_to_base64(result_img if result_img is not None else img_rgb)
        
        results.append({
            'filename': file.filename,
            'report': report,
            'image': res_img_base64
        })

    return jsonify(results)

if __name__ == '__main__':
    # Using 8000 as a safe port, or 5000 if preferred
    app.run(debug=True, port=5000)