function checkForm(e, inputId, formId, regEx, msgText) {

    if (!regEx.test(e.value)) {

        document.getElementById(formId).disabled = true;
        document.getElementById(inputId).textContent = msgText;

    }
}


function enableSubmit(divId, inputId, formName) {

    document.getElementById(inputId).disabled = false;
    document.forms[formName].reset();
    document.getElementById(divId).innerHTML = '<br />';

}


function displaySpinner() {

    let spinner = document.getElementById('spinner');
    spinner.innerHTML = '<br />';
    spinner.setAttribute('class', 'loading');

}


function padZero(num) {

    return (num < 10 ? '0' : '') + num

}


function timeStamp() {

    const today = new Date();

    let ts = today.toDateString() + ' ';
    ts += padZero(today.getHours()) + ':';
    ts += padZero(today.getMinutes()) + ':';
    ts += padZero(today.getSeconds());

    return ts;

}


// form validation and button manipulation based on URL input
const regExStr = '^https://(www\.)?practiscore\.com/results/new/[0-9a-z-]+$'
const psBadUrlMsg = 'Bad URL, please enter a valid Practiscore.com match URL.';
const psRegEx = new RegExp(regExStr, 'g');

if (document.getElementById('id_p_url')) {

    const heatFactor = document.getElementById('id_p_url');

    heatFactor.addEventListener('blur', function() {
        checkForm(
            heatFactor, 'checkform', 'heatfactor', psRegEx, psBadUrlMsg
        );
    }, false);

    heatFactor.addEventListener('focus', function() {
        enableSubmit('checkform', 'heatfactor', 'myForm');
    }, false);
}

// adds spinner to page while waiting for scores to load
if (document.getElementById('points')) {

    const points = document.getElementById('points');
    points.addEventListener('submit', displaySpinner, false);
}

if (document.getElementById('pps')) {

    const pps = document.getElementById('pps');
    pps.addEventListener('submit', displaySpinner, false);
}


// replace backend generated date with frontend generated date
// if (document.getElementById('date')) {

//     document.getElementById('date').textContent = timeStamp();
// }

$(document).ready(function() {
    $('#date').text(timeStamp());
});