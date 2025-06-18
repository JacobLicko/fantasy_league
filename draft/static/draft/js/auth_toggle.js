document.addEventListener('DOMContentLoaded', () => {
  // —— Toggle logic (landing/signup view) ——
  const loginBtn   = document.getElementById('loginBtn');
  const signupBtn  = document.getElementById('signupBtn');
  const loginForm  = document.getElementById('loginForm');
  const signupForm = document.getElementById('signupForm');

  if (loginBtn && signupBtn && loginForm && signupForm) {
    loginBtn.addEventListener('click', () => {
      loginForm.classList.add('active');
      signupForm.classList.remove('active');
    });
    signupBtn.addEventListener('click', () => {
      signupForm.classList.add('active');
      loginForm.classList.remove('active');
    });
  }

  // —— Live validation (signup only) ——
  const signupFormEl = document.getElementById('signupForm');
  if (signupFormEl) {
    const emailInput    = signupFormEl.querySelector('input[name="email"]');
    const emailConfirm  = signupFormEl.querySelector('input[name="email_confirm"]');
    const pwInput       = signupFormEl.querySelector('input[name="password1"]');
    const pwConfirm     = signupFormEl.querySelector('input[name="password2"]');
    const signupSubmit  = document.getElementById('signupSubmit');

    if (emailInput && emailConfirm && pwInput && pwConfirm && signupSubmit) {
      // Insert error elements
      const emailErr    = document.createElement('div');
      emailErr.className   = 'error';
      emailErr.textContent = 'Emails must match and be valid';
      emailErr.style.display = 'none';
      signupSubmit.parentNode.insertBefore(emailErr, signupSubmit);

      const reqErr      = document.createElement('div');
      reqErr.className   = 'error';
      reqErr.textContent = 'Password does not meet minimum requirements';
      reqErr.style.display = 'none';
      signupSubmit.parentNode.insertBefore(reqErr, signupSubmit);

      const matchErr    = document.createElement('div');
      matchErr.className   = 'error';
      matchErr.textContent = 'Passwords do not match';
      matchErr.style.display = 'none';
      signupSubmit.parentNode.insertBefore(matchErr, signupSubmit);

      // Validation regexes
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      const pwRegex    = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W).{8,}$/;

      function validateAll() {
        // 1) Email valid & match?
        const emailVal     = emailInput.value.trim();
        const emailsMatch  = emailVal === emailConfirm.value.trim();
        const emailIsValid = emailRegex.test(emailVal);
        if (!emailIsValid || !emailsMatch) {
          emailErr.style.display   = 'block';
          signupSubmit.disabled    = true;
          reqErr.style.display     = 'none';
          matchErr.style.display   = 'none';
          return;
        }
        emailErr.style.display = 'none';

        // 2) Password meets requirements?
        const pwVal    = pwInput.value;
        const meetsReq = pwRegex.test(pwVal);
        if (!meetsReq) {
          reqErr.style.display     = 'block';
          signupSubmit.disabled    = true;
          matchErr.style.display   = 'none';
          return;
        }
        reqErr.style.display = 'none';

        // 3) Passwords match?
        const match = pwVal === pwConfirm.value;
        matchErr.style.display = match ? 'none' : 'block';
        signupSubmit.disabled  = !match;
      }

      // Wire up inputs
      [emailInput, emailConfirm, pwInput, pwConfirm]
        .forEach(el => el.addEventListener('input', validateAll));

      // Initial validation
      validateAll();
    }
  }
});
