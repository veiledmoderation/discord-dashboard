const socket = io({ transports: ["websocket"] });

function addFeedItem(feedId, data) {
    const feed = document.getElementById(feedId);
    if (!feed) return;

    const item = document.createElement("div");
    item.className = "vm-log-item";
    item.innerHTML = `
        <span class="vm-log-time">${data.time}</span>
        <span class="vm-log-text">${data.text}</span>
    `;

    feed.prepend(item);

    while (feed.children.length > 50) {
        feed.removeChild(feed.lastChild);
    }
}

socket.on("tickets_feed", (data) => addFeedItem("ticket-feed", data));
socket.on("appeals_feed", (data) => addFeedItem("appeal-feed", data));
socket.on("staff_reports_feed", (data) => addFeedItem("staff-report-feed", data));
socket.on("sla_feed", (data) => addFeedItem("sla-feed", data));
socket.on("priority_feed", (data) => addFeedItem("priority-feed", data));
socket.on("assignment_feed", (data) => addFeedItem("assignment-feed", data));
