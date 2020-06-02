const form_input = document.myForm.field.value;

function checkform()
{
    const ps_url_re = new RegExp(
        '^https://(www\.)?practiscore\.com/results/new/[0-9a-z-]+$', 'g'
    );

	if (!ps_url_re.test(form_input)) {
		// something is wrong
		alert('Bad URL, please enter a valid Practiscore.com match URL.');
		return false;
	}

	return true;
}