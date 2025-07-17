let startTime;
    let videoStream = null;

    const targetSentences = [
      "The quick brown fox jumps over the lazy dog.",
      "Debugging is like being the detective in a crime movie.",
      "Simplicity is the soul of efficiency.",
      "A bug in the code is worth two in production.",
      "Great code is its own best documentation."
    ];

    function startTyping() {
      const selected = targetSentences[Math.floor(Math.random() * targetSentences.length)];
      document.getElementById("targetSentence").innerText = selected;
      document.getElementById("typingHint").innerText="";
      document.getElementById("startType").disabled=true;
      const input = document.getElementById("typingBox");
      input.value = "";
      input.disabled = false;
      input.focus();
      startTime = new Date().getTime();

      input.oninput = () => {
        // auto-finish when full length is typed
        if (input.value.length >= selected.length) {
          finishTyping(selected);
        }
      };

      input.onkeydown = function(e) {
        if (e.key === 'Enter') {
          e.preventDefault();
          finishTyping(selected);
        }
      };
    }

    function finishTyping(selected) {
      const endTime = new Date().getTime();
      const typed = document.getElementById("typingBox").value;
      const timeTaken = (endTime - startTime) / 1000.0;

      const targetWords = selected.trim().split(" ");
      const typedWords = typed.trim().split(" ");
      let typos = 0;

      for (let i = 0; i < Math.min(targetWords.length, typedWords.length); i++) {
        if (targetWords[i] !== typedWords[i]) typos++;
      }
      typos += Math.abs(targetWords.length - typedWords.length);

      const correctWords = Math.max(targetWords.length - typos, 0);
      const wpm = (correctWords / timeTaken) * 60;

      document.getElementById("typingResult").innerText =
        `✅ Typing Speed: ${wpm.toFixed(2)} WPM | ❌ Typos: ${typos}`;
      document.getElementById("typing_speed").value = wpm.toFixed(2);
      document.getElementById("typos").value = typos;
      document.getElementById("typingBox").disabled = true;
    }

    async function startCamera() {
      try {
        videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
        const video = document.getElementById("video");
        video.srcObject = videoStream;
        video.style.display = "block";
        document.getElementById("snapBtn").style.display = "inline-block";
      } catch (err) {
        alert("⚠️ Could not access webcam.");
      }
    }

    function stopCamera() {
      if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
      }
      document.getElementById("video").style.display = "none";
      document.getElementById("snapBtn").style.display = "none";
    }

    function captureImage() {
      const video = document.getElementById("video");
      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.getContext("2d").drawImage(video, 0, 0);

      canvas.toBlob(function(blob) {
        replaceFileInputWithBlob(blob, "webcam.jpg");
        showImagePreview(blob);
        document.getElementById("emotionResult").innerText = "🧠 Captured via webcam.";
      }, "image/jpeg");

      stopCamera();
    }

    function storeUploadedImage(file) {
      if (file) {
        replaceFileInputWithBlob(file, file.name);
        showImagePreview(file);
        document.getElementById("emotionResult").innerText = `🧠 Uploaded: ${file.name}`;
      }
    }

    function replaceFileInputWithBlob(blob, filename) {
      const dt = new DataTransfer();
      const newFile = new File([blob], filename, { type: blob.type });
      dt.items.add(newFile);
      const finalInput = document.getElementById("finalImageInput");
      finalInput.files = dt.files;
    }

    function showImagePreview(blobOrFile) {
      const preview = document.getElementById("imagePreview");
      const reader = new FileReader();
      reader.onload = function (e) {
        preview.src = e.target.result;
        preview.style.display = "block";
      };
      reader.readAsDataURL(blobOrFile);
    }