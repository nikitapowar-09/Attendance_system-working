
  // const video = document.getElementById('video');
  // const captureBtn = document.getElementById('capture-image-btn');
  // const statusText = document.getElementById('register-status');
  // let stream = null;
  // let faceDetected = false;

  // // Load face-api.js models
  // Promise.all([
  //   faceapi.nets.tinyFaceDetector.loadFromUri('static\js\face-api.js-models-master')  // You must host the models
  // ]).then(() => {
  //   console.log("Face detection model loaded");
  // });

  // document.getElementById('start-capture-btn').addEventListener('click', async () => {
  //   stream = await navigator.mediaDevices.getUserMedia({ video: {} });
  //   video.srcObject = stream;
  //   video.style.display = 'block';
  //   captureBtn.style.display = 'none';
  //   statusText.textContent = 'Position your face in the center with good lighting...';

  //   // Start face detection loop
  //   const checkFace = async () => {
  //     const detection = await faceapi.detectSingleFace(video, new faceapi.TinyFaceDetectorOptions());
  //     if (detection) {
  //       statusText.textContent = "Face detected! You can capture now.";
  //       faceDetected = true;
  //       captureBtn.style.display = 'inline-block';
  //     } else {
  //       statusText.textContent = "No face detected. Keep your face straight, well-lit, and centered.";
  //       faceDetected = false;
  //       captureBtn.style.display = 'none';
  //     }
  //     requestAnimationFrame(checkFace);
  //   };

  //   checkFace();
  // });

  // captureBtn.addEventListener('click', () => {
  //   if (!faceDetected) {
  //     alert("No face detected. Please adjust your position.");
  //     return;
  //   }
  //   const canvas = document.getElementById('canvas');
  //   canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
  //   canvas.style.display = 'block';
  //   stream.getTracks().forEach(track => track.stop());
  //   video.style.display = 'none';
  //   captureBtn.style.display = 'none';

  //   const imageData = canvas.toDataURL('image/jpeg');

  //   fetch('/upload_captured_image', {
  //     method: 'POST',
  //     headers: { 'Content-Type': 'application/json' },
  //     body: JSON.stringify({ imageData })
  //   }).then(res => res.json())
  //     .then(data => statusText.textContent = data.message)
  //     .catch(err => statusText.textContent = "Error uploading: " + err.message);
  // });const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const startBtn = document.getElementById('start-capture-btn');
const captureBtn = document.getElementById('capture-image-btn');
const hiddenInput = document.getElementById('captured_image');

let stream = null;

startBtn.addEventListener('click', async () => {
    stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
    video.style.display = 'block';
    captureBtn.style.display = 'inline-block';
});

captureBtn.addEventListener('click', () => {
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.style.display = 'block';
    video.style.display = 'none';

    // Stop the camera
    stream.getTracks().forEach(track => track.stop());

    // Convert to base64
    const imageData = canvas.toDataURL('image/jpeg');
    hiddenInput.value = imageData;
});
