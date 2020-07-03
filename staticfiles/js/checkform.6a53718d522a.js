$(function() {

    function displaySpinner() {
        $(spinner).addClass('loading');
    }

    function removeSpinner() {
        $(spinner).removeClass('loading');
    }

    function padZero(num) {
        return (num < 10 ? '0' : '') + num
    }

    function timeStamp() {
        var today = new Date();

        var ts = today.toDateString() + ' ';
        ts += padZero(today.getHours()) + ':';
        ts += padZero(today.getMinutes()) + ':';
        ts += padZero(today.getSeconds());

        return ts;
    }

    // form validation and button manipulation based on URL input
    var regExStr = '^https://(www\.)?practiscore\.com/results/new/[0-9a-z-]+$'
    var psBadUrlMsg = 'Bad URL, please enter a valid Practiscore.com match URL.';
    var psRegEx = new RegExp(regExStr, 'g');

    $('#heatfactor').click(function(e) {
        if (!psRegEx.test($('#id_p_url')[0].value)) {
            e.preventDefault();
            $('#checkform').fadeIn(1000).delay(1000)
            .html(psBadUrlMsg)
            .css('display', 'inline-block');
        } else {
            displaySpinner();
        }
    });

    $('#id_p_url').focus(function() {
        $('[name=myForm]').trigger('reset');
        $('#checkform').fadeOut(1500);
    });

    // adds spinner to page while waiting for scores to load
    $('#points').submit(() => {
        displaySpinner()
    });

    // adds spinner to page while waiting for pps to load
    $('#pps').submit(() => {
        displaySpinner()
    });

    // replace backend generated date with frontend generated date
    $('#date').text(timeStamp());

    // display results of get_upped app on current page
    $('#classificationCalc').submit(function(e) {
        e.preventDefault();
        var url = $(this).attr('action');
        var formData = $(this).serialize();

        $.ajax({
            type: 'POST',
            url: url,
            data: formData,
            beforeSend: () => {
                $('#responseHTML').empty().removeClass('resp');
                displaySpinner();
            },
            complete: () => {
                removeSpinner();
            },
            success: (resp) => {
                $('#responseHTML')
                .addClass('resp')
                .html($(resp)[15].innerHTML)
                .hide()
                .fadeIn(1000);
            },
            error: () => {
                $('#responseHTML')
                .addClass('resp')
                .html('<font color="red">Sorry, an error occured.</font')
                .hide()
                .fadeIn(1000);
            },
        });
    });

    // reset form data on focus
    $('#id_mem_num_1').focus(() => {
        $('#classificationCalc').trigger('reset');
    });

});
