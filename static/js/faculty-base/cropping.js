// Get DOM elements
const cropperModal = document.getElementById('cropperModal');
const imageToCrop = document.getElementById('imageToCrop');
const fileInput = document.getElementById('profileImageInput');
const cropAndSaveButton = document.getElementById('cropAndSaveButton');
const profileImageForm = document.getElementById('profileImageForm');
const croppedImageDataInput = document.getElementById('croppedImageData');
const profilePreview = document.getElementById('profilePreview');

let cropper;

// Trigger when a user selects a file
fileInput.addEventListener('change', (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
        const reader = new FileReader();
        reader.onload = (event) => {
            imageToCrop.src = event.target.result;
            cropperModal.classList.remove('hidden');
            
            // Initialize Cropper.js
            if (cropper) {
                cropper.destroy();
            }
            cropper = new Cropper(imageToCrop, {
                aspectRatio: 1 / 1, // Square crop (1080x1080)
                viewMode: 2, // Restrict crop box to not exceed the size of the canvas
                dragMode: 'move', // Allow dragging the image to reposition
                background: false,
                autoCropArea: 1, // Full crop area
                responsive: true,
                restore: false,
                guides: true,
                center: true,
                highlight: false,
                cropBoxMovable: true,
                cropBoxResizable: false, // Fixed size crop box
                toggleDragModeOnDblclick: false,
            });
        };
        reader.readAsDataURL(files[0]);
    }
});

// Function to close the cropper modal
function closeCropperModal() {
    cropperModal.classList.add('hidden');
    if (cropper) {
        cropper.destroy();
    }
    // Reset file input to allow selecting the same file again
    fileInput.value = ''; 
}

// Handle the "Crop & Save" button click
cropAndSaveButton.addEventListener('click', () => {
    if (cropper) {
        // Get the cropped image as a canvas with 1080x1080 dimensions
        const canvas = cropper.getCroppedCanvas({
            width: 1080,
            height: 1080,
            imageSmoothingEnabled: true,
            imageSmoothingQuality: 'high',
        });

        // Convert canvas to a Base64 string (JPEG for smaller size)
        const croppedImageData = canvas.toDataURL('image/jpeg', 0.9);
        
        // Put the Base64 string into our hidden form input
        croppedImageDataInput.value = croppedImageData;

        // Update the preview image on the page
        profilePreview.src = croppedImageData;
        
        // Submit the form to the server
        profileImageForm.submit();
    }
});