// Enhanced password match validation with better UI
function updatePasswordMatch() {
  const password = document.getElementById("new_password").value;
  const confirmPassword = document.getElementById("confirm_password").value;
  const matchMessage = document.getElementById("match-message");
  const matchIcon = document.getElementById("match-icon");
  const matchText = document.getElementById("match-text");
  const confirmField = document.getElementById("confirm_password");

  if (confirmPassword.length > 0) {
    matchMessage.classList.remove("hidden");
    
    if (password === confirmPassword) {
      confirmField.setCustomValidity("");
      confirmField.classList.remove("border-red-300", "focus:ring-red-500");
      confirmField.classList.add("border-green-300", "focus:ring-green-500");
      
      matchMessage.className = "text-xs mt-4 font-medium flex items-center space-x-1.5 text-green-600";
      matchIcon.innerHTML = `
        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
        </svg>
      `;
      matchText.textContent = "Passwords match";
    } else {
      confirmField.setCustomValidity("Passwords do not match");
      confirmField.classList.remove("border-green-300", "focus:ring-green-500");
      confirmField.classList.add("border-red-300", "focus:ring-red-500");

      matchMessage.className = "text-xs mt-4 font-medium flex items-center space-x-1.5 text-red-600";
      matchIcon.innerHTML = `
        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
        </svg>
      `;
      matchText.textContent = "Passwords do not match";
    }
  } else {
    confirmField.setCustomValidity("");
    confirmField.classList.remove("border-red-300", "focus:ring-red-500", "border-green-300", "focus:ring-green-500");
    matchMessage.classList.add("hidden");
  }
}

// Event listeners for password matching
document.getElementById('new_password').addEventListener('input', updatePasswordMatch);
document.getElementById('confirm_password').addEventListener('input', updatePasswordMatch);


//Eye toggle for password
document.getElementById('toggle_new_password').addEventListener('click', function () {
    const passwordInput = document.getElementById('new_password');
    const eyeOpen = document.getElementById('new_password_eye_open');
    const eyeClosed = document.getElementById('new_password_eye');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        eyeOpen.classList.add('hidden');
        eyeClosed.classList.remove('hidden');
    } else {
        passwordInput.type = 'password';
        eyeOpen.classList.remove('hidden');
        eyeClosed.classList.add('hidden');
    }
});

document.getElementById('toggle_confirm_password').addEventListener('click', function () {
    const passwordInput = document.getElementById('confirm_password');
    const eyeOpen = document.getElementById('confirm_password_eye_open');
    const eyeClosed = document.getElementById('confirm_password_eye');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        eyeOpen.classList.add('hidden');
        eyeClosed.classList.remove('hidden');
    } else {
        passwordInput.type = 'password';
        eyeOpen.classList.remove('hidden');
        eyeClosed.classList.add('hidden');
    }
});

// Form submission loading state
document.getElementById('changePasswordForm').addEventListener('submit', function() {
    // Button loading state
    const button = document.getElementById('submitButton');
    const buttonContent = button.querySelector('.button-content');
    const buttonSpinner = button.querySelector('.button-spinner');

    button.disabled = true;
    buttonContent.classList.add('hidden');
    buttonSpinner.classList.remove('hidden');

    // Preloader state
    const preloader = document.getElementById('preloader');
    const preloaderText = document.getElementById('preloader-text');
    
    preloaderText.textContent = 'Updating Password...';
    preloader.classList.remove('hidden');
});