document.addEventListener("DOMContentLoaded", () => {
    const rows = document.querySelectorAll(".vm-table tr");

    rows.forEach(row => {
        if (row.classList.contains("sla-red")) {
            row.style.background = "rgba(255,0,0,0.15)";
        }
        if (row.classList.contains("sla-yellow")) {
            row.style.background = "rgba(255,255,0,0.15)";
        }
        if (row.classList.contains("sla-green")) {
            row.style.background = "rgba(0,255,0,0.15)";
        }
    });
});
