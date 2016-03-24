$(function() {

    'use strict';

    var INPUT_NOTIFY_VALUE = 'notify';

    $(document).on('change', 'input[value="'+INPUT_NOTIFY_VALUE+'"]', function() {
        if ($(this).prop('checked') === true) {
            $(this).parents('div.checkbox').siblings().show();

            if ($(this).parents('div.checkbox').siblings().find('input[type="checkbox"]:checked').length === 0) {
                 $(this).parents('div.checkbox').siblings().find('input[type="checkbox"]').first().prop('checked', true);
            }
            return false;
        }
        $(this).parents('div.checkbox').siblings().find('input[type="checkbox"]').prop('checked', false);
        $(this).parents('div.checkbox').siblings().hide();
    });

    $(document).on('change', 'input[value!="'+INPUT_NOTIFY_VALUE+'"]', function() {
        if ($(this).prop('checked') === false) {
            if ($(this).parents('div.checkbox').siblings().find('input[type="checkbox"][value!="'+INPUT_NOTIFY_VALUE+'"]:checked').length === 0) {
                $(this).parents('div.checkbox').siblings().find('[value="'+INPUT_NOTIFY_VALUE+'"]').click();
            }
        }
    });

    $(document).on('ajaxy-refreshed', function() {
        $('input[value="'+INPUT_NOTIFY_VALUE+'"]').trigger('change');
    });
});