let lastReportMarkdown = "";

function showToast(message, isError = false) {
    const toast = document.getElementById("toast");
    const toastMsg = document.getElementById("toast-msg");
    const toastIcon = document.getElementById("toast-icon");

    if (!toast || !toastMsg) return;

    toastMsg.innerText = message;
    if (isError) {
        toastIcon.className = "fa-solid fa-triangle-exclamation";
        toast.style.borderColor = "rgba(244, 63, 94, 0.4)";
        toast.style.background = "rgba(244, 63, 94, 0.15)";
    } else {
        toastIcon.className = "fa-solid fa-circle-check";
        toast.style.borderColor = "rgba(16, 185, 129, 0.4)";
        toast.style.background = "rgba(16, 185, 129, 0.15)";
    }

    toast.classList.remove("hidden");
    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.classList.add("hidden"), 300);
    }, 3000);
}

function setPrompt(text) {
    document.getElementById("user-query").value = text;
    showToast("Quick prompt loaded into query box");
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
        showToast("Please enter a request or select a prompt.", true);
        return;
    }

    runBtn.disabled = true;
    runBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> 5 Agents Collaborating...';

    // Reset Agent Status Cards
    const agents = ["planner", "researcher", "analyst", "reviewer", "reporter"];
    agents.forEach(a => setAgentState(a, "pending"));

    // Reset Outputs
    document.getElementById("report-placeholder").classList.remove("hidden");
    document.getElementById("report-rendered").classList.add("hidden");
    document.getElementById("report-rendered").innerHTML = "";
    agents.forEach(a => {
        document.getElementById(`output-${a}`).innerHTML = "<em>Processing agent output...</em>";
    });

    // Animate Step Progress
    let agentIdx = 0;
    setAgentState(agents[agentIdx], "running");
    const stepInterval = setInterval(() => {
        if (agentIdx < agents.length - 1) {
            setAgentState(agents[agentIdx], "completed");
            agentIdx++;
            setAgentState(agents[agentIdx], "running");
        }
    }, 1500);

    try {
        const selectedLanguage = document.getElementById("report-language") ? document.getElementById("report-language").value : "english";

        const response = await fetch("/api/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: query, language: selectedLanguage })
        });

        clearInterval(stepInterval);

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || "Server error occurred");
        }

        const data = await response.json();

        // Mark all completed & update outputs
        agents.forEach(a => setAgentState(a, "completed"));

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
        showToast("5-Agent Collaborative Pipeline Completed!");

    } catch (err) {
        clearInterval(stepInterval);
        showToast("Execution Error: " + err.message, true);
        agents.forEach(a => setAgentState(a, "pending"));
    } finally {
        runBtn.disabled = false;
        runBtn.innerHTML = '<i class="fa-solid fa-rocket"></i> Launch 5-Agent Pipeline';
    }
}

function copyReport() {
    if (!lastReportMarkdown) {
        showToast("No report generated to copy yet.", true);
        return;
    }
    navigator.clipboard.writeText(lastReportMarkdown);
    showToast("Report Markdown copied to clipboard!");
}

function downloadReport() {
    if (!lastReportMarkdown) {
        showToast("No report generated to download yet.", true);
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
    showToast("Report Markdown downloaded!");
}

function exportPDF() {
    if (!lastReportMarkdown) {
        showToast("No report generated to export as PDF yet.", true);
        return;
    }

    showToast("Generating high-contrast PDF document...");
    
    // Create dedicated high-contrast PDF container with watermark & SS emblem
    const pdfContainer = document.createElement("div");
    pdfContainer.className = "pdf-export-wrapper";
    
    pdfContainer.innerHTML = `
        <div class="pdf-watermark-overlay">MULTI-AGENT COLLABORATION</div>
        <div class="pdf-header">
            <div class="pdf-brand">
                <div class="pdf-ss-badge">SS</div>
                <div>
                    <h2 class="pdf-title">Multi-Agent AI Executive Report</h2>
                    <p class="pdf-subtitle">Autonomous 5-Agent Collaborative Pipeline (Planner • Researcher • Analyst • Reviewer • Reporter)</p>
                </div>
            </div>
            <div class="pdf-date">${new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })}</div>
        </div>
        <div class="pdf-divider"></div>
        <div class="pdf-body">
            ${marked.parse(lastReportMarkdown)}
        </div>
        <div class="pdf-footer-repeat">
            <div class="pdf-footer-brand">
                <span class="pdf-ss-mini-symbol">SS</span> Developed by <strong>SS</strong>
            </div>
            <div class="pdf-footer-note">Multi-Agent Collaboration AI Platform</div>
        </div>
    `;

    document.body.appendChild(pdfContainer);

    // PDF Export Settings (Crisp Black Text on White Page, Watermark on every page)
    const opt = {
        margin:       [10, 10, 15, 10],
        filename:     'multi_agent_collaborative_report.pdf',
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2, useCORS: true, backgroundColor: '#ffffff' },
        jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' },
        pagebreak:    { mode: ['avoid-all', 'css', 'legacy'] }
    };

    html2pdf().set(opt).from(pdfContainer).save().then(() => {
        document.body.removeChild(pdfContainer);
        showToast("PDF Export downloaded successfully!");
    }).catch(err => {
        if (document.body.contains(pdfContainer)) {
            document.body.removeChild(pdfContainer);
        }
        showToast("PDF Export failed: " + err.message, true);
    });
}
