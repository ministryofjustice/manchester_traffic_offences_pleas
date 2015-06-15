/**
 * Fallback for browsers not supporting native trim()
 */
if(typeof String.prototype.trim !== 'function') {
  String.prototype.trim = function() {
    return this.replace(/^\s+|\s+$/g, ''); 
  };
}

// Function.prototype.bind
//
// A polyfill for Function.prototype.bind. Which lets you bind a defined
// value to the `this` keyword in a function call.
//
// Bind is natively supported in:
//   IE9+
//   Chrome 7+
//   Firefox 4+
//   Safari 5.1.4+
//   iOS 6+
//   Android Browser 4+
//   Chrome for Android 0.16+
//
// Originally from:
// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function/bind
if (!Function.prototype.bind) {
  Function.prototype.bind = function (oThis) {
    if (typeof this !== "function") {
      // closest thing possible to the ECMAScript 5
      // internal IsCallable function
      throw new TypeError("Function.prototype.bind - what is trying to be bound is not callable");
    }

    var aArgs = Array.prototype.slice.call(arguments, 1),
        fToBind = this,
        fNOP = function () {},
        fBound = function () {
          return fToBind.apply(this instanceof fNOP && oThis
                 ? this
                 : oThis,
                 aArgs.concat(Array.prototype.slice.call(arguments)));
        };

    fNOP.prototype = this.prototype;
    fBound.prototype = new fNOP();

    return fBound;
  };
}

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
/**
 * Details Element
 *
 * Replicate <details> functionality that's entirely cross-browser
 * compatible and offers options to update text depending on state
 *
 * -----------------------------------------------------------------------
 * Usage:
 *
 * <div class="js-Details [open]" data-summary-open="Alternative text">
 *   <a class="details-trigger" href="#details-content"><span class="summary">View details</span></a>
 *   <div class="details-content" id="details-content">
 *     Content here
 *   </div>
 * </div>
 *
 * If summaryOpen is set, the summary text is replaced when open. Copy in markup
 * should always be for the closed state.
 */
(function() {
  "use strict";

  window.moj = window.moj || { Modules: {}, Events: $({}) };

  var Details = function($el, options) {
    this.init($el, options);
    return this;
  };

  Details.prototype = {

    init: function($el, options) {
      
      $("<i>").addClass("arrow arrow-closed").text("\u25ba").prependTo($('.details-trigger', $el));

      this.cacheElements($el);
      this.addAriaAttributes();
      this.bindEvents();

      this.isOpera = Object.prototype.toString.call(window.opera) == "[object Opera]";

      this.openText = this.$details.data("summary-open");
      this.closedText = this.$summaryText.text();

      this.updateState();
    },

    cacheElements: function($el) {
      this.$details = $el;
      this.$summary = $(".details-trigger", $el);
      this.$summaryText = $(".summary", this.$summary);
      this.$content = $(".details-content", $el);
      this.$icon = $("i.arrow", this.$summary);
    },

    addAriaAttributes: function() {
      var id = this.$content.attr("id");

      if (!id) {
        id = "js-details-" + this.$details.index(".js-Details");
        this.$content.attr("id", id);
      }

      this.$summary.attr({
        "role": "button",
        "aria-controls": id,
        "aria-expanded": "false"
      });

      this.$content.attr({
        "aria-hidden": "true"
      });
    },

    bindEvents: function() {
      var self = this;

      this.$summary.off("click.details keydown.details").on({
        "click.details": function(event) {
          event.preventDefault();
          self.toggleContent();
        },
        "keydown.details": function(event) {
          if (event.keyCode == 32 || (event.keyCode == 13 && !self.isOpera)) {
            event.preventDefault();
            self.$summary.click();
          }
        }
      });
    },

    updateState: function() {
      if (this.$details.hasClass("open")) {
        this.$summary.attr("aria-expanded", "true");
        this.$content.show().attr("aria-hidden", "false");
        this.$icon.removeClass("arrow-closed").addClass("arrow-open").text("\u25bc");

        if (this.openText) {
          this.$summaryText.text(this.openText);
        }
      }
      else {
        this.$summary.attr("aria-expanded", "false");
        this.$content.hide().attr("aria-hidden", "true");
        this.$icon.removeClass("arrow-open").addClass("arrow-closed").text("\u25ba");

        if (this.openText) {
          this.$summaryText.text(this.closedText);
        }
      }
    },

    toggleContent: function() {
      this.$details.toggleClass("open");
      this.updateState();
    }
  };

  moj.Modules._Details = Details;

  moj.Modules.Details = {
    init: function() {
      return $(".js-Details").each(function() {
        $(this).data("Details", new Details($(this), $(this).data()));
      });
    }
  };

}());
(function() {
  "use strict";

  window.moj = window.moj || { Modules: {}, Events: $({}) };

  var ExternalLinksTracker = function($el, options) {
    this.init($el, options);
    return this;
  };

  ExternalLinksTracker.prototype = {
    defaults: {
      "eventCategory": "External links",
      "eventAction": document.location.pathname
    },

    init: function($el, options) {
      if (typeof ga === "undefined") return;

      this.settings = $.extend({}, this.defaults, options);
      this.cacheElements($el);
      this.bindEvents();
    },

    cacheElements: function($el) {
      this.$links = $el;
    },

    bindEvents: function() {
      var self = this;

      this.$links.on('click', function(event) {
        event.preventDefault();
        self.sendGAEvent($(this));
      });
    },

    sendGAEvent: function($el) {
      var self = this,
          href = $el.attr("href"),
          target = $el.attr("target");

      ga("send",
         "event",
         self.settings.eventCategory,
         href,
         self.settings.eventAction,
         {"hitCallback": self.openLink(href, target)}
      );
    },

    openLink: function(href, target) {
      if (target && !/^_(self|parent|top)$/i.test(target)) {
        window.open(href, target);
      }
      else {
        window.location.href = href;
      }
    }
  };

  moj.Modules._ExternalLinksTracker = ExternalLinksTracker;

  moj.Modules.ExternalLinksTracker = {
    init: function() {
      $('a[rel=external]').each(function() {
        $(this).data('ExternalLinksTracker', new ExternalLinksTracker($(this), $(this).data()));
      });
    }
  };
}());
/**
 * Page exit prompt
 *
 * Prompts the user upon leaving the page if they have changed
 * any data in any form.
 */

