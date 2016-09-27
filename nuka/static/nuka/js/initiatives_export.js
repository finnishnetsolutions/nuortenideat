$(function() {

    var onSubmitMain = function(e) {
        $('#initiative_list').html('');
        $('.loader-gif').clone().appendTo($('#initiative_list')).show();
    };

    $('#idea-form').on('submit.Main', onSubmitMain);

    $('button[name="export"]').on('click', function(e) {
        e.preventDefault();
        var export_choice = $('<input type="hidden" name="export" value="'+$(this).val()+'" />');
        var form = $('#idea-form');
        form.removeClass('ajaxy-form').attr('target', '_blank').
                off('submit.Main').
                append(export_choice).
                submit();

        export_choice.remove();
        form.on('submit.Main', onSubmitMain).
                addClass('ajaxy-form').attr('target', '');
    });

});