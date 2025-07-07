console.log("🏷️ league_detail.js loaded");

const btn = document.getElementById('beginDraftBtn');
const dt  = btn.dataset.draftDatetime; // e.g. "2025-07-01T15:30"
const draftDate = new Date(dt);

function updateButton() {
if (new Date() >= draftDate) {
    btn.disabled = false;
    btn.classList.add('enabled');
} else {
    btn.disabled = true;
    btn.classList.remove('enabled');
}
}

updateButton();
setInterval(updateButton, 60000); // re-check every minute

// edit league toggle
const editBtn = document.getElementById('editLeagueBtn');
const editPanel = document.getElementById('editLeagueContainer');
console.log("⚙️ editBtn, editPanel:", editBtn, editPanel);
if (editBtn && editPanel) {
editBtn.addEventListener('click', () => {
    console.log("✏️ Edit button clicked");
    editPanel.classList.toggle('active');
});
}

// Delete‐confirmation modal
const deleteTrigger = document.getElementById('deleteLeagueTrigger');
const deleteModal   = document.getElementById('deleteModal');
const cancelDelete  = document.getElementById('cancelDelete');

if (deleteTrigger && deleteModal && cancelDelete) {
deleteTrigger.addEventListener('click', e => {
    e.preventDefault();              // prevent form submit
    deleteModal.classList.add('active');
});
cancelDelete.addEventListener('click', () => {
    deleteModal.classList.remove('active');
});
}