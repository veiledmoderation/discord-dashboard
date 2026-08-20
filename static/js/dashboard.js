function runCommand(event, cmdName) {
    event.preventDefault();

    const form = event.target;
    const data = {};

    Array.from(form.elements).forEach(el => {
        if (el.name) {
            data[el.name] = el.value;
        }
    });

    fetch(`/run-command/${cmdName}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
        .then(res => res.json())
        .then(json => {
            const result = document.getElementById("command-result");
            if (!result) return;

            result.innerHTML = `
                <strong>Status:</strong> ${json.status}<br>
                <strong>Message:</strong> ${json.message || ""}
            `;
        })
        .catch(err => {
            const result = document.getElementById("command-result");
            if (!result) return;
            result.textContent = "Error running command.";
            console.error(err);
        });
}
