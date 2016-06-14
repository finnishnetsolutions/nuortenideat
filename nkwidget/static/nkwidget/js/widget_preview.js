$(function() {
    $(".widget-modal-refreshers").find(":input").change(refresh_widget_preview);
    $(".widget-modal-refresher").change(refresh_widget_preview);
    $("#widget-modal").on("shown.bs.modal", function() {
        refresh_widget_preview();
    });
    $("#widget-modal-code").focus(function() {
        $(this).select();
        $(this).mouseup(function () {
            $(this).unbind("mouseup");
            return false;
        });
    });
});

function refresh_widget_preview() {
    // Generate the url with the proper query string.
    var widget_url = $("#widget-modal").data("widget-url");
    var query_string = window.document.location.search || "?";
    if (query_string != "?") query_string += "&";
    var color = "color=" + $("#id_color").val();
    var limit = "limit=" + $("#id_limit").val();
    var language = "language=" + $("#id_language").val();
    query_string += [color, limit, language].join("&");
    widget_url += query_string;

    // Update the iframe's src.
    var preview_wrap = $("#widget-iframe");
    preview_wrap.attr("src", widget_url);

    // Update the code box.
    $("#widget-modal-code").val('<iframe src="' + widget_url + '"></iframe>');

    // Update the iframe height based on the content.
    preview_wrap.ready(function() {
        var preview_height = preview_wrap.contents().find("main").height() + 6;
        preview_wrap.height(preview_height);

        // Needs a small wait for the iframe content to load, to get the real height.
        setTimeout(function() {
            var preview_height = preview_wrap.contents().find("main").height() + 6;
            preview_wrap.height(preview_height);
        }, 200);
        setTimeout(function() {
            var preview_height = preview_wrap.contents().find("main").height() + 6;
            preview_wrap.height(preview_height);
        }, 600);
    });
}
