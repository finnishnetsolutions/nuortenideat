/*global jQuery*/

(function ($) {

    "use strict";

    $.fn.formidableFormset = function (method, opts) {

        if (typeof method !== "string") {
            opts = method || {};
            method = 'initialize';
        }

        opts = $.extend({}, $.fn.formidableFormset.defaults[opts.defaults || 'default'], opts);

        return this.each(function () {
            $.fn.formidableFormset.api[method].call(this, opts)
        });
    };

    $.fn.formidableFormset.defaults = {
        default: {
            addFormMethod: 'append',
            deleteFormButtonSelector: '.formidable-formset-form-delete',
            addFormButtonSelector: '.formidable-formset-form-add',
            formsWrapSelector: '.formidable-formset-forms',
            formWrapSelector: '.formidable-form-wrap',
            tooltipAttribute: 'title',
            deleteInputName: null,
            disabledButtonClass: 'disabled',
            disableUnUpdatable: false,
            unUpdatableFormWrapClass: null,
            newFormTemplate: null,
            newFormTemplateSelector: null,
            formIndexPlaceHolder: '__form_index__',
            nextFormIndex: null,
            minForms: 0,
            maxForms: 10
        }
    };

    $.fn.formidableFormset.api = {
        initialize: function (commonOpts) {
            var formset, formsetId, formsWrap, opts, addFormButton, deleteInput;

            formset = $(this);
            formsetId = formset.attr('id');

            opts = $.extend({}, commonOpts, formset.data());

            formsWrap = formset.children(opts.formsWrapSelector);
            if (formsWrap.length === 0) {
                formsWrap = formset.find(opts.formsWrapSelector).filter(function () {
                    return !$(this).data('formsetId') || ($(this).data('formsetId') === formsetId);
                });
            }

            if (opts.newFormTemplateSelector) {
                if (opts.newFormTemplate) {
                    throw "You must only specify one of the newFormTemplate and newFormTemplateSelector options"
                }
                opts.newFormTemplate = $(opts.newFormTemplateSelector).html();
            }

            if (!opts.newFormTemplate) {
                throw "newFormTemplate option is not defined";
            }

            if (opts.newFormTemplate.indexOf(opts.formIndexPlaceHolder) === -1) {
                throw "newFormTemplate does not contain formIndexPlaceHolder (" + opts.formIndexPlaceHolder +")";
            }

            if  (opts.nextFormIndex === null) {
                opts.nextFormIndex = formset.children('.formidable-form-wrap').length;
            }

            opts.nextFormIndex = parseInt(opts.nextFormIndex);
            opts.maxForms = parseInt(opts.maxForms);
            opts.minForms = parseInt(opts.minForms);

            formset.data('formidableFormset', opts);

            addFormButton = $(opts.addFormButtonSelector);

            if (opts.deleteInputName) {
                deleteInput = formset.find('select[name="' + opts.deleteInputName + '"]');
            } else {
                deleteInput = $('<select />').prop('multiple', true);
            }

            formset.on('click', opts.deleteFormButtonSelector, function () {
                if (($(this).data('formsetId') && $(this).data('formsetId') !== formsetId) ||
                        $(this).hasClass(opts.disabledButtonClass)) {
                    return;
                }
                $(this).closest(opts.formWrapSelector).fadeOut('fast', function () {
                    var objectId = $(this).data('objectId');
                    if (objectId) {
                        deleteInput.append(
                            $('<option/>').val(objectId).text(objectId).prop('selected', true)
                        );
                    }
                    $(this).remove();
                    formset.trigger('formidableFormset.formCountChanged');
                });
            });

            formset.on('click', opts.addFormButtonSelector, function (e) {
                var formTemplate, newForm;

                if (($(this).data('formsetId') && $(this).data('formsetId') !== formsetId)
                    || $(this).hasClass(opts.disabledButtonClass))
                {
                    return;
                }

                formTemplate = opts.newFormTemplate.replace(
                    new RegExp(opts.formIndexPlaceHolder, 'g'),
                    (opts.nextFormIndex++).toString()
                );

                newForm = $(formTemplate).hide();
                formsWrap[opts.addFormMethod](newForm);
                newForm.fadeIn().trigger('formidableFormset.formAdded',
                                         {formset: formset, form: newForm});
                formset.trigger('formidableFormset.formCountChanged');
            });

            formset.on('formidableFormset.formCountChanged', function () {
                var formCount = formsWrap.children(opts.formWrapSelector).length;
                addFormButton.toggleClass('disabled', formCount >= opts.maxForms);
                formset.find(opts.deleteFormButtonSelector).each(function () {
                    var deleteFormsetId = $(this).data('formsetId'), deletable;
                    deletable = parseInt(
                        $(this).closest(opts.formWrapSelector).data('deletable')
                    );
                    if (!deleteFormsetId || (deleteFormsetId === formsetId)) {
                        // this delete button (probably) belongs to our jurisdiction
                        $(this).toggleClass(opts.disabledButtonClass,
                                            formCount <= opts.minForms || !deletable);
                    }
                })
            });

            formsWrap.children(opts.formWrapSelector).each(function () {
                if (parseInt($(this).data('updatable')) !== 1) {
                    if (opts.disableUnUpdatable) {
                        $(this).find(':input').prop('disabled', true);
                    }
                    if (opts.unUpdatableFormWrapClass) {
                        $(this).toggleClass(opts.unUpdatableFormWrapClass, true);
                    }
                    $(this).trigger('formidableFormset.formDisabled');
                }
            });

            formset.trigger('formidableFormset.formCountChanged');
        }

    };

}(jQuery));
