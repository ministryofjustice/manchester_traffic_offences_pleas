$(document).ready(function () {
    jQuery.fx.off = true;

    $('[name^=nojs]').remove();

    $('.skiplink').on('click', function() {
      $('#content').attr('tabindex', -1).on('blur focusout', function() {
        $(this).removeAttr('tabindex');
      }).focus();
    });
});