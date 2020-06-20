function checkForm(e, inputId, formId, regEx, msgText) {
    if (!regEx.test(e[0].value)) {
        $('#'+formId).attr('disabled', true);
        $('#'+inputId).fadeIn(5000).text(msgText);
    }
}

function enableSubmit(divId, inputId, formName) {
    $('#'+inputId).attr('disabled', false);
    $('[name='+formName+']').trigger('reset');
    $('#'+divId).html('<br />');
}

function displaySpinner() {
    let $spinner = $('#spinner').html();
    $(spinner).append('<br />');
    $(spinner).addClass('loading');
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

const $heatFactor = $('#id_p_url')

$heatFactor.blur(function() {
    checkForm($heatFactor, 'checkform', 'heatfactor', psRegEx, psBadUrlMsg);
});

$heatFactor.focus(function() {
    enableSubmit('checkform', 'heatfactor', 'myForm');
});

// adds spinner to page while waiting for scores to load
$('#points').submit(displaySpinner)
// adds spinner to page while waiting for pps to load
$('#pps').submit(displaySpinner);

// replace backend generated date with frontend generated date
$('#date').text(timeStamp());
