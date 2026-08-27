async function poll(endpoint, elementId) {
    try {
        const res = await fetch(endpoint);
        const data = await res.json();

        const box = document.getElementById(elementId);
        if (!box) return;

        box.innerHTML = "";

        data.forEach(item => {
            const div = document.createElement("div");
            div.className = "vm-log-item";
            div.innerHTML = `
                <span class="vm-log-time">${item.time}</span>
                <span class="vm-log-text">${item.text}</span>
            `;
            box.appendChild(div);
        });

    } catch (err) {
        console.error("Live update error:", err);
    }
}

setInterval(() => {
    poll("/api/live/dashboard", "dashboard-live-list");
    poll("/api/live/tickets", "tickets-live-list");
    poll("/api/live/ticket", "ticket-live-list");
    poll("/api/live/qna", "qna-live-list");
    poll("/api/live/autorole", "autorole-live-list");
    poll("/api/live/announcement", "announcement-live-list");
    poll("/api/live/ping", "ping-live-list");
}, 3000);
