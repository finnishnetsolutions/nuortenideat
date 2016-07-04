var survey_wrap = null;
var new_question_id = 0;
var new_subtitle_id = 0;

$(function() {

    survey_wrap = $(".survey-wrap");
    var survey_elements = $(".survey-elements");

    survey_elements.on("click", ".survey-element-up", move_element_up);
    survey_elements.on("click", ".survey-element-down", move_element_down);
    survey_elements.on("click", ".survey-element-delete", delete_element);

    survey_elements.on("click", ".survey-element-save", function() {
        update_element_order($(this).closest(".survey-element"));
    });

    $(".survey-element-add").on('click', add_element);

    survey_wrap.on("elementAdd", function(e, element) {
        if (element.hasClass("survey-element-question") && element.hasClass("survey-element-new")) {
            new_question_id += 1;
        }
        if (element.hasClass("survey-element-subtitle") && element.hasClass("survey-element-new")) {
            new_subtitle_id += 1;
        }
    });
});

function move_element_up(e) {
    e.preventDefault();
    var element = $(this).closest(".survey-element");

    if (element.is(":first-child")) {
        return;
    }

    var commit_move = function() {
        var previous_element = element.prevAll(".survey-element:first");
        element.insertBefore(previous_element);

        // Update page numbers if necessary.
        if (element.hasClass("survey-element-page") && previous_element.hasClass("survey-element-page")) {
            var page_number = element.find(".survey-element-page-number");
            page_number.text(parseInt(page_number.text()) - 1);

            page_number = previous_element.find(".survey-element-page-number");
            page_number.text(parseInt(page_number.text()) + 1);
        }

        update_element_order(element);
    };

    // If href exists, do ajax call, else just move the element.
    var url = $(this).attr("href");
    if (url) {
        $.ajax({
            url: url,
            method: "post",
            success: function() {
                commit_move();
            }
        });
    }
    else {
        commit_move();
    }
}

function move_element_down(e) {
    e.preventDefault();
    var element = $(this).closest(".survey-element");

    if (element.is(":last-child")) {
        return;
    }

    var commit_move = function() {
        var next_element = element.nextAll(".survey-element:first");
        element.insertAfter(next_element);

        // Update page numbers if necessary.
        if (element.hasClass("survey-element-page") && next_element.hasClass("survey-element-page")) {
            var page_number = element.find(".survey-element-page-number");
            page_number.text(parseInt(page_number.text()) + 1);

            page_number = next_element.find(".survey-element-page-number");
            page_number.text(parseInt(page_number.text()) - 1);
        }

        update_element_order(element);
    };

    // If href exists, do ajax call, else just move the element.
    // When creating an element, it may not have the href yet.
    var url = $(this).attr("href");
    if (url) {
        $.ajax({
            url: $(this).attr("href"),
            method: "post",
            success: function() {
                commit_move();
            }
        });
    }
    else {
        commit_move();
    }
}

function delete_element(e) {
    e.preventDefault();
    var element = $(this).closest(".survey-element");

    var commit_delete = function() {
        // If deleted element is page, update the rest page numbers.
        if (element.hasClass("survey-element-page")) {
            element.nextAll(".survey-element-page").each(function(index) {
                var page_number = $(this).find(".survey-element-page-number");
                page_number.text(parseInt(page_number.text()) - 1);
            });
        }

        // TODO: If deleted element is a question, update the rest of the questions orders.
        var wrap = element.parents('.survey-wrap')

        element.remove();
        survey_wrap.trigger("elementRemove", [element]);
    };

    // If href exists, do ajax call, else just move the element.
    var url = $(this).attr("href");
    if (url) {
        $.ajax({
            url: $(this).attr("href"),
            method: "post",
            success: function() {
                commit_delete();
            }
        });
    }
    else {
        commit_delete();
    }
}

function add_element(e) {
    e.preventDefault();
    var data = {};
    var add_button = $(this);

    if (add_button.hasClass("survey-element-add-question")) {
        data.prefix_id = new_question_id;
    }
    if (add_button.hasClass("survey-element-add-subtitle")) {
        data.prefix_id = new_subtitle_id;
    }
    $.ajax({
        url: $(this).attr("href"),
        method: $(this).data("method"),
        data: data,
        success: function(data) {
            var wrap = add_button.parents('.survey-wrap')
            wrap.find(".survey-elements").append(data);
            wrap.trigger("elementAdd", [$(data)]);
        }
    });
}

// Updates the elements order input if it has one.
function update_element_order(element) {
    var order_input = element.find(".order");
    if (order_input.length) {
        order_input.val(element.prevAll(".survey-element").not(".survey-element-new").length);
    }
}
