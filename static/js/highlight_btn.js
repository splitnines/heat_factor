window.onload = function () {
    var elms = document.getElementsByTagName('input');

    // search for element with class "btn"
    for (var i = 0; i < elms.length; i++) {

        if (elms[i].getAttribute('class') === 'btn') {

            elms[i].onmouseover = function () {
                this.style.backgroundColor = '#ededed';
            }

            elms[i].onmouseout = function () {
                this.style.backgroundColor = '#cfcfcf';
            }
        }
    }
}