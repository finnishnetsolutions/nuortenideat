
// Animation does not work properly yet. Left here for future refining.
/*
var bars = $(".progress-bar");
$(function() {

    $(".progress-bar").each(progress_bar_animation);

});

function progress_bar_animation()
{
    var bar = $(this);
    var value_now = bar.attr("aria-valuenow");
    var value_max = bar.attr("aria-valuemax");
    var width = value_now / value_max * 100.0;
    bar.animate({
       width: width + "%"
    }, 700);
}
*/