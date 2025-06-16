document.addEventListener('DOMContentLoaded', () => {
  const loginBtn   = document.getElementById('loginBtn');
  const signupBtn  = document.getElementById('signupBtn');
  const loginForm  = document.getElementById('loginForm');
  const signupForm = document.getElementById('signupForm');

  loginBtn.addEventListener('click', () => {
    loginForm.classList.add('active');
    signupForm.classList.remove('active');
  });
  signupBtn.addEventListener('click', () => {
    signupForm.classList.add('active');
    loginForm.classList.remove('active');
  });
});
