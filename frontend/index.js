const BASE_URL = 'https://desktop-sm21qic.tail63492a.ts.net';
const insightUrlMap = {};
let currentGroupTaskId = null;
let lastInsightPdfFilename = null;
let groupInsightGenerated = false; // Track if insight has been generated
let groupInsightData = null; // Store the insight data

const tabInsightCache = {
    personal: null,
    dual: null,
    group: null,
    translate: null,
};
const tabInsightPdfCache = {
    personal: null,
    dual: null,
    group: null,
    translate: null,
};


// Tab switching functionality
function showTab(tabId) {
    console.log('Switching to tab:', tabId);

    // Hide all modals first
    hideAllModals();

    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.classList.remove('active');
    });

    // Show the selected tab content
    document.getElementById(tabId).classList.add('active');

    // Update tab buttons
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.classList.remove('active');
    });
    tabs.forEach(tab => {
        if (tab.getAttribute('onclick') === `showTab('${tabId}')`) {
            tab.classList.add('active');
        }
    });

    // Reset form states when switching tabs (but preserve insights)
    if (tabId === 'personal') {
        resetFormState('personalForm');
    } else if (tabId === 'group') {
        resetFormState('groupZipForm');
        // Update button state based on available insight
        updateShowInsightButton();
    } else if (tabId === 'dual') {
        resetFormState('dualForm');
    }

    // Hide all insight previews except for the current tab
    document.querySelectorAll('.insight-preview').forEach(div => {
        if (!div.id.startsWith(tabId)) {
            div.innerHTML = '';
            div.style.display = 'none';
        }
    });

    // Restore cached insight for this tab, if available
    const cacheMap = {
        personal: 'personal',
        dual: 'dual',
        group: 'group',
        translate: 'translate'
    };

    if (cacheMap[tabId] && tabInsightCache[tabId]) {
        console.log(`Restoring cached insight for ${tabId}`);
        showInsightInTab(tabId, tabInsightCache[tabId], tabInsightPdfCache[tabId]);

        // For group tab, also update the button state
        if (tabId === 'group') {
            groupInsightGenerated = true; // Mark as generated since we have cached data
            updateShowInsightButton();

            // Show a status message that insight is available
            showStatus('groupStatus', '<strong>SUCCESS:</strong> Group insight is displayed below.', 'success');
        }
    }
}



// Utility functions
function showStatus(elementId, message, type = 'processing') {
    const statusEl = document.getElementById(elementId);

    // Check if the element exists
    if (!statusEl) {
        console.warn(`Status element '${elementId}' not found. Creating temporary status display.`);

        // For dual form, we might need to create or find the status element differently
        if (elementId === 'dualStatus') {
            // Try to find the dual form and add status there
            const dualForm = document.getElementById('dual');
            if (dualForm) {
                let existingStatus = dualForm.querySelector('.status');
                if (!existingStatus) {
                    // Create a new status element
                    existingStatus = document.createElement('div');
                    existingStatus.id = 'dualStatus';
                    existingStatus.className = 'status';

                    // Find a good place to insert it (after the form)
                    const form = dualForm.querySelector('form');
                    if (form) {
                        form.parentNode.insertBefore(existingStatus, form.nextSibling);
                    } else {
                        dualForm.appendChild(existingStatus);
                    }
                }

                // Now use this element
                existingStatus.className = `status ${type}`;
                existingStatus.style.display = 'flex';
                existingStatus.style.alignItems = 'center';
                existingStatus.innerHTML = '';

                const messageEl = document.createElement('div');
                messageEl.innerHTML = message;
                existingStatus.appendChild(messageEl);

                console.log(`Created/found status element for dual form`);
                return;
            }
        }

        // Fallback: just log the message
        console.log(`Status (${type}): ${message}`);
        return;
    }

    // Original logic for existing elements
    statusEl.className = `status ${type}`;
    statusEl.style.display = 'flex';
    statusEl.style.alignItems = 'center';
    statusEl.innerHTML = '';

    const messageEl = document.createElement('div');
    messageEl.innerHTML = message;
    statusEl.appendChild(messageEl);
}


function hideStatus(elementId) {
    document.getElementById(elementId).style.display = 'none';
}


document.getElementById('translateForm').addEventListener('submit', async (e) => {
e.preventDefault();
const fileInput = document.getElementById('translateFile');

if (!fileInput.files[0]) {
    alert('Please select a PDF file');
    return;
}

try {
    showStatus('translateStatus', '<strong>PROCESSING:</strong> Processing translation request...', 'processing');

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    const response = await fetch(`${BASE_URL}/translate`, {
        method: 'POST',
        body: formData
    });

    const result = await response.json();

    if (response.ok) {
        pollTaskStatus(result.task_id, 'translateStatus');
    } else {
        showStatus('translateStatus', `<strong>ERROR:</strong> ${result.detail}`, 'error');
    }
} catch (error) {
    showStatus('translateStatus', `<strong>CONNECTION ERROR:</strong> ${error.message}`, 'error');
}
});
function updateProgress(elementId, percent) {
const progressFill = document.querySelector(`#${elementId} .progress-fill`);
if (progressFill) {
    // If we have actual progress data, switch from animation to actual progress
    if (percent > 0) {
        progressFill.classList.remove('animated');
        progressFill.classList.add('with-progress');
        progressFill.style.width = `${percent}%`;
    }
}
}

