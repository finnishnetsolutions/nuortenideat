// Include on page to add asterisk on all required form fields.
$(document).ready(function()
{
    var required_fields = $("form").find(":input[required]");

    for (var i = 0; i < required_fields.length; i++)
    {
        var label = $(required_fields[i]).parent().children("label");
        label.text(label.text() + "*");
    }
});