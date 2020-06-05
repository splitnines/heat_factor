
function checkForm() {

    let msg = document.getElementById('checkform');

    const ps_url_re = new RegExp(
        '^https://(www\.)?practiscore\.com/results/new/[0-9a-z-]+$', 'g'
    );

    // const my_form = document.forms["myForm"];

    if (!ps_url_re.test(this.value)) {

        document.getElementById('heatfactor').disabled = true;
        msg.textContent = 'Bad URL, please enter a valid Practiscore.com match URL.';
        // my_form.reset();

    }


    return false;
}


function enableSubmit() {

    let msg = document.getElementById('checkform');
    document.getElementById('heatfactor').disabled = false;
    msg.innerHTML = '<br />'
}


// function displayMessage() {

//     let msg = document.getElementById('message');
//     msg.textContent = 'The image takes a few seconds to load.'
// }

const heatFactor = document.getElementById('id_p_url');
if (heatFactor) {
    heatFactor.addEventListener('blur', checkForm, false);
}
if (heatFactor) {
    heatFactor.addEventListener('focus', enableSubmit, false);
}

// const points = document.getElementById('points');
// if (points) {
//     points.addEventListener('submit', displayMessage, false);
// }
