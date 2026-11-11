let currentThreadId = localStorage.getItem("travel_thread_id") || null;
let latestAnswerMarkdown = "";

let pendingApproval = false;

function setPrompt(text) {
    document.getElementById("userInput").value = text;
}

function setLoading(isLoading) {
    const sendBtn = document.getElementById("sendBtn");
    const btnText = document.getElementById("btnText");
    const btnLoader = document.getElementById("btnLoader");

    sendBtn.disabled = isLoading;

    if (isLoading) {
        btnText.classList.add("hidden");
        btnLoader.classList.remove("hidden");
    } else {
        btnText.classList.remove("hidden");
        btnLoader.classList.add("hidden");
    }
}

function showError(message) {
    const errorBox = document.getElementById("errorBox");

    errorBox.textContent = message;
    errorBox.classList.remove("hidden");
}

function hideError() {
    const errorBox = document.getElementById("errorBox");

    errorBox.classList.add("hidden");
    errorBox.textContent = "";
}

function showApproval(data) {

    pendingApproval = true;

    document.getElementById("approveBtn").disabled = false;
    document.getElementById("rejectBtn").disabled = false;

    const resultSection = document.getElementById("resultSection");
    const resultBox = document.getElementById("resultBox");
    const approvalPanel = document.getElementById("approvalPanel");
    const threadInfo = document.getElementById("threadInfo");

    const itinerary =
        data.approval?.itinerary || data.itinerary || "";

    latestAnswerMarkdown = itinerary;

    if (typeof marked !== "undefined") {
        resultBox.innerHTML = marked.parse(itinerary);
    } else {
        resultBox.innerText = itinerary;
    }

    threadInfo.textContent = `Thread ID: ${data.thread_id}`;

    approvalPanel.classList.remove("hidden");

    document.getElementById("approvalFeedback").value = "";
    document.getElementById("approvalStatus").textContent = "";

    resultSection.classList.remove("hidden");

    resultSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


function showCompletedResult(data) {

    pendingApproval = false;

    const resultSection = document.getElementById("resultSection");
    const resultBox = document.getElementById("resultBox");
    const approvalPanel = document.getElementById("approvalPanel");
    const threadInfo = document.getElementById("threadInfo");

    const answer = data.answer || "No response generated.";

    latestAnswerMarkdown = answer;

    if (typeof marked !== "undefined") {
        resultBox.innerHTML = marked.parse(answer);
    } else {
        resultBox.innerText = answer;
    }

    threadInfo.textContent = `Thread ID: ${data.thread_id}`;

    approvalPanel.classList.add("hidden");

    resultSection.classList.remove("hidden");

    resultSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}

async function sendMessage() {

    hideError();

    const input = document.getElementById("userInput");
    const message = input.value.trim();

    if (!message) {
        showError("Please enter your travel request first.");
        return;
    }

    setLoading(true);

    document.getElementById("approvalPanel").classList.add("hidden");

    try {

        const response = await fetch("/api/travel", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: message,
                thread_id: currentThreadId
            })

        });

        const data = await response.json();

        if (!response.ok || data.success === false) {
            throw new Error(data.error || "Something went wrong.");
        }

        currentThreadId = data.thread_id;

        localStorage.setItem(
            "travel_thread_id",
            currentThreadId
        );

        if (data.status === "approval_required") {

            showApproval(data);

        } else if (data.status === "completed") {

            showCompletedResult(data);

        } else {

            throw new Error("Unexpected response from travel API.");

        }

    } catch (error) {

        showError(error.message);

    } finally {

        setLoading(false);

    }
}

async function submitApproval(decision) {

    if (!pendingApproval || !currentThreadId) {
        showError("No pending approval found.");
        return;
    }

    const approveBtn = document.getElementById("approveBtn");
    const rejectBtn = document.getElementById("rejectBtn");
    const status = document.getElementById("approvalStatus");

    const feedback = document
        .getElementById("approvalFeedback")
        .value.trim();

    approveBtn.disabled = true;
    rejectBtn.disabled = true;

    status.textContent = "Processing your decision...";

    try {

        const response = await fetch("/api/travel/approval", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                thread_id: currentThreadId,

                decision: decision,

                feedback: feedback

            })

        });

        const data = await response.json();

        if (!response.ok || data.success === false) {
            throw new Error(data.error || "Approval request failed.");
        }

        if (data.status !== "completed") {
            throw new Error("Unexpected approval response.");
        }

        showCompletedResult(data);

    } catch (error) {

        status.textContent = "";

        showError(error.message);

        approveBtn.disabled = false;
        rejectBtn.disabled = false;

    }

}

function copyResult() {
    const resultBox = document.getElementById("resultBox");
    const text = resultBox.innerText;

    if (!text) {
        return;
    }

    navigator.clipboard.writeText(text)
        .then(() => {
            const copyBtn = document.querySelector(".copy-btn");
            const oldText = copyBtn.textContent;

            copyBtn.textContent = "Copied!";

            setTimeout(() => {
                copyBtn.textContent = oldText;
            }, 1400);
        })
        .catch(() => {
            showError("Could not copy result.");
        });
}

function downloadPDF() {
    const pdfContent = document.getElementById("pdfContent");

    if (!latestAnswerMarkdown || !pdfContent) {
        showError("No travel plan available to download.");
        return;
    }

    const downloadBtn = document.querySelector(".download-btn");
    const oldText = downloadBtn.textContent;

    downloadBtn.textContent = "Preparing PDF...";
    downloadBtn.disabled = true;

    const options = {
        margin: 0.5,
        filename: "ai-travel-plan.pdf",
        image: {
            type: "jpeg",
            quality: 0.98
        },
        html2canvas: {
            scale: 2,
            useCORS: true,
            backgroundColor: "#ffffff"
        },
        jsPDF: {
            unit: "in",
            format: "a4",
            orientation: "portrait"
        },
        pagebreak: {
            mode: ["avoid-all", "css", "legacy"]
        }
    };

    html2pdf()
        .set(options)
        .from(pdfContent)
        .save()
        .then(() => {
            downloadBtn.textContent = oldText;
            downloadBtn.disabled = false;
        })
        .catch(() => {
            downloadBtn.textContent = oldText;
            downloadBtn.disabled = false;
            showError("Could not download PDF.");
        });
}

document.addEventListener("keydown", function(event) {
    if (event.ctrlKey && event.key === "Enter") {
        sendMessage();
    }
});