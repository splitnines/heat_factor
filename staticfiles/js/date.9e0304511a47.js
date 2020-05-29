onload = "location.reload();"

function retDate() {
    const myDate = new Date();
    return myDate;
};

function timeStamp() {
    const today = new Date();

    let ts = today.toDateString() + ' ';
    ts += today.getHours() + ':' + today.getMinutes() + ':';
    ts += today.getSeconds();

    return ts;
};

var el = document.getElementById('date');
el.textContent = timeStamp();