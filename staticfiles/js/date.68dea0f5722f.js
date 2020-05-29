onload = "location.reload();"

function retDate() {
    const myDate = new Date();
    return myDate;
};

var el = document.getElementById('date');
el.textContent = retDate();