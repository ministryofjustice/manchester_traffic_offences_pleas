$(document).ready(function () {
    jQuery.fx.off = true;

    $('.nojs-only[name=split_form]').remove();

    $('.skiplink').on('click', function() {
      $('#content').attr('tabindex', -1).on('blur focusout', function() {
        $(this).removeAttr('tabindex');
      }).focus();
    });
});