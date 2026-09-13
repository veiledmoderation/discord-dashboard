document.addEventListener("DOMContentLoaded", () => {
    const rows = document.querySelectorAll(".vm-table tr");

    rows.forEach(row => {
        const ratingAvg = parseFloat(row.children[5]?.innerText || "0");

        if (ratingAvg >= 4.5) {
            row.style.background = "rgba(0,255,0,0.15)";
        } else if (ratingAvg <= 2) {
            row.style.background = "rgba(255,0,0,0.15)";
        }
    });
});
