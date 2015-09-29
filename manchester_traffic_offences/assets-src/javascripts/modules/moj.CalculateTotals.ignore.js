/**
 * Calculate totals
 *
 * Calculate totals for a selection of terms.
 *
 * -----------------------------------------------------------------------
 * Usage:
 *
 * <span class="js-CalculateTotals" data-total-terms=".term" data-total-precision="2"></span>
 */
(function() {
  'use strict';

  window.moj = window.moj || { Modules: {}, Events: $({}) };

  var CalculateTotals = function($el, options) {
    this.init($el, options);
    return this;
  };

  CalculateTotals.prototype = {
    defaults: {
      terms: '.term', // Selector for list of terms
      precision: 2 // Rounding precision (use 0 for integer result)
    },

    init: function($el, options) {
      this.settings = $.extend({}, this.defaults, options);

      this.termSelector = $el.data('totalTerms') || this.settings.terms;
      this.precision = $el.data('totalPrecision') || this.settings.precision;

      this.cacheElements($el);

      this.bindEvents();
    },

    cacheElements: function($el) {
      this.$total = $el;
      this.$terms = $(this.termSelector);
    },

    bindEvents: function() {
      var self = this;
      this.$terms
        .on('change.CalculateTotals update.CalculateTotals', function() {
          self.updateTotal();
        });
      moj.Events
        .on('render.CalculateTotals', function() {
          self.updateTotal();
        });
    },

    getNumericValue: function($element) {
      var value = $element.text();

      if ($element.is(':input')) {
        value = $element.val();
      }

      // Remove commas
      value = value.replace(/,/g,'');

      return ($.isNumeric(value)) ? parseFloat(value) : 0;
    },

    getTotal: function() {
      var self = this,
          total = 0;

      this.$terms.each(function() {
        total += self.getNumericValue($(this));
      });

      return total;
    },

    updateTotal: function() {
      var total = this.getTotal();

      total = this.formatNumber(total);
      this.$total.text(total).trigger('update.CalculateTotals');
    },

    formatNumber: function(number) {
      var parts = number.toFixed(this.precision).toString().split(".");
          parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");

      return parts.join(".");
    }
  };

  moj.Modules._CalculateTotals = CalculateTotals;

  moj.Modules.CalculateTotals = {
    init: function() {
      return $('.js-CalculateTotals').each(function() {
        $(this).data('CalculateTotals', new CalculateTotals($(this), $(this).data()));
      });
    }
  };

}());
