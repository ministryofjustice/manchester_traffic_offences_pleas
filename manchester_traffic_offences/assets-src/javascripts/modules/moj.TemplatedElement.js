/**
 * Templated Element
 *
 * Update the text of an element based on the value of a related input field
 *
 * -----------------------------------------------------------------------
 * Usage:
 *
 * <span class="js-TemplatedElement"
 *     data-template-trigger="field_name"
 *     data-template="Content with {value}"
 *     data-template-defaults-for="Excluded value"
 *     data-template-delegate="#other-element">Original content</span>
 *
 * If templateDelegate is set, the functionality will be transferred to the
 * matching element.
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
      trigger: '',
      template: '{value}',
      defaultsFor: null
    },

    init: function($el, options) {
      this.settings = $.extend({}, this.defaults, options);

      this.trigger = $el.data('templateTrigger') || this.settings.trigger;
      this.template = $el.data('template') || this.settings.template;
      this.defaultsFor = $el.data('templateDefaultsFor') || this.settings.defaultsFor;

      if ($el.data('templateDelegate')) {
        $el = $($el.data('templateDelegate'));
      }

      this.originalText = $el.eq(0).text();

      this.cacheElements($el);

      this.bindEvents();
    },

    cacheElements: function($el) {
      this.$element = $el;
      this.$inputs = $(':radio[name="' + this.trigger + '"]');
    },

    bindEvents: function() {
      var self = this;
      this.$inputs.on('change.TemplatedElement', function() {
        self.updateText();
      });
      moj.Events.on('render.TemplatedElement', function() {
        self.updateText();
      });
    },

    getCurrentValue: function() {
      var $currentSelection = this.$inputs.filter(':checked');
      var currentValue = $currentSelection.attr('data-template-value') || $currentSelection.parent('label').text();

      return currentValue.trim();
    },

    formatValue: function(value) {
      return value.toLowerCase();
    },

    updateText: function() {
      this.$element.text(this.getText());
    },

    getText: function() {
      var text = this.originalText,
          value = this.getCurrentValue();

      if (value && value !== this.defaultsFor) {
        value = this.formatValue(value);
        text = this.populateTemplate(value);
      }

      return text;
    },

    populateTemplate: function(value) {
      return this.template.replace('{value}', value);
    }
  };

  moj.Modules._TemplatedElement = TemplatedElement;

  moj.Modules.TemplatedElement = {
    init: function() {
      return $('.js-TemplatedElement').each(function() {
        $(this).data('TemplatedElement', new TemplatedElement($(this), $(this).data()));
      });
    }
  };

}());
