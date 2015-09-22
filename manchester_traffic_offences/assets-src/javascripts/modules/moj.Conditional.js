/**
 * Conditional form elements reveal
 *
 * Reveal content based on value of related field
 *
 * -----------------------------------------------------------------------
 * Usage:
 *
 * <input type="radio" name="trigger_name" value="regex">
 * <input type="radio" name="trigger_name" value="another value">
 * <div class="js-Conditional" id="target_id" data-conditional-trigger="trigger_name" data-conditional-value="^regex$">...</div>
 */

(function() {
  'use strict';

  window.moj = window.moj || { Modules: {}, Events: $({}) };

  var Conditional = function($el, options) {
    this.init($el, options);
    return this;
  };

  Conditional.prototype = {
    defaults: {},

    init: function($el, options) {
      this.settings = $.extend({}, this.defaults, options);
      this.cacheElements($el);
      this.addAriaAttributes();
      this.bindEvents();
    },

    cacheElements: function($el) {
      this.$conditional = $el;
      this.$inputs = $('[name="' + $el.data('conditionalTrigger') + '"]');
    },

    bindEvents: function() {
      var self = this;
      this.$inputs
        .on('change.Conditional', function() {
          self.toggle();
        });
      moj.Events
        .on('render.Conditional', function() {
          self.toggle();
        });
    },

    addAriaAttributes: function() {
      this.$inputs.attr('aria-controls', this.$conditional.attr('id'));
    },

    getInputValue: function($input) {
      switch($input.attr('type')) {
        case "radio":
          return $('[name="' + $input.attr('name') + '"]:checked').attr('value');

        case "checkbox":
          return $input.filter(':checked').val();

        default:
          return $input.val() || $input.find(':selected').attr('value');
      }
    },

    toggle: function() {
      var currentValue = this.getInputValue(this.$inputs),
          testExpression = new RegExp(this.$conditional.data('conditionalValue'));

      if (currentValue && currentValue.match(testExpression)) {
        this.$conditional
          .show()
          .attr('aria-expanded', 'true')
          .attr('aria-hidden', 'false');
      }
      else {
        this.$conditional
          .hide()
          .attr('aria-expanded', 'false')
          .attr('aria-hidden', 'true');
      }
    }
  };

  moj.Modules._Conditional = Conditional;

  moj.Modules.Conditional = {
    init: function() {
      return $('.js-Conditional').each(function() {
        $(this).data('Conditional', new Conditional($(this), $(this).data()));
      });
    }
  };

}());
