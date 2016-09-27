/* global $, window*/

$(function () {

    "use strict";

    var ajaxySuccess = function(wrap, returnUrl, successWrap, targetMethod, trigger) {
        return function (resp) {
            if(typeof resp === "string") {
                // Try to interpret response as json. Useful with
                // jQuery form plugin's IE9 iframe file upload hack.
                try {
                    resp = jQuery.parseJSON(resp);
                } catch (e) {
                }
            }
            if (resp.success) {

                if (successWrap) {
                   wrap = $(successWrap);
                }
                var next = resp.next || returnUrl;
                if (targetMethod) {
                    $.get(next, function(data) {
                        wrap[targetMethod](data);
                        wrap.trigger('ajaxy-refreshed');
                    });
                } else {
                    wrap.load(next, function () {
                        wrap.trigger('ajaxy-refreshed');
                    });
                }
            } else if (resp.location) {
                window.location = resp.location;
            } else if (resp.reload) {
                if (resp.hash) {
                    window.location.hash = resp.hash;
                }
                window.location.reload(true);
            } else if (typeof resp === "string") {
                targetMethod = targetMethod || "html";
                wrap[targetMethod](resp).trigger('ajaxy-refreshed');
            }

            if (resp.trigger) {
                trigger.trigger('triggerAjaxyReady');
            }
        }
    };

    $(document).on('click', '.ajaxy-link', function (e) {
        var target, method, confirmation, targetMethod;

        e.preventDefault();

        confirmation = $(this).attr("data-ajaxy-confirm");
        if (confirmation && !window.confirm(confirmation)) {
            return false;
        }

        target = $(this).attr('data-ajaxy-target'),
        method = $(this).attr("data-ajaxy-method") || "GET";
        targetMethod = $(this).attr("data-ajaxy-target-method") || targetMethod;

        if (target) {
            target = $(target);
        } else if($(this).data('toggle') == 'ajaxy-modal') {
            var dialogClass = $(this).data('modal-dialog-class') || 'modal-lg';
            var modalWrap = $(
                '<div class="modal fade ajaxy-modal-div">' +
                    '<div class="modal-dialog">' +
                        '<div class="modal-content ajaxy-wrap"></div>' +
                    '</div>' +
                '</div>'
            );
            modalWrap.children('.modal-dialog').addClass(dialogClass);
            target = modalWrap.find('.ajaxy-wrap');
            $('body').append(modalWrap.hide());
        } else {
            target = $(this).parents('.ajaxy-wrap').first();
        }

        $.ajax($(this).attr('href'), {
            type: method,
            success: ajaxySuccess(target, $(this).attr('data-ajaxy-success-url'),
                $(this).attr('data-ajaxy-success-wrap'), targetMethod, $(this))
        });

    });

    $(document).on('ajaxy-refreshed', '.modal-content.ajaxy-wrap', function () {
        $(this).parents('.modal').first().modal('show');
    });

    $(document).on('submit', '.ajaxy-form', function (e) {
        var form = $(this),
            wrap = $(this).parents('.ajaxy-wrap').first(),
            onSuccess, beforeSubmit, targetMethod;

        e.preventDefault();

        var target = $(this).attr('data-ajaxy-target');
        if (target) {
            wrap = $(target);
        }

        targetMethod = $(this).attr("data-ajaxy-target-method") || targetMethod;

        onSuccess = ajaxySuccess(wrap, form.attr('data-ajaxy-return-url'),
            form.attr('data-ajaxy-success-wrap'), targetMethod);

        beforeSubmit = $.Event("beforeAjaxySubmit")

        form.trigger(beforeSubmit);

        if (beforeSubmit.isPropagationStopped()) {
            return false;
        }

        if(form.is('form')) {
            $(this).ajaxSubmit({success: onSuccess});
        } else {
            // TODO: completely untested..
            var data = form.find('input,textarea,select').serialize();
            $.post(form.attr('data-ajaxy-action'), data).done(onSuccess);
        };
    });

    $(document).on('ajaxy-reload', '.ajaxy-wrap', function (e) {
        e.stopPropagation();
        $(this).load($(this).attr('data-ajaxy-url'), function () {
            $(this).trigger('ajaxy-refreshed');
        });
    });

    $(document).on('click', '.ajaxy-form .ajaxy-form-close', function (e) {
        e.preventDefault();
        var form;
        form = $(this).parents('.ajaxy-form');
        $(this).parents('.ajaxy-wrap').load(form.attr('data-ajaxy-return-url'));
    });

});
