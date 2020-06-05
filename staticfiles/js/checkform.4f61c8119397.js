
// function checkForm() {

//     // const my_form = document.forms["myForm"];
//     const p_url = document.getElementById('id_p_url');

//     const ps_url_re = new RegExp(
//         '^https://(www\.)?practiscore\.com/results/new/[0-9a-z-]+$', 'g'
//     );

// 	if (!ps_url_re.test(p_url.value)) {
//         alert('Bad URL, please enter a valid Practiscore.com match URL.');
//         // my_form.reset();
// 		return false;
//     }
// 	return true;
// }


function checkForm() {
    let msg = document.getElementById('checkform');
    if (!ps_url_re.test(this.value)) {
        msg.textContent = 'Bad URL, please enter a valid Practiscore.com match URL.';
    } else {
        msg.textContent = '';
    }
}

const heatFactor = document.getElementById('heatfactor');
heatFactor.addEventListener('blur', checkForm, false);