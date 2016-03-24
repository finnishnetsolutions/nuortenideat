$(function() {
    "use strict";

    function change_choice(event) {
        var loader_obj = show_loader_icon();
        $.ajax({
            url: $("#messages-change-url").attr("href"),
            data: {
                'page': get_active_page_nr(),
                "nayta": $(this).val(),
                "jarjestys": $("#messages-sorting").val()
            }
        }).done(function(html) {
            loader_obj.hide();
            $("#messages-table-wrapper").html(html);
        });
    }

    function change_sorting(event) {
        var loader_obj = show_loader_icon();
        $.ajax({
            url: $("#messages-change-url").attr("href"),
            data: {
                'page': get_active_page_nr(),
                "nayta": $("#messages-choice").val(),
                "jarjestys": $(this).val()
            }
        }).done(function(html) {
            loader_obj.hide();
            $("#messages-table-wrapper").html(html);
        });

    }

    function show_loader_icon() {
        var $ajax_loading = $("#messages-ajax-loading");
        $ajax_loading.show();
        return $ajax_loading;
    }

    function get_active_page_nr() {
        return $('ul.pagination > li.active').find('a').html();
    }


    $("#messages-choice").on('change', change_choice);
    $("#messages-sorting").on('change', change_sorting);
    $(document).on('click', 'ul.pagination > li', function(event) {
        event.preventDefault();
        event.stopPropagation();
        var url = $(this).find('a').attr('href');
        var loader_obj = show_loader_icon();
        if (url === '#') {
            loader_obj.hide();
            return false;
        }

        var data = {
            'nayta': $("#messages-choice").val(),
            'jarjestys': $("#messages-sorting").val()
        };

        url += "&" + $.param(data);
        $.ajax({url: url})
            .done(function(html) {
                loader_obj.hide();
                $("#messages-table-wrapper").html(html);
            });
        return false;
    });
});
