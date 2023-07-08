const validEmail = (emailVal) => {
    const validEmailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;

    return validEmailRegex.test(emailVal);
}

const login = (e) => {
    const username = document.querySelector('[name="username"]');
    const password = document.querySelector('[name="password"]');
    const formError = document.querySelector('.form-error');

    const loginData = new URLSearchParams();
    loginData.append('username', username.value);
    loginData.append('password', password.value);

    // Validate and get token.
    fetch(`${window.location.href.split('/')[0]}/user/login`, {
        method: "POST",
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: loginData
    })
    .then(async result => {
        if (!result.ok) {
            result.json().then(response => {
                formError.innerText = response.detail;
                username.style.borderColor = "red";
                password.style.borderColor = "red";
            });

            throw new Error("Invalid Username or Password");
        }

        return result.json();
    })
    .then(response => {
        username.style.borderColor = "#ccc";
        password.style.borderColor = "#ccc";
        
        // Save token.
        sessionStorage.setItem("AT", response.token)

        window.location.href = "/";
    })
    .catch((err) => {
        console.error(err);
        formError.innerText = err.message;
        username.style.borderColor = "red";
        password.style.borderColor = "red";
    });
};

const signUp = () => {
    const email = document.querySelector('[name="email"]');
    const username = document.querySelector('[name="username"]');
    const firstName = document.querySelector('[name="first"]');
    const lastName = document.querySelector('[name="last"]');
    const password = document.querySelector('[name="password"]');
    const formError = document.querySelector('.form-error');

    // Verify email is valid.
    if (!validEmail(email.value)) {
        email.style.borderColor = "red";
    }

    email.style.borderColor = "#ccc";

    fetch(`${window.location.href.split('/')[0]}/user/create`, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            email: email.value,
            username: username.value,
            first_name: firstName.value,
            last_name: lastName.value,
            password: password.value
        })
    })
    .then(async result => {
        if (!result.ok) {
            result.json().then(response => {
                if (!response.ok && response.detail.toLowerCase().includes('email')) {
                    formError.innerHTML = response.detail;
                    email.style.borderColor = "red";
                    throw new Error("Invalid Email Address");
                }
        
                if (!response.ok && response.detail.toLowerCase().includes('username')) {
                    formError.innerHTML = response.detail;
                    username.style.borderColor = "red";
                    throw new Error("Invalid Username");
                }
            });
        }

        return result.json();
    })
    .then(response => {
        username.style.borderColor = "#ccc";
        email.style.borderColor = "#ccc";

        // Save token.
        sessionStorage.setItem("AT", response.token)

        window.location.href = "/";
    })
    .catch((err) => {
        console.error(err);
        formError.innerHTML = err.message;
        email.style.borderColor = "red";
        username.style.borderColor = "red";
    });
};