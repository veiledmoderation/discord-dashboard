// Cyber animation initializer

document.addEventListener("DOMContentLoaded", () => {
    const slides = document.querySelectorAll(".cyber-slide");
    slides.forEach((el, i) => {
        el.style.animationDelay = `${i * 0.08}s`;
    });
});
