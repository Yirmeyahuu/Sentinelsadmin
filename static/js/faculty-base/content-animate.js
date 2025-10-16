// HTMX Transition Effects
document.body.addEventListener('htmx:beforeSwap', function(evt) {
    const main = document.getElementById('mainContent');
    if (main) {
        main.style.transition = '';
        main.style.transform = 'translateX(-80px)';
        main.style.opacity = 0;
    }
});

document.body.addEventListener('htmx:afterSwap', function() {
    const main = document.getElementById('mainContent');
    if (main) {
        main.style.transition = 'transform 0.2s cubic-bezier(0.4,0,0.2,1), opacity 0.2s cubic-bezier(0.4,0,0.2,1)';
        setTimeout(() => {
            main.style.transform = 'translateX(0)';
            main.style.opacity = 1;
        }, 10);
    }
});