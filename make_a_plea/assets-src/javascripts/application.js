//= require moj.js
//= require modules/moj.Conditional.js
//= require modules/moj.Details.js
//= require modules/moj.ExternalLinksTracker.js
//= require modules/moj.FocusHandler.js
//= require modules/moj.PromptOnChange.js
//= require modules/moj.SelectionButtons.js
//= require modules/moj.TemplatedElement.js

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

  moj.init();
});
