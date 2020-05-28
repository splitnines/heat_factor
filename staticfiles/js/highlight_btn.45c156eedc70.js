onload="location.reload();"
window.onload = function () {
    // for heat_factor I need to use "input"
    var elms = document.getElementsByTagName("input");

    // search for element with class "colorbtn"
    for (var i = 0; i < elms.length; i++) {
        if (elms[i].getAttribute("class") === "btn") {
            elms[i].onmouseover = function () {
                this.style.backgroundColor = "rgba(0, 0, 0, 0.9)";
            };

            elms[i].onmouseout = function () {
                this.style.backgroundColor = "rgba(0, 0, 0, 0.2)";
            };
        }
    }
};
