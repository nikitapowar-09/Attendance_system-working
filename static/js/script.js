const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const attendanceForm = document.getElementById('attendance-form');
const attendanceStatus = document.getElementById('attendance-status');
const captureFaceBtn = document.getElementById('capture-face-btn');

// Handle Attendance Form Submission
attendanceForm.addEventListener('submit', async (event) => {
  event.preventDefault(); // Prevent form from submitting normally

  const employeeId = document.getElementById('attendance-id').value;

  // Validate that the Employee ID is a 4-digit number
  const isValidId = /^\d{4}$/.test(employeeId); // Regex to check for 4 digits

  if (!employeeId) {
    attendanceStatus.textContent = "Please enter an Employee ID.";
    return;
  }

  if (!isValidId) {
    attendanceStatus.textContent = "Please enter a valid 4-digit Employee ID.";
    return;
  }

  attendanceStatus.textContent = "Starting face capture...";

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
    video.style.display = 'block';

    captureFaceBtn.style.display = 'block'; // Show capture face button
    captureFaceBtn.onclick = () => {
      // Capture Face
      const context = canvas.getContext('2d');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Stop the video stream
      const tracks = stream.getTracks();
      tracks.forEach(track => track.stop());
      video.style.display = 'none';

      captureFaceBtn.style.display = 'none';

      // Simulate face matching process
      const isFaceMatched = Math.random() > 0.5; // Simulating face matching success randomly

      if (isFaceMatched) {
        attendanceStatus.textContent = `Attendance marked successfully for Employee ID: ${employeeId}.`;
      } else {
        attendanceStatus.textContent = `Face does not match for Employee ID: ${employeeId}. Please try again.`;
      }
    };
  } catch (error) {
    console.error("Camera access error:", error);
    attendanceStatus.textContent = "Error accessing camera. Please check permissions.";
  }
});
