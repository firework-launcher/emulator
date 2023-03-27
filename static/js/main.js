const socket = io();

status_table = document.getElementById("status");

for (let i = 1; i < 33; i++) {
    row = document.createElement("tr");
    pin_element = document.createElement("td");
    state_element = document.createElement("td");
    launched_element = document.createElement("td");
    state_element.setAttribute("id", i+"_state");
    launched_element.setAttribute("id", i+"_launched");
    launched_element.setAttribute("style", "color: #ff0000;")
    pin_element.innerText = i;
    state_element.innerText = "1";
    launched_element.innerText = "No";
    row.appendChild(pin_element);
    row.appendChild(state_element);
    row.appendChild(launched_element);
    status_table.appendChild(row);
}

socket.on("pin_update", (data) => {
    console.log(data)
    state_element = document.getElementById(data["pin"]+"_state");
    state_element.innerText = data["state"];
    if (data["state"] == "0") {
        launched_element = document.getElementById(data["pin"]+"_launched");
        launched_element.innerText = "Yes";
        launched_element.setAttribute("style", "color: #00ff00;")
    }
});
