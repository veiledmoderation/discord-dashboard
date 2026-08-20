document.addEventListener("DOMContentLoaded", () => {
    console.log("Rituals Dashboard Loaded");

    // Fade-in animation
    document.body.style.opacity = 0;
    setTimeout(() => {
        document.body.style.transition = "opacity 0.5s";
        document.body.style.opacity = 1;
    }, 50);
});
