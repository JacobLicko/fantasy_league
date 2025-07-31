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

// Draft and ready up logic
function getCookie(name) {
  const v = `; ${document.cookie}`;
  const parts = v.split(`; ${name}=`);
  return parts.length === 2 ? parts.pop().split(';').shift() : '';
}

;(function() {
  const startBtn     = document.getElementById('beginDraftBtn');
  const leagueCode   = startBtn.dataset.leagueCode;
  const currentUser  = startBtn.dataset.currentUser;
  let countdownInt   = null;
  let sessionExpires = null;

  function resetUI() {
    clearInterval(countdownInt);
    countdownInt   = null;
    sessionExpires = null;
    startBtn.textContent = 'Begin Draft';
    startBtn.classList.remove('gold');
    document.querySelectorAll('.slot.ready')
            .forEach(el => el.classList.remove('ready'));
  }

  // Poll the server for session status
  function pollStatus() {
    fetch(`/league/${leagueCode}/draft_status/`)
      .then(r => r.json())
      .then(data => {
        if (!data.active) {
          // no session or expired → reset
          resetUI();
          return;
        }

        // highlight ready slots
        document.querySelectorAll('.slot').forEach(el => {
          const user = el.dataset.username;
          el.classList.toggle('ready', data.ready.includes(user));
        });

        // only ready users get the gold button
        console.log(`   -> amIReady? ${data.ready.includes(currentUser)}`);
        if (data.ready.includes(currentUser)) {
          console.log('   -> adding .gold to button');
          startBtn.classList.add('gold');
        } else {
          console.log('   -> removing .gold from button');
          startBtn.classList.remove('gold');
        }

        // start shared countdown once, based on the first click
        if (!sessionExpires) {
          sessionExpires = new Date(data.expires_at);
          countdownInt = setInterval(() => {
            const sec = Math.floor((sessionExpires - Date.now())/1000);
            startBtn.textContent = sec > 0
              ? `Begin Draft (${sec}s)`
              : 'Begin Draft';
          }, 500);
        }

        // when everyone is ready, navigate off
        if (data.all_ready) {
          window.location = `/league/${leagueCode}/draft/`;
        }
      })
      .catch(console.error);
  }

  // kick off polling for everyone
  pollStatus();
  setInterval(pollStatus, 3000);

  // clicking “Begin Draft” only marks *you* ready and (re)starts session
  startBtn.addEventListener('click', () => {
    fetch(`/league/${leagueCode}/start_draft/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCookie('csrftoken') }
    })
    .then(r => {
      if (!r.ok) throw new Error('too early or bad');
      return r.json();
    })
    .then(_data => {
      // no extra UI here – pollStatus() will pick up the new session
      // and handle both the shared timer and your gold button
      pollStatus();
    })
    .catch(err => console.warn(err));
  });
})();