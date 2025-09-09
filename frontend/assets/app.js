document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const errorMessageDiv = document.getElementById('error-message');

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            errorMessageDiv.textContent = ''; // Clear previous errors

            const email = loginForm.email.value;
            const password = loginForm.password.value;

            // The backend expects form data for the token endpoint
            const formData = new URLSearchParams();
            formData.append('username', email);
            formData.append('password', password);

            try {
                const response = await fetch('/api/v1/auth/token', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                });

                const data = await response.json();

                if (!response.ok) {
                    // Use the error detail from the backend if available
                    const message = data.detail || 'An unknown error occurred.';
                    throw new Error(message);
                }

                // Store tokens and redirect on success
                if (data.access_token) {
                    localStorage.setItem('access_token', data.access_token);
                    localStorage.setItem('refresh_token', data.refresh_token);
                    window.location.href = '/dashboard.html';
                }

            } catch (error) {
                errorMessageDiv.textContent = error.message;
            }
        });
    }

    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const errorMessageDiv = document.getElementById('error-message');
            const successMessageDiv = document.getElementById('success-message');
            errorMessageDiv.textContent = '';
            successMessageDiv.textContent = '';

            const email = registerForm.email.value;
            const password = registerForm.password.value;

            try {
                const response = await fetch('/api/v1/auth/register', {
                    method: 'POST',
                    body: JSON.stringify({ email, password }),
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

                const data = await response.json();

                if (!response.ok) {
                    const message = data.detail || 'An unknown error occurred.';
                    throw new Error(message);
                }

                successMessageDiv.textContent = 'Registration successful! You can now sign in.';
                registerForm.reset();

            } catch (error) {
                errorMessageDiv.textContent = error.message;
            }
        });
    }
});
