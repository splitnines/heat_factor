function timeStamp() {
    const today = new Date();

    let ts = today.toDateString() + ' ';
    ts += today.getHours() + ':' + today.getMinutes() + ':';
    ts += today.getSeconds();

    return ts;
};

const el = document.getElementById('date');

if (el) {
    el.textContent = timeStamp();
}
