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
          if ($('#id_guilty_not_guilty').closest('label').hasClass('selected')) {
            $('section[data-conditional-value="^guilty_court$"]').find('input[type="radio"]').prop('checked', false);
            $('section[data-conditional-value="^guilty_court$"]').find('label').removeClass('selected')
            if ($(this).attr('id') == 'id_interpreter_needed_true') {
              $('section[data-conditional-value="^not_guilty$"]').find('label[for="id_interpreter_needed_true"]').addClass('selected');
              $('section[data-conditional-value="^not_guilty$"]').find('input[id="id_interpreter_needed_true"]').prop('checked', true);
            } else if ($(this).attr('id') == 'id_interpreter_needed_false') {
              $('section[data-conditional-value="^not_guilty$"]').find('label[for="id_interpreter_needed_false"]').addClass('selected');
              $('section[data-conditional-value="^not_guilty$"]').find('input[id="id_interpreter_needed_false"]').prop('checked', true);
            }
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
