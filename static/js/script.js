document.querySelectorAll(".flash").forEach((message) => {
    window.setTimeout(() => {
        message.style.opacity = "0";
        message.style.transform = "translateY(-8px)";
        window.setTimeout(() => message.remove(), 250);
    }, 4500);
});

const password = document.querySelector('input[name="password"]');
const confirmation = document.querySelector('input[name="confirm_password"]');

if (password && confirmation) {
    const validatePasswords = () => {
        confirmation.setCustomValidity(
            password.value === confirmation.value ? "" : "Passwords do not match"
        );
    };
    password.addEventListener("input", validatePasswords);
    confirmation.addEventListener("input", validatePasswords);
}
