
function checkform() {

    const p_url = document.getElementById('id_p_url');
    const ps_url_re = new RegExp(
        '^https://(www\.)?practiscore\.com/results/new/[0-9a-z-]+$', 'g'
    );

	if (!ps_url_re.test(p_url.value)) {
        alert('Bad URL, please enter a valid Practiscore.com match URL.');
		return false;
    }
	return true;
}