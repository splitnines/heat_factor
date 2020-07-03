$(function() {

    function displaySpinner() {
        let $spinner = $('#spinner').html();
        // $(spinner).append('<br />');
        $(spinner).addClass('loading');
    }

    function removeSpinner() {
        let $spinner = $('#spinner').html();
        $(spinner).removeClass('loading');
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

    const $heatFactorBtn = $('#heatfactor')
    const $heatFactorInput = $('#id_p_url')

    $heatFactorBtn.on('click', function() {
        if (!psRegEx.test($heatFactorInput[0].value)) {
            $('#heatfactor').attr('disabled', true);
            $('#checkform').fadeIn(1000).delay(1000)
            .html(psBadUrlMsg)
            .css('display', 'inline-block');
        }
    });

    $heatFactorInput.on('focus', function() {
        $('#heatfactor').attr('disabled', false);
        $('[name=myForm]').trigger('reset');
        $('#checkform').fadeOut(1500);
    });

    // adds spinner to page while waiting for scores to load
    $('#points').submit(displaySpinner)

    // adds spinner to page while waiting for pps to load
    $('#pps').submit(displaySpinner);

    // replace backend generated date with frontend generated date
    $('#date').text(timeStamp());

    $('#classificationCalc').submit(function(e) {
        e.preventDefault();
        var url = $(this).attr('action');
        var formData = $(this).serialize();

        $.ajax({
            type: 'POST',
            url: url,
            data: formData,
            beforeSend: function() {
                $('#responseHTML').empty().removeClass('resp');
                displaySpinner();
            },
            complete: function() {
                removeSpinner();
            },
            success: function(resp) {
                $('#responseHTML')
                .addClass('resp')
                .html($(resp)[15].innerHTML)
                .hide()
                .fadeIn(1000);
            },
            error: function() {
                $('#responseHTML')
                .addClass('resp')
                .html('<font color="red">An error occured.</font')
                .hide()
                .fadeIn(1000);
            },
        });
    });

    $('#id_mem_num_1').focus(function() {
        $('#classificationCalc').trigger('reset');
    });

});
