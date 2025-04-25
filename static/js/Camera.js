
let video = document.getElementById("video");
let canvas = document.getElementById("canvas");
let capturedImageInput = document.getElementById("captured_image");
let startCameraBtn = document.getElementById("start-capture-btn");
let captureImageBtn = document.getElementById("capture-image-btn");

let cameraStarted = false;

// Load face-api.js model
Promise.all([
  faceapi.nets.tinyFaceDetector.loadFromUri('/static/js/face-api.js-models-master/models')
]).then(() => {
  console.log("FaceAPI models loaded");
});

// Check if camera is available
navigator.mediaDevices.enumerateDevices()
  .then(devices => {
    const hasVideoInput = devices.some(device => device.kind === 'videoinput');
    if (!hasVideoInput) {
      Swal.fire("No Camera", "No camera found. Please connect a webcam.", "error");
    }
  });

startCameraBtn.addEventListener("click", async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
    video.style.display = "block";
    captureImageBtn.style.display = "inline-block";
    cameraStarted = true;
  } catch (err) {
    Swal.fire("Error", "Camera access denied. Please allow permission to continue.", "error");
  }
});

captureImageBtn.addEventListener("click", async () => {
  if (!cameraStarted) {
    Swal.fire("Warning", "Camera is not started. Click 'Start Camera' first.", "warning");
    return;
  }

  const context = canvas.getContext("2d");
  const frames = [];
  const captures = 5;
  const delay = 250;

  let capturedCount = 0;

  const captureFrames = async (count) => {
    if (count === 0) {
      if (frames.length === 0) {
        Swal.fire("Error", "No valid face captured. Please try again.", "error");
        return;
      }

      frames.forEach((dataUrl) => {
        const input = document.createElement("input");
        input.type = "hidden";
        input.name = "captured_images[]";
        input.value = dataUrl;
        document.querySelector("form").appendChild(input);
      });

      Swal.fire("Success", `Captured ${frames.length} valid face images.`, "success");
      return;
    }

    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const detection = await faceapi.detectSingleFace(canvas, new faceapi.TinyFaceDetectorOptions());

    if (detection) {
      const dataUrl = canvas.toDataURL("image/jpeg");
      frames.push(dataUrl);
      capturedCount++;
    }

    setTimeout(() => captureFrames(count - 1), delay);
  };

  captureFrames(captures);
});

