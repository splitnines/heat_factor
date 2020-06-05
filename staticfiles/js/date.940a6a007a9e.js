function pad0(num) {
    return (num < 10 ? '0' : '') + num
}


function timeStamp() {
    const today = new Date();

    let ts = today.toDateString() + ' ';
    ts += today.getHours() + ':' + pad0(today.getMinutes()) + ':';
    ts += pad0(today.getSeconds());

    return ts;
};

const el = document.getElementById('date');

if (el) {
    el.textContent = timeStamp();
}