function addDownloadButton(elementId, taskId, filename, label = 'Download Report') {
    const statusEl = document.getElementById(elementId);

    // First, make the status element a flex container
    statusEl.style.display = 'flex';
    statusEl.style.justifyContent = 'space-between';
    statusEl.style.alignItems = 'center';
    statusEl.style.flexWrap = 'wrap';

    // Create the download button
    const downloadBtn = document.createElement('button');
    downloadBtn.className = 'btn download-btn';
    downloadBtn.innerHTML = label;
    downloadBtn.style.display = 'inline-flex';
    downloadBtn.style.marginLeft = 'auto'; // Push to the right
    downloadBtn.onclick = () => downloadFile(taskId, filename);

    // Append the button directly to the status element
    statusEl.appendChild(downloadBtn);
}
// Enable Get Insight button after PDF is generated
function enableGetInsightButton(formId, downloadUrl, statusId) {
    const form = document.getElementById(formId);
    if (form) {
        const btn = form.querySelector('button.get-insight-btn');
        if (btn) {
            btn.disabled = false;
            btn.textContent = "Get Insight";
            btn.style.background = "linear-gradient(135deg, #dc2626, #a30e0e)";
            btn.style.color = "#fff";
            btn.onclick = null; // Remove any existing click handler!
            if (formId === 'dualForm') {
                btn.addEventListener("click", function handler() {
                    // Save downloadUrl for use after user selects
                    window.__dualDownloadUrl = downloadUrl;
                    window.__dualStatusId = statusId;
                    window.__dualFormId = formId;
                    window.__dualBtnRef = btn;
                    openDualInsightChoiceModal();
                }, { once: true });
            } else {
                btn.addEventListener("click", async function handler() {
                    showLoadingOverlay({
                        text: "Generating your personal MBTI Insight...",
                        tip: "Hang tight, this may take up to a minute."
                    });

                    btn.disabled = true;
                    btn.style.background = "#a3a3a3";
                    btn.style.color = "#fff";

                    const formData = new FormData();
                    formData.append('download_url', downloadUrl);

                    try {
                        const response = await fetch(`${BASE_URL}/insight-by-download-url`, {
                            method: 'POST',
                            body: formData
                        });
                        const result = await response.json();

                        if (response.ok) {
                            pollInsightStatus(result.task_id, statusId, formId, btn);
                        } else {
                            hideLoadingOverlay();
                            showStatus(statusId, `<strong>ERROR:</strong> ${result.detail}`, 'error');
                            btn.disabled = false;
                            btn.textContent = "Get Insight";
                        }
                    } catch (error) {
                        hideLoadingOverlay();
                        showStatus(statusId, `<strong>CONNECTION ERROR:</strong> ${error.message}`, 'error');
                        btn.disabled = false;
                        btn.textContent = "Get Insight";
                    }
                }, { once: true });
            }
        }
    }
}

// Download function that downloads from output/filename
async function downloadFile(taskId, filename) {
    try {
        const response = await fetch(`${BASE_URL}/output/${filename}`);
        if (!response.ok) {
            throw new Error('Download failed');
        }

        return handleDownloadResponse(response, filename);
    } catch (error) {
        alert(`Download failed: ${error.message}`);
    }
}

// Helper function to handle the download response
async function handleDownloadResponse(response, filename) {
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);

    // Create temporary link element to trigger download
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = filename;

    // Add to DOM, click, and remove
    document.body.appendChild(a);
    a.click();

    // Cleanup
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}
// Similarly, update other form submissions to pass the formId


// Polling function to check task status
// Updated button switching logic with proper class management

function showDownloadButton(formId, downloadUrl, filename = null) {
    let generateBtn, downloadBtn;

    if (formId === 'personalForm') {
        generateBtn = document.getElementById('personalGenerateBtn');
        downloadBtn = document.getElementById('personalDownloadBtn');
        filename = filename || 'personal_report.pdf';
    } else if (formId === 'groupZipForm') {
        generateBtn = document.getElementById('groupGenerateBtn');
        downloadBtn = document.getElementById('groupDownloadBtn');
        filename = filename || 'group_report.xlsx';
    } else if (formId === 'dualForm') {
        generateBtn = document.getElementById('dualGenerateBtn');
        downloadBtn = document.getElementById('dualDownloadBtn');
        filename = filename || 'dual_report.pdf';
    }

    if (generateBtn && downloadBtn) {
        // Hide generate button
        generateBtn.classList.add('hide');

        // Show download button
        downloadBtn.classList.add('show');
        downloadBtn.style.display = 'flex';
        downloadBtn.disabled = false;

        // Setup download functionality
        downloadBtn.onclick = async function(e) {
            e.preventDefault();

            try {
                const fullDownloadUrl = downloadUrl.startsWith('http')
                    ? downloadUrl
                    : `${BASE_URL}${downloadUrl}`;

                const response = await fetch(fullDownloadUrl);
                if (!response.ok) {
                    throw new Error('Download failed');
                }

                // Extract filename from URL if not provided
                if (!filename) {
                    const urlParts = fullDownloadUrl.split('/');
                    filename = urlParts[urlParts.length - 1] || 'report.pdf';
                }

                await handleDownloadResponse(response, filename);
            } catch (error) {
                alert(`Download failed: ${error.message}`);
            }
        };
    }
}

function resetFormState(formId) {
    let generateBtn, downloadBtn;

    if (formId === 'personalForm') {
        generateBtn = document.getElementById('personalGenerateBtn');
        downloadBtn = document.getElementById('personalDownloadBtn');
    } else if (formId === 'groupZipForm') {
        generateBtn = document.getElementById('groupGenerateBtn');
        downloadBtn = document.getElementById('groupDownloadBtn');
    } else if (formId === 'dualForm') {
        generateBtn = document.getElementById('dualGenerateBtn');
        downloadBtn = document.getElementById('dualDownloadBtn');
    }

    if (generateBtn && downloadBtn) {
        // Show generate button
        generateBtn.classList.remove('hide');
        generateBtn.style.visibility = 'visible';
        generateBtn.style.opacity = '1';

        // Hide download button
        downloadBtn.classList.remove('show');
        downloadBtn.style.display = 'none';
        downloadBtn.style.visibility = 'hidden';
        downloadBtn.style.opacity = '0';
    }
}

