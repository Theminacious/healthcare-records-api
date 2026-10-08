const API_URL = "http://127.0.0.1:8000/api";
const form = document.getElementById("reg-form");
const statusBar = document.getElementById("status-bar");
const result = document.getElementById("result");
const submitButton = document.getElementById("submit-btn");

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    submitButton.disabled = true;
    statusBar.textContent = "Creating your account...";
    result.classList.add("hidden");

    const payload = {
        name: document.getElementById("name").value.trim(),
        email: document.getElementById("email").value.trim(),
        password: document.getElementById("password").value,
    };

    try {
        const response = await fetch(`${API_URL}/auth/register/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(Object.values(data).flat().join(" ") || "Registration failed.");
        }
        statusBar.textContent = "Registration complete.";
        result.textContent = "Account created. You can now sign in through the API login endpoint.";
        result.classList.remove("hidden");
        form.reset();
    } catch (error) {
        statusBar.textContent = "Registration failed.";
        result.textContent = error.message.includes("Failed to fetch")
            ? "Could not reach Django. Start the API with: USE_SQLITE=true python manage.py runserver"
            : error.message;
        result.classList.remove("hidden");
    } finally {
        submitButton.disabled = false;
    }
});