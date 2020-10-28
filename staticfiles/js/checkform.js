$(() => {
    function displaySpinner() {
        // rewrite in vanilla js
        $(spinner).addClass('loading');
    }

    function removeSpinner() {
        // rewrite in vanilla js
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
    const psBadUrlMsg = `Bad URL, please enter a valid Practiscore.com
                         match URL.`;
    const psRegEx = new RegExp(regExStr, 'g');

    $('#heatfactor').click((e) => {
        if (!psRegEx.test($('#id_p_url')[0].value)) {
            e.preventDefault();
            $('#checkform').fadeIn(1000).delay(1000)
            .html(psBadUrlMsg)
            .css('display', 'inline-block');
        } else {
            displaySpinner();
        }
    });

    $('#id_p_url').focus(() => {
        $('[name=myForm]').trigger('reset');
        $('#checkform').fadeOut(1000);
        $('checkform').toggleClass('fade');
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
        const url = $(this).attr('action');
        const formData = $(this).serialize();
        const errorHtml = '<font color="red">Sorry, an error occured.</font>'

        $.ajax({
            type: 'POST',
            url: url,
            data: formData,
            dataType: 'json',
            beforeSend: () => {
                $('#responseHTML').slideUp(600).empty().removeClass('resp');
                displaySpinner();
            },
            complete: () => {
                removeSpinner();
            },
            success: (resp) => {
                $('#responseHTML').addClass('resp')
                .html(resp.response_text)
                .hide().slideDown(600);
            },
            error: () => {
                $('#responseHTML')
                .addClass('resp').html(errorHtml).hide().slideDown(600);
            },
        });
    });

    // reset form data on focus
    $('#id_mem_num_1').focus(() => {
        $('#classificationCalc').trigger('reset');
    });

    // // embed most recent youtube video from my channel
    const youtubeChannelId = "UC_QPi6_8WRZ1bXgShJAzSbg";
    const youtubeChannelUrl = "https://www.youtube.com/feeds/videos.xml?channel_id=";
    const rss2jsonUrl = "https://api.rss2json.com/v1/api.json?rss_url=";
    const embeddedUrl = rss2jsonUrl + encodeURIComponent(
        youtubeChannelUrl + youtubeChannelId
    );

    $.getJSON(embeddedUrl, function(data) {
        const link = data.items[0].link;
        const id = link.substr(link.indexOf("=")+1);
        const youtubeSrc = `https://youtube.com/embed/${id}?controls=0&showinfo=0&rel=0`
        $("#youtubeVideo").attr("src", youtubeSrc);
    });

    // sample image animation
    $('#pointsImg').click(() => {
        $('#pointsMyModal').css('display', 'block');
        $('#img01').attr('src', $('#pointsImg').attr('src'))
        $('#pointsCaption').html($('#pointsImg').attr('alt'));
        $('.modal-content-1').css('width', '90%');
    });

    $('.pointsClose').click(() => {
        $('#pointsMyModal').css('display', 'none');
        $('.modal-content-1').css('width', '60%');
    });

    $('#ppsImg').click(() => {
        $('#ppsMyModal').css('display', 'block');
        $('#img02').attr('src', $('#ppsImg').attr('src'))
        $('#ppsCaption').html($('#ppsImg').attr('alt'));
        $('.modal-content-2').css('width', '90%');
    });

    $('.ppsClose').click(() => {
        $('#ppsMyModal').css('display', 'none');
        $('.modal-content-2').css('width', '60%');
    });
});