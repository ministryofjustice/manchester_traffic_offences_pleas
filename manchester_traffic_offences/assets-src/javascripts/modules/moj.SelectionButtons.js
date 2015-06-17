/**
 * Selection Buttons
 *
 * Provides extra focused and selected classes to radio and checkbox
 * form inputs to bring them to default gov.uk styling
 */

(function() {
  'use strict';

  window.moj = window.moj || { Modules: {}, Events: $({}) };

  moj.Modules.SelectionButtons = {
    init: function() {

      $('label input[type=radio], label input[type=checkbox]').on({
        'change': function(){
          if ($(this).is(':checked')) {
            if ($(this).is(':radio')) {
              $(this).closest('form').find('[name="' + $(this).attr('name') + '"]').closest('label').removeClass('selected');
            }
            $(this).closest('label').addClass('selected');
          }
          else {
            $(this).closest('label').removeClass('selected');
          }
        },
        'focus': function() {
          $(this).closest('label').addClass('focused');
        },
        'blur': function() {
          $(this).closest('label').removeClass('focused');
        }
      }).trigger('change');

    }
  };

}());
