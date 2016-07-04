$(function() {
    $(document).on('triggerAjaxyReady', '.survey-trigger-ajaxy-ready', function() {
        var toggle_class = 'fa-check';
        var sib_selector = '.' + $(this).attr('class').split(' ')[0];
        $(this).find('i').addClass(toggle_class);
        $(this).siblings(sib_selector).find('i').removeClass(toggle_class);
    });

    $(".survey-submit").on('click', function() {
        var top = $(this).parents('.survey-wrap').siblings('.survey-anchor').offset().top
        $("html, body").animate({scrollTop: top});
    });

    $('#create-survey-btn').on('triggerAjaxyReady', function() {
        $('#surveys').trigger('ajaxy-reload');
    });

    var new_survey_name_cached = null;
    $('#surveys').on('ajaxy-refreshed', function(e) {
        e.stopPropagation();
        if ($('.close-survey-modal').length) {
            $('.close-survey-modal').trigger('click');
        }
        var new_survey = $('#surveys').children('aside').last();
        var name = new_survey.find('a').first().attr('name');
        if (name != new_survey_name_cached) {
            if (!$('#create-survey-btn').hasClass('disabled')) {
                return false;
            }

            new_survey_name_cached = name;
            $("html, body").animate({scrollTop: new_survey.offset().top});
            new_survey.find('.edit-survey-btn').trigger('click');
            $('#create-survey-btn').removeClass('disabled');
        }
    });

    $('#create-survey-btn').on('click', function(event) {
        if ($(this).hasClass('disabled')) {
            event.preventDefault();
            return false;
        }
    });

    $(document).on('hide.bs.modal', function() {
        $('.ajaxy-modal-div').remove();
        $('body').removeClass('modal-open');
    });

    $(document).on('triggerAjaxyReady', '.survey-status-link', function(e) {
        $(this).closest('.survey-parent-wrap').trigger('ajaxy-reload');
    })
});