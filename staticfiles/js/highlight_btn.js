onload = "location.reload();"
window.onload = function () {
    const elms = document.querySelectorAll('.btn');

    for (let i = 0; i < elms.length; i++) {
        elms[i].onmouseover = function () {
            this.style.backgroundColor = "rgba(173, 216, 230, 1.0)";
        };

        elms[i].onmouseout = function () {
            this.style.backgroundColor = "rgba(173, 216, 230, 0.4)";
        };
    }
};
