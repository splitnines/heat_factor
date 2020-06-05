function pad0(num) {
    return (num < 10 ? '0' : '') + num
}


function timeStamp() {
    const today = new Date();

    let ts = today.toDateString() + ' ';
    ts += pad0(today.getHours()) + ':' + pad0(today.getMinutes()) + ':';
    ts += pad0(today.getSeconds());

    return ts;
};

const date = document.getElementById('date');

if (date) {
    date.textContent = timeStamp();
}