(function(){
  'use strict';

  window.moj = window.moj || { Modules: {}, Events: $({}) };

  var PromptOnChange = function(options) {
    this.init(options);
    return this;
  };

  PromptOnChange.prototype = {
    defaults: {
      message: "You have entered some information"
    },

    init: function(options) {
      this.settings = $.extend({}, this.defaults, options);
      this.enable();
      this.initMetaRefresh();
      this.hashedFields = this.hashFields();
      this.bindEvents();
    },

    bindEvents: function() {
      var self = this;

      $('form').on('submit', function() {
        self.disable();
      });

      $(window).on('beforeunload', function() {
        return self.runCheck();
      });
    },

    hashFields: function() {
      return $('form').serialize();
    },

    fieldsHaveChanged: function() {
      return this.hashFields() !== this.hashedFields;
    },

    runCheck: function() {
      var self = this;

      if (this.isEnabled && this.fieldsHaveChanged() && this.isMetaRefresh() === false) {
        return self.settings.message;
      }
    },

    enable: function() {
      this.isEnabled = true;
    },

    disable: function() {
      this.isEnabled = false;
    },

    isMetaRefresh: function() {      
      if (typeof this.metaRefreshAt !== 'undefined') {
        var now = new Date().getTime();
        
        if (now >= this.metaRefreshAt) {
          return true;
        }
      }

      return false;
    },

    initMetaRefresh: function() {
      var refreshTag = $('head').find('meta[http-equiv=refresh]');
      
      if (refreshTag.length) {
        var refreshTimeoutLength = parseInt(refreshTag.attr('content').match(/^\d*/)[0]);
        var now = new Date().getTime();
        
        this.metaRefreshAt = now + ((refreshTimeoutLength-1)*1000);
      }
    }
  };

  moj.Modules._PromptOnChange = PromptOnChange;
  
  moj.Modules.PromptOnChange = {
    init: function() {
      var options = {
        message: $('[name=promptOnChangeMessage]').val() || "You have entered some information"
      };
      return new PromptOnChange(options);
    }
  };

}());
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
$(document).ready(function () {
    jQuery.fx.off = true;

    var selectionButtons = new GOVUK.SelectionButtons($("label input[type='radio'], label input[type='checkbox']"));

    $('[name^=nojs]').remove();
});