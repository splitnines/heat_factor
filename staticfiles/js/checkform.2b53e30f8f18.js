
function checkform() {

    const p_url = document.getElementByName('myForm');
    const ps_url_re = new RegExp(
        '^https://(www\.)?practiscore\.com/results/new/[0-9a-z-]+$', 'g'
    );

	if (ps_url_re.test(p_url)) {
        console.log(p_url);
		alert('Bad URL, please enter a valid Practiscore.com match URL.');
		return false;
    }
    console.log(p_url);
	return false;
}