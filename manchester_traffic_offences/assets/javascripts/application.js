$(document).ready(function() {

  // Example - Form focus styles

  if ($('.form').length>0) {

    $(".block-label").each(function() {

      // Add focus
      $(".block-label input").focus(function() {
        $("label[for='" + this.id + "']").addClass("add-focus");
        }).blur(function() {
        $("label").removeClass("add-focus");
      });

    });

    // Add/remove selected class
    $('.block-label').find('input[type=radio], input[type=checkbox]').click(function() {

      $('.toggle-content').hide();

      var target = $('input:checked').parent().attr('data-target');
      $('#'+target).show();

    });

    // For pre-checked inputs, show toggled content
    var target = $('input:checked').parent().attr('data-target');
    $('#'+target).show();

  }

});
