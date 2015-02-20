$(document).ready(function () {
    jQuery.fx.off = true;

    var selectionButtons = new GOVUK.SelectionButtons($("label input[type='radio'], label input[type='checkbox']"));

    $('details').details();
});
