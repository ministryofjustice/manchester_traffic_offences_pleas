$(function() {
  jQuery.fx.off = true;

  $('.nojs-only[name=split_form]').remove();

  $(document).on('click', '.skiplink', function() {
    $('#content').attr('tabindex', -1).on('blur focusout', function() {
      $(this).removeAttr('tabindex');
    }).focus();
  });

  // Handle spacebar use on links with role=button
  $(document).on('keypress', 'a[role=button]', function(event){
    if (event.keyCode === 32) {
      event.preventDefault();
      event.target.click();
    }
  });
});
