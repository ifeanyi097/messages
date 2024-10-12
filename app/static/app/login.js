document.getElementById("loginForm").addEventListener("submit", function(event){
    event.preventDefault();

    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;
    let errorMessage = document.getElementById("error-message");

    if(username === "" || password === "") {
        errorMessage.textContent = "Username and password are required!";
    } else if(password.length < 6) {
        errorMessage.textContent = "Password must be at least 6 characters!";
    } else {
        errorMessage.textContent = "";
        loginUser(username,password);
        // Here you can handle form submission, like sending data to the server
    }
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrfToken = getCookie('csrftoken');

function loginUser(name, password){
    fetch(`/chat/login/`, {
        method:"POST",
        headers:{
            "Content-Type":"application/json",
            "X-CSRFToken":csrfToken
        },
        body: JSON.stringify({username:name, password:password})
    })
    .then(response => {
        if(!response.ok){
            alert("error")
        }
        return response.json;
    })
    .then(data => {
        if(data.status === "ok"){
            window.location.href = data.url;
        }
    })
}