// Updated pollTaskStatus function with better button management
async function pollTaskStatus(taskId, statusElementId, formId) {
    const maxAttempts = 60;
    let attempts = 0;

    const poll = async () => {
        try {
            const response = await fetch(`${BASE_URL}/status/${taskId}`);
            const status = await response.json();

            if (status.progress !== undefined) {
                updateProgress(statusElementId, status.progress);
            }

            const statusIcon = {
                'pending': '⏳',
                'processing': '🔄',
                'completed': '✅',
                'failed': '❌'
            };

            if (statusElementId !== 'dualStatus') {
                showStatus(statusElementId,
                    `${statusIcon[status.status] || '🔄'} <strong>${status.status.toUpperCase()}:</strong> ${status.message}`,
                    status.status === 'failed' ? 'error' : (status.status === 'completed' ? 'success' : 'processing')
                );
            }

            if (status.status === 'completed') {
                hideLoadingOverlay();

                // Handle download button for all form types
                if (status.download_url && (formId === 'personalForm' || formId === 'groupZipForm' || formId === 'dualForm')) {
                    // Extract filename from URL
                    const urlParts = status.download_url.split('/');
                    const filename = urlParts[urlParts.length - 1];

                    showDownloadButton(formId, status.download_url, filename);
                }

                // Enable Get Insight button for PDF reports
                if (status.download_url && status.download_url.endsWith('.pdf')) {
                    enableGetInsightButton(formId, status.download_url, statusElementId);
                }

                return;
            } else if (status.status === 'failed') {
                hideLoadingOverlay();
                return;
            }

            attempts++;
            if (attempts < maxAttempts) {
                setTimeout(poll, 5000);
            } else {
                showStatus(statusElementId, '<strong>TIMEOUT:</strong> Task took too long to complete. Please try again.', 'error');
            }
        }
        catch (error) {
            showStatus(statusElementId, `<strong>ERROR:</strong> ${error.message}`, 'error');
        }
    };

    poll();
}

document.getElementById('personalForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById('personalFile');

    if (!fileInput.files[0]) {
        alert('Please select a PDF file');
        return;
    }

    try {
        showStatus('personalStatus', ' <strong>PROCESSING:</strong> Creating personal report...', 'processing');
        showLoadingOverlay({text: "Creating your personal report...", tip: "Hang tight, this may take a moment."});

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        const response = await fetch(`${BASE_URL}/create-personal-report`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            pollTaskStatus(result.task_id, 'personalStatus', 'personalForm');
        } else {
            hideLoadingOverlay();
            showStatus('personalStatus', ` <strong>ERROR:</strong> ${result.detail}`, 'error');
        }
    } catch (error) {
        hideLoadingOverlay();
        showStatus('personalStatus', ` <strong>CONNECTION ERROR:</strong> ${error.message}`, 'error');
    }
});


document.getElementById('dualForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const file1 = document.getElementById('dualFile1').files[0];
    const file2 = document.getElementById('dualFile2').files[0];

    if (!file1 || !file2) {
        alert('Please select both PDF files');
        return;
    }

    try {
        // Make sure the status element exists
        let statusEl = document.getElementById('dualStatus');
        if (!statusEl) {
            const dualTab = document.getElementById('dual');
            const form = dualTab.querySelector('form');
            if (form) {
                statusEl = document.createElement('div');
                statusEl.id = 'dualStatus';
                statusEl.className = 'status';
                form.parentNode.insertBefore(statusEl, form.nextSibling);
            }
        }

        showLoadingOverlay({text: "Creating your dual report...", tip: "Hang tight, this may take a moment."});

        const formData = new FormData();
        formData.append('file1', file1);
        formData.append('file2', file2);

        const response = await fetch(`${BASE_URL}/create-dual-report`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            pollTaskStatus(result.task_id, 'dualStatus', 'dualForm');
        } else {
            showStatus('dualStatus', `<strong>ERROR:</strong> ${result.detail}`, 'error');
        }
    } catch (error) {
        showStatus('dualStatus', `<strong>CONNECTION ERROR:</strong> ${error.message}`, 'error');
    }
});

document.getElementById('translateForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById('translateFile');

    if (!fileInput.files[0]) {
        alert('Please select a PDF file');
        return;
    }

    try {
        showStatus('translateStatus', '<strong>PROCESSING:</strong> Processing translation request...', 'processing');
        showLoadingOverlay({text: "Creating your translated report...", tip: "Hang tight, this may take a moment."});

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        const response = await fetch(`${BASE_URL}/translate`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            pollTaskStatus(result.task_id, 'translateStatus');
        } else {
            showStatus('translateStatus', `<strong>ERROR:</strong> ${result.detail}`, 'error');
        }
    } catch (error) {
        showStatus('translateStatus', `<strong>CONNECTION ERROR:</strong> ${error.message}`, 'error');
    }
});

// Check service health on page load

// Add this function to ensure all modals are hidden on page load
function hideAllModals() {
    const modals = [
        'dualInsightChoiceModal',
        'dualSpecificInsightModal',
        'groupInsightModal'
    ];

    modals.forEach(modalId => {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
        }
    });
}

