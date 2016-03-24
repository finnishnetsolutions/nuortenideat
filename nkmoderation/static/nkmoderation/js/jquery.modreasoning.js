/*global jQuery, _*/

(function ($, _) {

    "use strict";

    $.fn.modreasoning = function (action, opts) {

        if (!_.isString(action)) {
            opts = action;
            action = 'initialize';
        }

        opts = $.extend({}, $.fn.modreasoning.defaults, opts);

        var methods = {
            initialize: function () {
                var form = $(this),
                    reasoningForm;

                if (opts.reasonFormHtml) {
                    reasoningForm = $(opts.reasonFormHtml)
                    $(opts.reasonFormTarget).append(reasoningForm);
                } else {
                    reasoningForm = $(this).find(opts.reasonFormSelector);
                }

                opts.reasonGiven = false;

                form.data('modreasoning', opts);

                reasoningForm.on('hidden.bs.modal', function () {
                    var data = form.data('modreasoning');
                    if(data.reasonGiven) {
                        form.trigger('submit');
                    }
                });

                reasoningForm.on('shown.bs.modal', function () {
                    $(this).find(opts.reasonFormReasonInputSelector).focus();
                });

                form.on(opts.triggerEvent, function (e1) {

                    var data = $(this).data('modreasoning');

                    if(data.reasonGiven) {
                        return true;
                    }

                    reasoningForm.modal('show').on('submit', 'form',
                        function (e) {
                            var data = form.data('modreasoning'), reasonInput, reason;

                            e.preventDefault();

                            reasonInput = reasoningForm.find(data.reasonFormReasonInputSelector);
                            reason = $.trim(reasonInput.val());

                            if (reason) {
                                data.reasonGiven = true;
                                form.find(opts.reasonFieldSelector).val(reason);
                                form.data('modreasoning', data);
                                reasoningForm.modal('hide');
                            } else {
                                reasonInput.parent().addClass(opts.fieldWrapErrorClass);
                            }
                        }
                    );

                    return false;
                });
            }
        };

        return this.each(methods[action]);
    };


    $.fn.modreasoning.defaults = {
        reasonFieldSelector: '#moderation-reason',
        reasonFormHtml: null,
        reasonFormTarget: 'body',
        reasonFormSelector: '#reasoning-form',
        reasonFormReasonInputSelector: '.reasoning-input',
        triggerEvent: 'submit',
        fieldWrapErrorClass: 'has-error'
    };

}(jQuery, _));
