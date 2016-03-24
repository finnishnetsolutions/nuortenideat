/*global jQuery, _*/

(function ($, _) {

    "use strict";

    $.fn.multilingo = function (action, opts) {

        if (!_.isString(action)) {
            opts = action;
            action = 'initialize';
        }

        var methods = {
            initialize: function () {
                var form = $(this).toggleClass('multilingo-form', true), langSelect,
                    activeLanguage;

                opts = $.extend({}, $.fn.multilingo.defaults, opts);

                langSelect = $(opts.langSelect)

                if (!opts.visibleLanguages) {
                    activeLanguage = opts.activeLanguage || opts.languages[0].code;
                    opts.visibleLanguages = [activeLanguage];
                    form.find('.multilingo-input').each(function () {
                       if ($.trim($(this).val() || "") &&
                           !_.contains(opts.visibleLanguages,
                               $(this).data('language-code'))) {
                           opts.visibleLanguages.push($(this).data('language-code'));
                       }
                    });
                }

                form.data('multilingo', _.extend({languageSelect: langSelect}, opts));

                langSelect.find(opts.langSelectTextSelector).text(opts.langChoiceText);
                langSelect.find(opts.langSelectChoicesSelector).html(
                    _.map(opts.languages, function (lang) {
                        var el = $(opts.langElement);
                        el.data('language-code', lang.code);
                        el.find(opts.langElementLabelSelector).text(lang.label);
                        el.click(function (e) {
                            e.preventDefault();
                            form.multilingo('toggle', lang.code);
                        });
                        return el;
                    })
                );
                form.prepend(langSelect);
                form.multilingo('refresh');
            },
            toggle: function () {
                var ml = $(this).data('multilingo'), lang = opts;
                if (_.contains(ml.visibleLanguages, lang)) {
                    ml.visibleLanguages = _.without(ml.visibleLanguages, lang);
                } else {
                    ml.visibleLanguages.push(lang);
                }
                ml.languagesChanged = true;
                $(this).data('multilingo', ml);
                $(this).multilingo('refresh');
            },
            refresh: function () {
                var ml = $(this).data('multilingo');

                $(this).find('.multilingo-language-version').each(function () {
                    $(this).toggle(
                        _.contains(ml.visibleLanguages, $(this).data('language-code'))
                    );
                });

                ml.languageSelect.find(ml.langElementSelector).each(function () {
                    var isActive = _.contains(ml.visibleLanguages,
                                              $(this).data('language-code'));
                    $(this).find(ml.langElementIconSelector).toggleClass(
                        ml.langElementIconCheckedClass, isActive
                    );
                });

                $(this).toggleClass('languages-changed', ml.languagesChanged);
                $(this).toggleClass('multiple-languages', ml.visibleLanguages.length > 1);
            }
        };
        return this.each(methods[action]);
    };

    $.fn.multilingo.defaults = {
        langSelect: '<div class="multilingo-select-wrap"><div class="btn-group multilingo-select"><div class="dropdown">' +
                    '<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-expanded="true">' +
                        '<span class="glyphicon glyphicon-cog"></span> ' +
                        '<span class="language-choice-text"></span> ' +
                        '<span class="caret"></span>' +
                    '</button>' +
                    '<ul class="dropdown-menu language-choices-wrap" role="menu"></ul>' +
                    '</div></div></div>',
        langSelectTextSelector: '.language-choice-text',
        langSelectChoicesSelector: '.language-choices-wrap',
        langElement: '<li class="language-choice"><a href="#" role="menuitem"><i class="fa fa-check fa-fw"></i> <span></span></a></li>',
        langElementSelector: '.language-choice',
        langElementIconSelector: '.fa',
        langElementIconCheckedClass: 'fa-check',
        langElementLabelSelector: 'span',
        langChoiceText: "Language versions",
        languages: [],
        languagesChanged: false
    };

}(jQuery, _));
