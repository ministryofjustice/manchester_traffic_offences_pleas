/**
 * Templated Element
 *
 * Update the text of an element based on the value of a related input field
 *
 * -----------------------------------------------------------------------
 * Usage:
 *
 * <span id="templated">Original content</span>
 *
 * <script>
 * $(function(){
 *   options = {
 *     "trigger": "field_name",
 *     "templates": {
 *       "value_one": "Template one",
 *       "value_two": "Template two"
 *     }
 *   }
 *   new moj.Modules.TemplatedElement($('#templated'), options);
 * });
 * </script>
 */
(function() {
  'use strict';

  window.moj = window.moj || { Modules: {}, Events: $({}) };

  var TemplatedElement = function($el, options) {
    this.init($el, options);
    return this;
  };

  TemplatedElement.prototype = {
    defaults: {
      trigger: ''
    },

    init: function($el, options) {
      this.settings = $.extend({}, this.defaults, options);

      this.trigger = this.settings.trigger;
      this.templates = this.settings.templates;
      this.originalText = $el.eq(0).text();

      this.cacheElements($el);

      this.bindEvents();
    },

    cacheElements: function($el) {
      this.$element = $el;
      this.$inputs = $(':radio' + this.trigger);
    },

    bindEvents: function() {
      var self = this;
      this.$inputs.on('change.TemplatedElement', function() {
        self.updateText();
      });
      this.updateText();
    },

    getCurrentValue: function() {
      return this.$inputs.filter(':checked').val();
    },

    updateText: function() {
      this.$element.text(this.getText());
    },

    getText: function() {
      var text = this.originalText,
          value = this.getCurrentValue();

      if (value && this.templates.hasOwnProperty(value)) {
        text = this.templates[value];
      }

      return text;
    }
  };

  moj.Modules._TemplatedElement = TemplatedElement;

}());
