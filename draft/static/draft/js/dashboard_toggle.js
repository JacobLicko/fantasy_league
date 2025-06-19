document.addEventListener('DOMContentLoaded', () => {
  const showBtn    = document.getElementById('showLeaguesBtn');
  const joinBtn    = document.getElementById('joinLeagueBtn');
  const createBtn  = document.getElementById('createLeagueBtn');

  const listCont   = document.getElementById('myLeaguesContainer');
  const joinCont   = document.getElementById('joinLeagueContainer');
  const createCont = document.getElementById('createLeagueContainer');

  function hideAll() {
    listCont.classList.remove('active');
    joinCont.classList.remove('active');
    createCont.classList.remove('active');
  }

  showBtn.addEventListener('click', () => {
    hideAll();
    listCont.classList.add('active');
  });

  joinBtn.addEventListener('click', () => {
    hideAll();
    joinCont.classList.add('active');
  });

  createBtn.addEventListener('click', () => {
    hideAll();
    createCont.classList.add('active');
  });
});
