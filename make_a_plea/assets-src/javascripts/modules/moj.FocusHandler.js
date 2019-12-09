/**
 * Handle several aspects of focusing on the relevant element
 */
(function() {
  'use strict';

  window.moj = window.moj || { Modules: {}, Events: $({}) };

  moj.Modules.FocusHandler = {
    init: function() {
      var $firstAlert = $('.success-header, .error-summary').eq(0);

      /**
       * Set focus to the first alert or success on the page
       */
      this.addTabIndex($firstAlert, '0');
      $firstAlert.focus();

      /**
       * Set focus to the main content when clicking the 'skip link'
       */
      this.addTabIndex($('#content'), '-1');
      $('.skiplink').on('click', function() { $('#content').focus(); });

      /**
       * Set focus to the relevant field when clicking an error message in the summary
       */
      $('.error-summary [href^="#section_"]').on('click', function() {
        var $target = $($(this).attr('href')).find('input, textarea, select').eq(0);
        setTimeout(function() { $target.focus(); }, 250);
      });
    },
    addTabIndex: function($el, tabIndex) {
      if ($el.attr('tabindex') === undefined) {
        $el.attr('tabindex', tabIndex);
      }
    }
  };
}());
