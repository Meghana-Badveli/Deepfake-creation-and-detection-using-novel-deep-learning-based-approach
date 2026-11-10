document.addEventListener('DOMContentLoaded', () => {
    const cameraInput = document.getElementById('camera-input');
    const batchInput = document.getElementById('batch-input');
    const cameraDropZone = document.getElementById('camera-drop-zone');
    const batchDropZone = document.getElementById('batch-drop-zone');
    const submitBtn = document.getElementById('submit-btn');
    const resultsContainer = document.getElementById('results-container');
    const loading = document.getElementById('loading');
    
    // Webcam elements
    const openCameraBtn = document.getElementById('open-camera-btn');
    const captureBtn = document.getElementById('capture-btn');
    const uploadSingleBtn = document.getElementById('upload-single-btn');
    const webcamVideo = document.getElementById('webcam-video');
    const cameraPreviewContainer = document.getElementById('camera-preview-container');
    const cameraControls = document.querySelector('.camera-controls');

    let selectedFiles = [];
    let cameraImage = null; // Will store base64 or file object

    // Handle single image upload button
    uploadSingleBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        cameraInput.click();
    });

    cameraInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            cameraImage = e.target.files[0];
            showPreview(cameraImage, cameraPreviewContainer);
            stopCamera();
        }
    });

    // Handle batch upload click
    batchDropZone.addEventListener('click', () => batchInput.click());

    batchInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            selectedFiles = Array.from(e.target.files);
            const content = batchDropZone.querySelector('.drop-zone-content');
            content.innerHTML = `<i class="fas fa-check-circle fa-3x" style="color: var(--report-text)"></i><p>${selectedFiles.length} files selected</p>`;
        }
    });

    // Camera Logic
    openCameraBtn.addEventListener('click', async (e) => {
        e.stopPropagation();
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            webcamVideo.srcObject = stream;
            cameraPreviewContainer.style.display = 'none';
            cameraControls.style.display = 'block';
            captureBtn.style.display = 'inline-block';
            openCameraBtn.style.display = 'none';
        } catch (err) {
            console.error("Error accessing camera:", err);
            alert("Could not access camera. Please check permissions.");
        }
    });

    captureBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const canvas = document.getElementById('webcam-canvas');
        canvas.width = webcamVideo.videoWidth;
        canvas.height = webcamVideo.videoHeight;
        canvas.getContext('2d').drawImage(webcamVideo, 0, 0);
        
        canvas.toBlob((blob) => {
            cameraImage = new File([blob], "camera_capture.jpg", { type: "image/jpeg" });
            showPreview(cameraImage, cameraPreviewContainer);
            stopCamera();
        }, 'image/jpeg');
    });

    function stopCamera() {
        if (webcamVideo.srcObject) {
            webcamVideo.srcObject.getTracks().forEach(track => track.stop());
            webcamVideo.srcObject = null;
        }
        cameraControls.style.display = 'none';
        cameraPreviewContainer.style.display = 'block';
        captureBtn.style.display = 'none';
        openCameraBtn.style.display = 'inline-block';
    }

    function showPreview(file, container) {
        const reader = new FileReader();
        reader.onload = (e) => {
            container.innerHTML = `<img src="${e.target.result}" style="max-height: 150px; border-radius: 8px;">`;
        };
        reader.readAsDataURL(file);
    }

    // Submit Logic
    submitBtn.addEventListener('click', async () => {
        if (!cameraImage && selectedFiles.length === 0) {
            alert("Please capture an image or upload files first.");
            return;
        }

        resultsContainer.innerHTML = '';
        loading.style.display = 'block';
        submitBtn.disabled = true;

        const formData = new FormData();
        if (cameraImage) {
            formData.append('images', cameraImage);
        }
        selectedFiles.forEach(file => {
            formData.append('images', file);
        });

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error("Server error");

            const results = await response.json();
            displayResults(results);
        } catch (err) {
            console.error(err);
            alert("An error occurred during analysis.");
        } finally {
            loading.style.display = 'none';
            submitBtn.disabled = false;
        }
    });

    function displayResults(results) {
        resultsContainer.innerHTML = '';
        results.forEach(res => {
            const card = document.createElement('div');
            card.className = 'result-card';
            
            card.innerHTML = `
                <div class="image-side">
                    <h3>🖼️ Source: ${res.filename}</h3>
                    <img src="${res.image}" alt="Result Image">
                </div>
                <div class="report-side">
                    <h3>📋 Analysis Report</h3>
                    <div class="report-style">${res.report}</div>
                </div>
            `;
            resultsContainer.appendChild(card);
        });
    }
});
