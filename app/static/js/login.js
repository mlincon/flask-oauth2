const signupForm = document.getElementById('signup-form');
signupForm.addEventListener('submit', handleSignupFormSubmit);


function handleSignupFormSubmit(event) {
    event.preventDefault();

    const formDataEntries = new FormData(signupForm).entries();
    const { email, password } = Object.fromEntries(formDataEntries);

    alert("You are: " + email + ", " + password + "\nThis is a dummy success message.");
}
