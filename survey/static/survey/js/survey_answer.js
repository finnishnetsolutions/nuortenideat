$(function() {
    var survey_elements = $(".survey-elements");

    //if ( ! $(".survey-wrap").data("survey-submitted") && $(".survey-wrap").data("survey-answerable")) {
    if ( ! $(".survey-wrap").data("survey-submitted")) {
        // Hide pages beyond first pagebreak.
        var current_page = 0;
        survey_elements.children().each(function(index) {
            var element = $(this);

            if (current_page >= 1) {
                element.hide();
            }
            if (element.hasClass("survey-element-page-button-wrap")) {
                current_page += 1;
            }
        });

        // Hide answer button initially if there are multiple pages.
        if (survey_elements.children(".survey-element-page-button-wrap").length >= 1) {
            $(".survey-actions").hide();
        }

        // Clicking a page break button loads more questions.
        $(".survey-element-page-btn").click(function() {
            var button_wrap = $(this).parent();
            var next_page = button_wrap.nextAll(".survey-element-page-button-wrap:first");
            button_wrap.nextUntil(next_page.next()).fadeIn();
            button_wrap.hide();

            // Show survey actions only on the last page.
            if (next_page.nextAll(".survey-element-page-button-wrap").length == 0) {
                $(".survey-actions").show();
            }
        });
    }
    else {
        $(".survey-element-page-button-wrap").hide();
    }

    // moved to idea_detail.html
    // $(".survey-submit").on('click', function() {
    //     var top = $(this).parents('.survey-wrap').siblings('.survey-anchor').offset().top
    //     $("html, body").animate({scrollTop: top});
    // });
});
