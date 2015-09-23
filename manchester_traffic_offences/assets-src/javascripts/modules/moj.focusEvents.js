
(function(){
  'use strict';

  window.moj = window.moj || { Modules: {}, Events: $({}) };

  /**
   * Move focus to main content when using the Skip link
   */
  $('.skiplink').on('click', function() {
    $('#content').attr('tabindex', -1).on('blur focusout', function() {
      $(this).removeAttr('tabindex');
    }).focus();
  });

  /**
   * Move focus to error summary or success header when present
   */


  /**
   * Move focus to associated field when clicking an error summary error message
   */

})();
