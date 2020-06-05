
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
    document.getElementById('heatfactor').disabled = false;
}

const heatFactor = document.getElementById('id_p_url');

if (heatFactor) {
    heatFactor.addEventListener('blur', checkForm, false);
}

if (heatFactor) {
    heatFactor.addEventListener('focus', enableSubmit, false);
}
