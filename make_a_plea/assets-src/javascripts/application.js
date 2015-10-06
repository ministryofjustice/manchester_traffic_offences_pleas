$(function() {
  jQuery.fx.off = true;
  $('.nojs-only[name=split_form]').remove();

  // Handle spacebar use on links with role=button
  $(document).on('keypress', 'a[role=button]', function(event){
    if (event.keyCode === 32) {
      event.preventDefault();
      event.target.click();
    }
  });
});
