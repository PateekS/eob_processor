// File upload handling
document.getElementById("upload-form").onsubmit = function (e) {
    e.preventDefault();
    const formData = new FormData(this);
    fetch("/upload", {
        method: "POST",
        body: formData,
    })
        .then(response => {
            if (!response.ok) {
                throw new Error("File upload failed");
            }
            return response.json();
        })
        .then(data => {
            const statusList = document.getElementById("status-list");
            statusList.innerHTML = "<li>Files uploaded successfully and processing started.</li>";

            // Poll for status updates
            const interval = setInterval(() => {
                fetch("/status")
                    .then(response => response.json())
                    .then(statusUpdates => {
                        statusList.innerHTML = "";
                        statusUpdates.forEach(status => {
                            const li = document.createElement("li");
                            li.textContent = status;
                            statusList.appendChild(li);
                        });
                    });
            }, 1000);

            // Stop polling after 30 seconds
            setTimeout(() => clearInterval(interval), 30000);
        })
        .catch(error => {
            const statusList = document.getElementById("status-list");
            statusList.innerHTML = `<li>Error: ${error.message}</li>`;
            console.error("Upload error:", error);
        });
};

// Query handling
document.getElementById("query-form").onsubmit = function (e) {
    e.preventDefault();
    const query = document.getElementById("query-input").value.trim();
    if (!query) {
        document.getElementById("query-result").innerText = "Please enter a query.";
        return;
    }

    document.getElementById("query-result").innerText = "Processing your query...";

    fetch("/query", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
    })
        .then(response => {
            if (!response.ok) {
                throw new Error("Query failed");
            }
            return response.json();
        })
        .then(data => {
            if (data.answer) {
                document.getElementById("query-result").innerText = data.answer;
            } else if (data.error) {
                document.getElementById("query-result").innerText = `Error: ${data.error}`;
            }
        })
        .catch(error => {
            document.getElementById("query-result").innerText = `Error: ${error.message}`;
            console.error("Query error:", error);
        });
};
