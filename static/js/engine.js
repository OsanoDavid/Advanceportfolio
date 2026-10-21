window.addEventListener('DOMContentLoaded', () => {
    const loader = document.getElementById('system-loader');
    setTimeout(() => {
        loader.style.opacity = '0';
        setTimeout(() => { loader.style.visibility = 'hidden'; }, 400);
    }, 300);
});