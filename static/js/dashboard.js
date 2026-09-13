document.addEventListener("DOMContentLoaded", () => {
    const cards = document.querySelectorAll(".vm-card");

    cards.forEach(card => {
        card.addEventListener("mouseenter", () => {
            card.style.boxShadow = "0 0 15px #0099ff";
        });
        card.addEventListener("mouseleave", () => {
            card.style.boxShadow = "0 0 10px #000";
        });
    });
});
