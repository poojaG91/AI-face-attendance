function registerFace() {
    let name = document.getElementById("name").value;

    fetch("/register", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({name: name})
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("msg").innerText = data.msg;
    });
}

function markAttendance() {
    fetch("/attendance", {
        method: "POST"
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("msg").innerText = data.msg;
    });
}
