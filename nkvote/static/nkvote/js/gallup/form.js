$(function(){

    // Enable button click events.
    $(".add-option").click(add_option);
    $(".delete-option").click(delete_option);
    $("#add-question").click(add_question);
    $("#delete-question").click(delete_question);

    // Initial (when the page is load) button disables below.
    var questions_list = $("#questions_list");
    var questions = questions_list.children();
    var questions_count = questions.length;
    var options_wrapper = null, options = null;

    for (var i = 0; i < questions_count; i++)
    {
        options_wrapper = $(questions[i]).children("#options_q-"+(i+1));
        options = options_wrapper.children();

        // Disable add option button, if there are already 10 options.
        if (options.length >= 10)
        {
            var add_option_btn = $(questions[i]).find(".add-option");
            add_option_btn.addClass("disabled");
        }

        // Disable delete option button, if there are only 2 options.
        else if (options.length <= 2)
        {
            var delete_option_btn = options_wrapper.parent().children(".delete-option");
            delete_option_btn.addClass("disabled");
        }
    }

    // Disable delete question button, if there is only 1 question.
    if (questions_count <= 1)
        $("#delete-question").addClass("disabled");

});

function add_option(e)
{
    e.preventDefault();

    var question_seq = $(this).data("question-seq");
    var options_list = $("#options_q-"+question_seq);
    var options_count = options_list.children().length;
    var option_seq = parseInt(options_list.find(".option_seq_number").last().text()) + 1;

    if (options_count == 10) return false;

    $.ajax($(this).attr("href"), {
        data: {
            "question_seq": question_seq,
            "option_seq": option_seq
        }
    })
    .done(function(data) {
        // Append the received html to the options list and show it with animation.
        // Multilingo must be refreshed for the new data to show.
        options_list.append(data);
        $("#gallup-form").multilingo("refresh");
        options_list.children().last().hide().slideDown("fast");

        // Enable the delete button if there are more than 2 options.
        options_count = options_list.children().length;
        var question_wrapper = $("#wrapper_q-"+question_seq);
        var delete_option_btn = question_wrapper.find(".delete-option");
        if (options_count > 2 && delete_option_btn.hasClass("disabled"))
            delete_option_btn.removeClass("disabled");

        // Disable the add button if there are 10 or more options.
        var add_opinion_btn = question_wrapper.find(".add-option");
        if (options_count >= 10 && ! add_opinion_btn.hasClass("disabled"))
            add_opinion_btn.addClass("disabled");
    });
}

function delete_option(e)
{
    e.preventDefault();

    var question_seq = $(this).data("question-seq");
    var options_list = $("#options_q-"+question_seq);
    var options = options_list.children();

    if (options.length <= 2) return false;

    var after_slide = function()
    {
        // Remove the option.
        $(this).remove();

        // Disable the delete button if there is only 2 options left.
        var options_count = options_list.children().length;
        var question_wrapper = $("#wrapper_q-"+question_seq);
        var delete_option_btn = question_wrapper.find(".delete-option");
        if (options_count <= 2 && ! delete_option_btn.hasClass("disabled"))
            delete_option_btn.addClass("disabled");

        // Enable the add button if there are less than 10 options.
        var add_opinion_btn = question_wrapper.find(".add-option");
        if (options_count < 10 && add_opinion_btn.hasClass("disabled"))
            add_opinion_btn.removeClass("disabled");
    };
    options_list.children().last().slideUp("fast", after_slide);
}

function add_question(e)
{
    e.preventDefault();

    var questions_list = $("#questions_list");
    var question_seq = parseInt(questions_list.find(".question_seq_number").last().text()) + 1;

    $.ajax($(this).attr("href"), {
        data: {
            "question_seq": question_seq
        }
    })
    .done(function(data){
        // Append the returned question html and show it with animation.
        questions_list.append(data);
        $("#gallup-form").multilingo("refresh");
        $("#wrapper_q-"+question_seq).hide().slideDown("fast");

        // Add click events to the new buttons.
        $("#wrapper_q-"+question_seq+" a.add-option").click(add_option);
        $("#wrapper_q-"+question_seq+" a.delete-option").click(delete_option);

        // Enable the delete button if there is more than 1 question.
        var delete_question_btn = $("#delete-question");
        var question_count = questions_list.children().length;
        if (question_count > 1 && delete_question_btn.hasClass("disabled"))
            delete_question_btn.removeClass("disabled");
    });
}

function delete_question(e)
{
    e.preventDefault();

    var questions_list = $("#questions_list");
    var questions = questions_list.children();
    if (questions.length <= 1) return false;

    var after_slide = function()
    {
        // Remove the question.
        $(this).remove();

        // Disable the delete button if there is only 1 question or less.
        var delete_question_btn = $("#delete-question");
        var question_count = questions_list.children().length;
        if (question_count <= 1 && ! delete_question_btn.hasClass("disabled"))
            delete_question_btn.addClass("disabled");
    };
    questions.last().slideUp("fast", after_slide);
}

// Refreshes all the inputs required attributes.
function refresh_required()
{
    // Initialize the different input variables.
    var inputs = $("input.multilingo-input");
    var hidden_inputs = $(".multilingo-language-version:hidden").find("input");
    var visible_inputs = $(".multilingo-language-version:visible").find("input");

    // If no language is active, add required to every input and return out of the function.
    if (visible_inputs.length == 0)
    {
        inputs.attr("required", "required");
        return true;
    }

    // Remove hidden inputs' required and add it to visible inputs.
    hidden_inputs.removeAttr("required");
    visible_inputs.attr("required", "required");

    // Get all (unique) languages in multilingo inputs.
    var all_languages = [], languages = [];
    for (var i=0; i < inputs.length; i++)
        all_languages.push($(inputs[i]).data("language-code"));
    $.each(all_languages, function(i, el) {
        if ($.inArray(el, languages) === -1) languages.push(el);
    });

    // Get all the languages that have no values in inputs
    var empty_languages = [];
    for (i=0; i < languages.length; i++)
    {
        var lang_inputs = inputs.filter("[data-language-code=\""+languages[i]+"\"]");
        var all_empty = true;
        for (var j=0; j < lang_inputs.length; j++)
        {
            if ($(lang_inputs[j]).val())
            {
                all_empty = false;
                break;
            }
        }
        if (all_empty) empty_languages.push(languages[i]);
    }

    // If there is atleast one language that has values in inputs.
    if (empty_languages.length < languages.length)
    {
        // Remove required attribute from the visible empty languages inputs.
        for (i=0; i < empty_languages.length; i++)
            visible_inputs.filter("[data-language-code=\"" + empty_languages[i] + "\"]").removeAttr("required");
    }
}
