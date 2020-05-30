function timeStamp() {
    var today = new Date();

    var ts = today.toDateString() + ' ';
    ts += today.getHours() + ':' + today.getMinutes() + ':';
    ts += today.getSeconds();

    return ts;
};

var el = document.getElementById('date');
el.textContent = timeStamp();