// Update the window load event listener
window.addEventListener('load', async () => {
    // Hide all modals first
    hideAllModals();

    try {
        const response = await fetch(`${BASE_URL}/health`);
        if (response.ok) {
            console.log('MBTI Processing Service is running and healthy');
        } else {
            console.warn('Service health check failed');
        }
    } catch (error) {
        console.error('Cannot connect to MBTI Processing Service:', error.message);
        // Show a subtle notification instead of alert
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #fef2f2;
            color: #dc2626;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            border-left: 4px solid #ef4444;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            z-index: 1000;
            max-width: 300px;
            font-size: 0.9rem;
        `;
        notification.innerHTML = '<strong>Service Offline:</strong> Make sure the MBTI Processing Service is running on https://desktop-sm21qic.tail63492a.ts.net:3000';
        document.body.appendChild(notification);

        // Auto-remove notification after 10 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 10000);
    }
});


// Add smooth scrolling for better UX
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});


document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded');

    // Hide all modals on DOM load
    hideAllModals();

    // Set up dual insight handlers
    setupDualInsightHandlers();

    // Feature cards setup
    const featureCards = document.querySelectorAll('.feature-card');

    featureCards[0].addEventListener('click', function() {
        showTab('personal');
    });

    featureCards[1].addEventListener('click', function() {
        showTab('dual');
    });

    featureCards[2].addEventListener('click', function() {
        showTab('group');
    });

    featureCards[3].addEventListener('click', function() {
        showTab('translate');
    });

    // Add hover effect to feature cards
    featureCards.forEach(card => {
        card.style.cursor = 'pointer';

        card.addEventListener('mouseover', function() {
            this.style.boxShadow = '0 10px 25px rgba(0,0,0,0.15)';
            this.style.transform = 'translateY(-5px)';
        });

        card.addEventListener('mouseout', function() {
            this.style.boxShadow = '';
            this.style.transform = '';
        });
    });
});

function setupDualInsightHandlers() {
    console.log('Setting up dual insight handlers');

    // Generic insight button
    const genericBtn = document.getElementById('btnDualGenericInsight');
    if (genericBtn) {
        console.log('Found generic button, setting up handler');
        genericBtn.onclick = async function() {
            console.log('Generic insight button clicked');
            closeDualInsightChoiceModal();

            showLoadingOverlay({
                text: "Generating Generic Insight...",
                tip: "Hang tight, this may take up to a minute."
            });

            const form = document.getElementById('dualForm');
            const insightBtn = form ? form.querySelector('button.get-insight-btn') : null;

            if (!insightBtn) {
                console.error('Could not find insight button in dual form');
                hideLoadingOverlay();
                alert('Error: Could not find insight button');
                return;
            }

            const formData = new FormData();
            formData.append('download_url', window.__dualDownloadUrl);

            try {
                const response = await fetch(`${BASE_URL}/insight-by-download-url`, {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();

                if (response.ok) {
                    console.log('Starting insight polling for generic insight');
                    pollInsightStatus(result.task_id, 'dualStatus', 'dualForm', insightBtn);
                } else {
                    hideLoadingOverlay();
                    showStatus('dualStatus', `<strong>ERROR:</strong> ${result.detail}`, 'error');
                    insightBtn.disabled = false;
                    insightBtn.textContent = "Get Insight";
                }
            } catch (error) {
                console.error('Generic insight request error:', error);
                hideLoadingOverlay();
                showStatus('dualStatus', `<strong>CONNECTION ERROR:</strong> ${error.message}`, 'error');
                insightBtn.disabled = false;
                insightBtn.textContent = "Get Insight";
            }
        };
    } else {
        console.warn('Generic insight button not found');
    }

    // Specific insight button
    const specificBtn = document.getElementById('btnDualSpecificInsight');
    if (specificBtn) {
        console.log('Found specific button, setting up handler');
        specificBtn.onclick = function() {
            console.log('Specific insight button clicked');
            closeDualInsightChoiceModal();
            openDualSpecificInsightModal();
        };
    } else {
        console.warn('Specific insight button not found');
    }

    // Relationship type dropdown
    const relationshipTypeSelect = document.getElementById('relationshipType');
    if (relationshipTypeSelect) {
        relationshipTypeSelect.onchange = function() {
            const otherDiv = document.getElementById('relationshipTypeOtherDiv');
            const otherInput = document.getElementById('relationshipTypeOther');

            if (this.value === 'other') {
                otherDiv.style.display = 'block';
                otherInput.required = true;
            } else {
                otherDiv.style.display = 'none';
                otherInput.required = false;
                otherInput.value = '';
            }
        };
    }

    // Specific insight form submission
    const specificForm = document.getElementById('dualSpecificInsightForm');
    if (specificForm) {
        specificForm.onsubmit = async function(e) {
            e.preventDefault();
            console.log('Specific insight form submitted');

            showLoadingOverlay({
                text: "Generating your specific MBTI Insight...",
                tip: "This can take up to a minute."
            });

            const form = document.getElementById('dualForm');
            const insightBtn = form ? form.querySelector('button.get-insight-btn') : null;

            if (!insightBtn) {
                console.error('Could not find insight button in dual form');
                hideLoadingOverlay();
                alert('Error: Could not find insight button');
                return;
            }

            let relationshipType = document.getElementById('relationshipType').value;
            if (relationshipType === 'other') {
                relationshipType = document.getElementById('relationshipTypeOther').value;
            }
            const relationshipGoals = document.getElementById('relationshipGoals').value;
            const downloadUrl = window.__dualDownloadUrl;

            if (!downloadUrl) {
                alert('Missing report file. Please generate the report first.');
                hideLoadingOverlay();
                return;
            }

            const formData = new FormData();
            formData.append('download_url', downloadUrl);
            formData.append('relationship_type', relationshipType);
            formData.append('relationship_goals', relationshipGoals);

            try {
                const response = await fetch(`${BASE_URL}/insight-by-download-url`, {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (response.ok) {
                    console.log('Starting insight polling for specific insight');
                    pollInsightStatus(result.task_id, 'dualStatus', 'dualForm', insightBtn);
                    closeDualSpecificInsightModal();
                } else {
                    hideLoadingOverlay();
                    showStatus('dualStatus', `<strong>ERROR:</strong> ${result.detail}`, 'error');
                }
            } catch (error) {
                console.error('Specific insight request error:', error);
                hideLoadingOverlay();
                showStatus('dualStatus', `<strong>CONNECTION ERROR:</strong> ${error.message}`, 'error');
            }
        };
    }
}
function testDualButtons() {
    console.log('Testing dual insight buttons...');
    console.log('Generic button exists:', !!document.getElementById('btnDualGenericInsight'));
    console.log('Specific button exists:', !!document.getElementById('btnDualSpecificInsight'));
    console.log('Choice modal exists:', !!document.getElementById('dualInsightChoiceModal'));
    console.log('Specific modal exists:', !!document.getElementById('dualSpecificInsightModal'));

    const genericBtn = document.getElementById('btnDualGenericInsight');
    if (genericBtn) {
        console.log('Generic button onclick:', genericBtn.onclick);
    }

    const specificBtn = document.getElementById('btnDualSpecificInsight');
    if (specificBtn) {
        console.log('Specific button onclick:', specificBtn.onclick);
    }
}

// Request insight generation
async function getInsightByDownloadUrl(downloadUrl, statusId, formId, btn) {
    const formData = new FormData();
    formData.append('download_url', downloadUrl);

    try {
        const response = await fetch(`${BASE_URL}/insight-by-download-url`, {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        if (response.ok) {
            pollInsightStatus(result.task_id, statusId, formId, btn);
        } else {
            showStatus(statusId, `ERROR: ${result.detail}`, 'error');
            if (btn) {
                btn.disabled = false;
                btn.textContent = "Get Insight";
            }
        }
    } catch (error) {
        showStatus(statusId, `CONNECTION ERROR: ${error.message}`, 'error');
        if (btn) {
            btn.disabled = false;
            btn.textContent = "Get Insight";
        }
    }
}

function extractBodyContent(html) {
    try {
        // Create a temporary DOM element to parse the HTML
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;

        // Try to find content within body tags first
        const bodyElement = tempDiv.querySelector('body');
        if (bodyElement) {
            return bodyElement.innerHTML;
        }

        // If no body tag, try to find main content areas
        const contentSelectors = [
            '.report-content',
            '.content',
            'main',
            '.main-content'
        ];

        for (const selector of contentSelectors) {
            const element = tempDiv.querySelector(selector);
            if (element) {
                return element.innerHTML;
            }
        }

        // Fallback to the entire content
        return html;
    } catch (error) {
        console.warn('Error extracting body content:', error);
        return html;
    }
}
// Poll for completion and activate "Show Insight"

// Replace the pollInsightStatus function with this fixed version
function pollInsightStatus(taskId, statusId, formId, btn) {
    console.log('pollInsightStatus called with:', { taskId, statusId, formId, btnExists: !!btn });

    const poll = async () => {
        try {
            const response = await fetch(`${BASE_URL}/status/${taskId}`);
            const status = await response.json();

            console.log('Poll status:', status.status);

            // Use the enhanced showStatus function
            showStatus(
                statusId,
                `<strong>${status.status.toUpperCase()}:</strong> ${status.message}`,
                status.status === 'failed' ? 'error' : (status.status === 'completed' ? 'success' : 'processing')
            );

            if (status.status === 'completed') {
                hideLoadingOverlay();
                console.log('Task completed, processing insight...');

                // Save HTML and PDF insight URLs if present
                let insightHtmlUrl = null;
                let insightPdfUrl = null;

                if (status.download_url && status.download_url.endsWith('.html')) {
                    insightHtmlUrl = `${BASE_URL}${status.download_url}`;
                    console.log(`Saved HTML insight URL: ${insightHtmlUrl}`);
                }

                if (status.insight_pdf_url || status.insight_pdf_filename) {
                    insightPdfUrl = status.insight_pdf_url
                        ? `${BASE_URL}${status.insight_pdf_url}`
                        : status.insight_pdf_filename
                        ? `${BASE_URL}/output/${status.insight_pdf_filename}`
                        : null;
                } else if (status.download_url && status.download_url.endsWith('.html')) {
                    insightPdfUrl = `${BASE_URL}/output/${status.download_url.split('/').pop().replace('.html', '.pdf')}`;
                }

                // Save for later use
                lastInsightPdfFilename = insightPdfUrl;

                // For group form, show the insight directly
                if (formId === 'groupZipForm' && insightHtmlUrl) {
                    try {
                        const resp = await fetch(insightHtmlUrl);
                        const html = await resp.text();
                        showInsightInTab('group', html, lastInsightPdfFilename);

                        // Show success message
                        showStatus(statusId, '<strong>SUCCESS:</strong> Group insight generated successfully!', 'success');
                    } catch (error) {
                        console.error('Error loading group insight:', error);
                        showStatus(statusId, '<strong>ERROR:</strong> Could not load insight content.', 'error');
                    }
                } else if (formId === 'dualForm') {
                    // Handle dual form logic (existing code)
                    let targetBtn = btn;
                    if (!targetBtn) {
                        const form = document.getElementById('dualForm');
                        targetBtn = form ? form.querySelector('button.get-insight-btn') : null;
                    }

                    if (targetBtn && insightHtmlUrl) {
                        targetBtn.onclick = null;
                        if (targetBtn._insightHandler) {
                            targetBtn.removeEventListener("click", targetBtn._insightHandler);
                        }

                        setButtonShowInsight(targetBtn);

                        targetBtn._insightHandler = async function showInsightHandler(e) {
                            e.preventDefault();
                            e.stopPropagation();

                            try {
                                const resp = await fetch(insightHtmlUrl);
                                const html = await resp.text();
                                showInsightInTab('dual', html, lastInsightPdfFilename);
                            } catch (error) {
                                console.error('Error loading insight:', error);
                                alert("Could not load insight.");
                            }
                        };

                        targetBtn.addEventListener("click", targetBtn._insightHandler);
                        showStatus(statusId, '<strong>SUCCESS:</strong> Insight ready! Click "Show Insight" to view.', 'success');
                    }
                } else {
                    // Handle other forms normally
                    if (insightHtmlUrl && btn) {
                        setButtonShowInsight(btn);
                        btn.onclick = null;
                        if (btn._insightHandler) {
                            btn.removeEventListener("click", btn._insightHandler);
                        }

                        btn._insightHandler = async function showInsightHandler() {
                            try {
                                const resp = await fetch(insightHtmlUrl);
                                const html = await resp.text();

                                let tabName = null;
                                if (formId === 'personalForm') tabName = 'personal';
                                else if (formId === 'translateForm') tabName = 'translate';

                                showInsightInTab(tabName, html, lastInsightPdfFilename);
                            } catch (e) {
                                alert("Could not load insight.");
                            }
                        };

                        btn.addEventListener("click", btn._insightHandler);
                    }
                }

                return;
            } else if (status.status === 'failed') {
                hideLoadingOverlay();
                console.log('Task failed');
                if (btn) {
                    btn.disabled = false;
                    btn.textContent = "Get Insight";
                    btn.style.background = "linear-gradient(135deg, #dc2626, #a30e0e)";
                }
                return;
            } else {
                // Still processing
                setTimeout(poll, 2000);
            }
        } catch (error) {
            console.error('Poll error:', error);
            hideLoadingOverlay();

            try {
                showStatus(statusId, `<strong>ERROR:</strong> ${error.message}`, 'error');
            } catch (statusError) {
                console.error('Could not show status:', statusError);
            }

            if (btn) {
                btn.disabled = false;
                btn.textContent = "Get Insight";
                btn.style.background = "linear-gradient(135deg, #dc2626, #a30e0e)";
            }
        }
    };
    poll();
}

document.getElementById('groupZipForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    // Reset insight state when starting new group report
    resetGroupInsightState();

    const fileInput = document.getElementById('groupZipFile');

    if (!fileInput.files[0]) {
        alert('Please select a ZIP file');
        return;
    }

    try {
        showStatus('groupStatus', '<strong>PROCESSING:</strong> Uploading and extracting ZIP file...', 'processing');
        showLoadingOverlay({
            text: "Processing group ZIP...",
            tip: "Large teams may take up to a minute."
        });

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        const response = await fetch(`${BASE_URL}/upload-zip-group-report`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            pollTaskStatus(result.task_id, 'groupStatus', 'groupZipForm');
            currentGroupTaskId = result.task_id;
            localStorage.setItem("currentGroupTaskId", currentGroupTaskId);
        } else {
            hideLoadingOverlay();
            showStatus('groupStatus', `<strong>ERROR:</strong> ${result.detail}`, 'error');
        }
    } catch (error) {
        hideLoadingOverlay();
        showStatus('groupStatus', `<strong>CONNECTION ERROR:</strong> ${error.message}`, 'error');
    }
});
function hideAllModals() {
    const modals = [
        'dualInsightChoiceModal',
        'dualSpecificInsightModal',
        'groupInsightModal'
    ];

    console.log('Hiding all modals');

    modals.forEach(modalId => {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
            console.log(`Hidden modal: ${modalId}`);
        }
    });
}

function closeGroupInsightModal() {
    document.getElementById('groupInsightModal').style.display = 'none';
}

function resetFormState(formId) {
    if (formId === 'personalForm') {
        const generateBtn = document.getElementById('personalGenerateBtn');
        const downloadBtn = document.getElementById('personalDownloadBtn');

        if (generateBtn && downloadBtn) {
            generateBtn.style.visibility = 'visible';
            downloadBtn.style.display = 'none';
        }
    } else if (formId === 'groupZipForm') {
        const generateBtn = document.getElementById('groupGenerateBtn');
        const downloadBtn = document.getElementById('groupDownloadBtn');

        if (generateBtn && downloadBtn) {
            generateBtn.style.visibility = 'visible';
            downloadBtn.style.display = 'none';
        }
    } else if (formId === 'dualForm') {
        const generateBtn = document.getElementById('dualGenerateBtn');
        const downloadBtn = document.getElementById('dualDownloadBtn');

        if (generateBtn && downloadBtn) {
            generateBtn.style.visibility = 'visible';
            downloadBtn.style.display = 'none';
        }
    }
}
document.getElementById('groupInsightForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const form = e.target;
    const data = {};

    // Collect all fields with proper validation
    for (const el of form.elements) {
        if (el.name && el.value) {
            data[el.name] = el.value.trim();
        }
    }

    console.log('Form data collected:', data);

    // Restore the task ID if not in memory
    if (!currentGroupTaskId) {
        currentGroupTaskId = localStorage.getItem("currentGroupTaskId");
    }

    if (!currentGroupTaskId) {
        alert("No group report found. Please upload a ZIP and generate the group report first.");
        return;
    }

    data.group_task_id = currentGroupTaskId;
    console.log('Final data being sent:', data);

    // Validate required fields
    const requiredFields = ['group_name', 'industry', 'team_type', 'analysis_goal'];
    const missingFields = requiredFields.filter(field => !data[field]);

    if (missingFields.length > 0) {
        alert(`Please fill in the following required fields: ${missingFields.join(', ')}`);
        return;
    }

    showLoadingOverlay({
        text: "Generating group insight...",
        tip: "This might take up to a minute for large teams."
    });

    try {
        const response = await fetch(`${BASE_URL}/group-insight`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            console.log('Success! Task ID:', result.task_id);

            // Poll for completion and handle insight display
            pollGroupInsightStatus(result.task_id);

            // Close the modal after successful submission
            closeGroupInsightModal();
        } else {
            hideLoadingOverlay();
            console.error('Server error:', result);
            showStatus('groupStatus', `<strong>ERROR:</strong> ${result.detail || 'Unknown server error'}`, 'error');
        }
    } catch (err) {
        hideLoadingOverlay();
        console.error('Network error:', err);
        showStatus('groupStatus', `<strong>CONNECTION ERROR:</strong> ${err.message}`, 'error');
    }
});


// Updated pollGroupInsightStatus to properly integrate with the tab cache system
function pollGroupInsightStatus(taskId) {
    const poll = async () => {
        try {
            const response = await fetch(`${BASE_URL}/status/${taskId}`);
            const status = await response.json();

            console.log('Group insight poll status:', status.status);

            showStatus('groupStatus',
                `<strong>${status.status.toUpperCase()}:</strong> ${status.message}`,
                status.status === 'failed' ? 'error' : (status.status === 'completed' ? 'success' : 'processing')
            );

            if (status.status === 'completed') {
                hideLoadingOverlay();
                console.log('Group insight completed');

                if (status.download_url && status.download_url.endsWith('.html')) {
                    const insightHtmlUrl = `${BASE_URL}${status.download_url}`;
                    console.log(`Group insight HTML URL: ${insightHtmlUrl}`);

                    try {
                        // Fetch and store the insight content
                        const resp = await fetch(insightHtmlUrl);
                        const html = await resp.text();

                        // Extract just the body content to avoid nested HTML structure
                        const bodyContent = extractBodyContent(html);

                        // Store insight data globally AND in tab cache
                        groupInsightData = {
                            html: bodyContent, // Use extracted body content
                            pdfUrl: status.insight_pdf_url ? `${BASE_URL}${status.insight_pdf_url}` : null
                        };

                        // Mark insight as generated
                        groupInsightGenerated = true;

                        // Store in tab cache system
                        tabInsightCache['group'] = bodyContent;
                        tabInsightPdfCache['group'] = groupInsightData.pdfUrl;

                        // Update the Show Insight button text to indicate it's ready
                        updateShowInsightButton();

                        // Show the insight immediately in the group tab
                        showInsightInTab('group', bodyContent, groupInsightData.pdfUrl);

                        showStatus('groupStatus', '<strong>SUCCESS:</strong> Group insight generated! Insight is displayed below.', 'success');
                    } catch (error) {
                        console.error('Error loading group insight:', error);
                        showStatus('groupStatus', '<strong>ERROR:</strong> Could not load insight content.', 'error');
                    }
                } else {
                    showStatus('groupStatus', '<strong>ERROR:</strong> No insight content received.', 'error');
                }

                return;
            } else if (status.status === 'failed') {
                hideLoadingOverlay();
                console.log('Group insight failed');
                return;
            } else {
                // Still processing
                setTimeout(poll, 2000);
            }
        } catch (error) {
            console.error('Group insight poll error:', error);
            hideLoadingOverlay();
            showStatus('groupStatus', `<strong>ERROR:</strong> ${error.message}`, 'error');
        }
    };
    poll();
}

// Updated openGroupInsightModal function with better logic
function openGroupInsightModal() {
    console.log('openGroupInsightModal called');
    console.log('groupInsightGenerated:', groupInsightGenerated);
    console.log('groupInsightData:', groupInsightData);
    console.log('tabInsightCache.group:', tabInsightCache['group']);

    // Check multiple sources for insight data
    const hasGroupInsightData = groupInsightGenerated && groupInsightData;
    const hasTabCacheData = tabInsightCache['group'];

    if (hasGroupInsightData || hasTabCacheData) {
        console.log('Showing existing insight');

        // Use the most recent data available
        let htmlContent, pdfUrl;

        if (hasGroupInsightData) {
            htmlContent = groupInsightData.html;
            pdfUrl = groupInsightData.pdfUrl;
        } else {
            htmlContent = tabInsightCache['group'];
            pdfUrl = tabInsightPdfCache['group'];
        }

        // Show the insight directly in the group tab
        showInsightInTab('group', htmlContent, pdfUrl);

        // Scroll to the insight preview
        setTimeout(() => {
            const previewDiv = document.getElementById('groupInsightPreview');
            if (previewDiv) {
                previewDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }, 100);

        // Update button to show it's been generated
        updateShowInsightButton();

        // Show a status message indicating the insight is displayed
        showStatus('groupStatus', '<strong>SUCCESS:</strong> Group insight is displayed below.', 'success');
    } else {
        console.log('No insight found, showing form modal');
        // If no insight generated yet, show the form modal
        hideAllModals();
        document.getElementById('groupInsightModal').style.display = 'block';
    }
}

// Updated updateShowInsightButton to handle both states better
function updateShowInsightButton() {
    const showInsightBtn = document.querySelector('button[onclick="openGroupInsightModal()"]');
    if (showInsightBtn) {
        if (groupInsightGenerated || tabInsightCache['group']) {
            showInsightBtn.textContent = 'Show Generated Insight';
            showInsightBtn.style.background = 'linear-gradient(135deg, #2563eb, #3b82f6)';
            showInsightBtn.style.color = '#fff';
            console.log('Button updated to show generated insight state');
        } else {
            showInsightBtn.textContent = 'Show Insight';
            showInsightBtn.style.background = '';
            showInsightBtn.style.color = '';
            console.log('Button reset to default state');
        }
    } else {
        console.warn('Show Insight button not found');
    }
}

function resetGroupInsightState() {
    console.log('Resetting group insight state');

    groupInsightGenerated = false;
    groupInsightData = null;

    // Also clear tab cache
    tabInsightCache['group'] = null;
    tabInsightPdfCache['group'] = null;

    // Reset button appearance
    updateShowInsightButton();

    // Clear any displayed insight
    const previewDiv = document.getElementById('groupInsightPreview');
    if (previewDiv) {
        previewDiv.innerHTML = '';
        previewDiv.style.display = 'none';
    }
}
// This is your upload ZIP or create group report fetch:
async function uploadGroupReport(zipFile) {
    const formData = new FormData();
    formData.append("file", zipFile);

    const res = await fetch(`${BASE_URL}/upload-zip-group-report`, {
        method: "POST",
        body: formData
    });
    const result = await res.json();
    if (result.task_id) {
        currentGroupTaskId = result.task_id; // <--- STORE TASK ID!
        // showStatus etc...
    }
}

// Show a universal, beautiful loading overlay
function showLoadingOverlay({ text = "Processing your request...", progress = null, tip = "", showGlyph = false } = {}) {
    // Remove if exists
    hideLoadingOverlay();

    const overlay = document.createElement("div");
    overlay.className = "loading-overlay";
    overlay.id = "loadingOverlay";
    overlay.innerHTML = `
        <div class="loader-content">
        <img src="media/m_loader.png" class="custom-loader-img" alt="M Loader Logo">
            <div class="loader-text">${text}</div>
            <div class="loader-progress-bar" style="display:${progress !== null ? 'block':'none'};">
                <div class="loader-progress-fill" style="width:${progress !== null ? progress+'%' : '40%'};"></div>
            </div>
            <div class="loader-tip">${tip}</div>
        </div>
    `;
    document.body.appendChild(overlay);
}

// Optionally update progress in overlay
function updateLoadingOverlayProgress(percent) {
    const fill = document.querySelector("#loadingOverlay .loader-progress-fill");
    if (fill) {
        fill.style.width = `${percent}%`;
    }
}

// Hide overlay
function hideLoadingOverlay() {
    const overlay = document.getElementById("loadingOverlay");
    if (overlay) overlay.remove();
}

function setButtonLoading(btn, text="Generating Insight...") {
    btn.disabled = true;
    btn.style.background = "#a3a3a3";
    btn.style.color = "#fff";
}

function setButtonShowInsight(btn) {
    if (!btn) {
        console.warn('setButtonShowInsight called with no button');
        return;
    }

    btn.disabled = false;
    btn.textContent = "Show Insight";
    btn.style.background = "linear-gradient(135deg, #2563eb, #3b82f6)";
    btn.style.color = "#fff";
    btn.style.display = "inline-flex";
    btn.style.visibility = "visible";

    console.log('Button set to Show Insight state:', btn.textContent);
}

function showInsightInTab(tabName, htmlContent, pdfUrl=null) {
    console.log(`Showing insight in ${tabName} tab`);

    // Store HTML and PDF for this tab
    tabInsightCache[tabName] = htmlContent;
    tabInsightPdfCache[tabName] = pdfUrl;

    // Hide all other previews first
    document.querySelectorAll('.insight-preview').forEach(div => {
        if (!div.id.startsWith(tabName)) {
            div.innerHTML = '';
            div.style.display = 'none';
        }
    });

    // Show in the relevant div
    const previewDiv = document.getElementById(`${tabName}InsightPreview`);
    if (previewDiv) {
        console.log(`Found preview div for ${tabName}`);

        // Set the content
        previewDiv.innerHTML = htmlContent;

        // Add download button if PDF URL is provided
        if (pdfUrl) {
            const downloadBtn = document.createElement('button');
            downloadBtn.className = 'btn download-btn';
            downloadBtn.innerText = 'Download Insight PDF';
            downloadBtn.style.marginTop = "2rem";
            downloadBtn.onclick = async function () {
                try {
                    const response = await fetch(pdfUrl);
                    if (!response.ok) {
                        throw new Error('Download failed');
                    }

                    // Extract filename from URL or use default
                    const urlParts = pdfUrl.split('/');
                    const filename = urlParts[urlParts.length - 1] || 'insight.pdf';

                    await handleDownloadResponse(response, filename);
                } catch (error) {
                    alert(`Download failed: ${error.message}`);
                }
            };
            previewDiv.appendChild(downloadBtn);
        }

        previewDiv.style.display = 'block';

        // Scroll to the preview after a short delay
        setTimeout(() => {
            previewDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);

        console.log(`Insight displayed in ${tabName} tab`);
    } else {
        console.error(`Preview div not found for ${tabName}: ${tabName}InsightPreview`);
    }
}
function openDualInsightChoiceModal() {
    console.log('Opening dual insight choice modal');
    hideAllModals(); // Hide all first
    document.getElementById('dualInsightChoiceModal').style.display = 'flex';
}

function closeDualInsightChoiceModal() {
    console.log('Closing dual insight choice modal');
    document.getElementById('dualInsightChoiceModal').style.display = 'none';
}
function openDualSpecificInsightModal() {
    console.log('Opening dual specific insight modal');
    hideAllModals(); // Hide all first
    document.getElementById('dualSpecificInsightModal').style.display = 'flex';
}
function closeDualSpecificInsightModal() {
    console.log('Closing dual specific insight modal');
    document.getElementById('dualSpecificInsightModal').style.display = 'none';
    document.getElementById('dualSpecificInsightForm').reset();
    document.getElementById('relationshipTypeOtherDiv').style.display = 'none';
}
setTimeout(testDualButtons, 1000);