let lastReportMarkdown = "";

function setPrompt(text) {
    document.getElementById("user-query").value = text;
}

function switchTab(tabId) {
    document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(content => content.classList.remove("active"));

    if (tabId === "final-report") {
        document.querySelectorAll(".tab-btn")[0].classList.add("active");
        document.getElementById("final-report").classList.add("active");
    } else {
        document.querySelectorAll(".tab-btn")[1].classList.add("active");
        document.getElementById("agent-outputs").classList.add("active");
    }
}

function toggleAccordion(id) {
    const el = document.getElementById(id);
    if (el) {
        el.classList.toggle("open");
    }
}

function setAgentState(agent, state) {
    const stepCard = document.getElementById(`step-${agent}`);
    const badge = document.getElementById(`badge-${agent}`);

    if (!stepCard || !badge) return;

    stepCard.classList.remove("active", "completed");
    badge.classList.remove("pending", "running", "completed");

    if (state === "running") {
        stepCard.classList.add("active");
        badge.classList.add("running");
        badge.innerText = "Processing...";
    } else if (state === "completed") {
        stepCard.classList.add("completed");
        badge.classList.add("completed");
        badge.innerText = "Done ✓";
    } else {
        badge.classList.add("pending");
        badge.innerText = "Waiting";
    }
}

async function startWorkflow() {
    const queryInput = document.getElementById("user-query");
    const runBtn = document.getElementById("run-btn");
    const query = queryInput.value.trim();

    if (!query) {
        alert("Please enter a request or select a quick prompt.");
        return;
    }

    runBtn.disabled = true;
    runBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Agents Collaborating...';

    // Reset Agent Status Cards
    ["planner", "researcher", "analyst", "reviewer", "reporter"].forEach(a => setAgentState(a, "pending"));

    // Reset Outputs
    document.getElementById("report-placeholder").classList.remove("hidden");
    document.getElementById("report-rendered").classList.add("hidden");
    document.getElementById("report-rendered").innerHTML = "";
    ["planner", "researcher", "analyst", "reviewer", "reporter"].forEach(a => {
        document.getElementById(`output-${a}`).innerHTML = "<em>Processing...</em>";
    });

    try {
        // Step 1: Planner
        setAgentState("planner", "running");
        
        const response = await fetch("/api/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: query })
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || "Server error occurred");
        }

        const data = await response.json();

        // Mark all completed & update outputs
        ["planner", "researcher", "analyst", "reviewer", "reporter"].forEach(a => setAgentState(a, "completed"));

        document.getElementById("output-planner").innerHTML = marked.parse(data.planner || "");
        document.getElementById("output-researcher").innerHTML = marked.parse(data.researcher || "");
        document.getElementById("output-analyst").innerHTML = marked.parse(data.analyst || "");
        document.getElementById("output-reviewer").innerHTML = marked.parse(data.reviewer || "");
        document.getElementById("output-reporter").innerHTML = marked.parse(data.reporter || "");

        // Render Final Report
        lastReportMarkdown = data.reporter || "";
        document.getElementById("report-placeholder").classList.add("hidden");
        const reportDiv = document.getElementById("report-rendered");
        reportDiv.innerHTML = marked.parse(lastReportMarkdown);
        reportDiv.classList.remove("hidden");

        switchTab("final-report");

    } catch (err) {
        alert("Execution Error: " + err.message);
        ["planner", "researcher", "analyst", "reviewer", "reporter"].forEach(a => setAgentState(a, "pending"));
    } finally {
        runBtn.disabled = false;
        runBtn.innerHTML = '<i class="fa-solid fa-rocket"></i> Launch 5-Agent Pipeline';
    }
}

function copyReport() {
    if (!lastReportMarkdown) {
        alert("No report generated to copy yet.");
        return;
    }
    navigator.clipboard.writeText(lastReportMarkdown);
    alert("Report markdown copied to clipboard!");
}

function downloadReport() {
    if (!lastReportMarkdown) {
        alert("No report generated to download yet.");
        return;
    }
    const blob = new Blob([lastReportMarkdown], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "multi_agent_report.md";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
