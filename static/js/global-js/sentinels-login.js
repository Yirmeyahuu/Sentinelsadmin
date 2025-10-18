document.getElementById('togglePassword').addEventListener('click', function (e) {
    e.preventDefault(); // Prevent form submission
    const passwordInput = document.getElementById('password');
    const eyeOpen = document.getElementById('eyeOpen');
    const eyeClosed = document.getElementById('eyeClosed');
    
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

document.getElementById('loginForm').addEventListener('submit', function() {
    // Button loading state
    const button = document.getElementById('submitButton');
    const buttonText = button.querySelector('.button-text');
    const buttonArrow = button.querySelector('.button-arrow');
    const buttonSpinner = button.querySelector('.button-spinner');

    button.disabled = true;
    buttonText.textContent = 'Logging In...';
    buttonArrow.classList.add('hidden');
    buttonSpinner.classList.remove('hidden');

    // Preloader state
    const preloader = document.getElementById('preloader');
    const preloaderText = document.getElementById('preloader-text');
    
    preloaderText.textContent = 'Logging In...';
    preloader.classList.remove('hidden');
});