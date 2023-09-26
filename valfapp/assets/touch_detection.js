if ('ontouchstart' in window) {
    document.getElementById('touch-support-output').textContent = 'touch';
} else {
    document.getElementById('touch-support-output').textContent = 'no-touch';
}
