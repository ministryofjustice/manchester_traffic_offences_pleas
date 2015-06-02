/*! http://mths.be/details v0.1.0 by @mathias | includes http://mths.be/noselect v1.0.3 */
;(function(document, $) {

	var proto = $.fn,
	    details,
	    // :'(
	    isOpera = Object.prototype.toString.call(window.opera) == '[object Opera]',
	    // Feature test for native `<details>` support
	    isDetailsSupported = (function(doc) {
	    	var el = doc.createElement('details'),
	    	    fake,
	    	    root,
	    	    diff;
	    	if (!('open' in el)) {
	    		return false;
	    	}
	    	root = doc.body || (function() {
	    		var de = doc.documentElement;
	    		fake = true;
	    		return de.insertBefore(doc.createElement('body'), de.firstElementChild || de.firstChild);
	    	}());
	    	el.innerHTML = '<summary>a</summary>b';
	    	el.style.display = 'block';
	    	root.appendChild(el);
	    	diff = el.offsetHeight;
	    	el.open = true;
	    	diff = diff != el.offsetHeight;
	    	root.removeChild(el);
	    	if (fake) {
	    		root.parentNode.removeChild(root);
	    	}
	    	return diff;
	    }(document)),
	    toggleOpen = function($details, $detailsSummary, $detailsNotSummary, toggle) {
	    	var isOpen = $details.prop('open'),
	    	    close = isOpen && toggle || !isOpen && !toggle;
	    	if (close) {
	    		$details.removeClass('open').prop('open', false).triggerHandler('close.details');
	    		$detailsSummary.attr('aria-expanded', false);
	    		$detailsNotSummary.hide();
	    	} else {
	    		$details.addClass('open').prop('open', true).triggerHandler('open.details');
	    		$detailsSummary.attr('aria-expanded', true);
	    		$detailsNotSummary.show();
	    	}
	    };

	/* http://mths.be/noselect v1.0.3 */
	proto.noSelect = function() {

		// Since the string 'none' is used three times, storing it in a variable gives better results after minification
		var none = 'none';

		// onselectstart and ondragstart for WebKit & IE
		// onmousedown for WebKit & Opera
		return this.bind('selectstart dragstart mousedown', function() {
			return false;
		}).css({
			'MozUserSelect': none,
			'msUserSelect': none,
			'webkitUserSelect': none,
			'userSelect': none
		});

	};

	// Execute the fallback only if there’s no native `details` support
	if (isDetailsSupported) {

		details = proto.details = function() {

			return this.each(function() {
				var $details = $(this),
				    $summary = $('summary', $details).first();
				$summary.attr({
					'role': 'button',
					'aria-expanded': $details.prop('open')
				}).on('click', function() {
					// the value of the `open` property is the old value
					var close = $details.prop('open');
					$summary.attr('aria-expanded', !close);
					$details.triggerHandler((close ? 'close' : 'open') + '.details');
				});
			});

		};

		details.support = isDetailsSupported;

	} else {

		details = proto.details = function() {

			// Loop through all `details` elements
			return this.each(function() {

				// Store a reference to the current `details` element in a variable
				var $details = $(this),
				    // Store a reference to the `summary` element of the current `details` element (if any) in a variable
				    $detailsSummary = $('summary', $details).first(),
				    // Do the same for the info within the `details` element
				    $detailsNotSummary = $details.children(':not(summary)'),
				    // This will be used later to look for direct child text nodes
				    $detailsNotSummaryContents = $details.contents(':not(summary)');

				// If there is no `summary` in the current `details` element…
				if (!$detailsSummary.length) {
					// …create one with default text
					$detailsSummary = $('<summary>').text('Details').prependTo($details);
				}

				// Look for direct child text nodes
				if ($detailsNotSummary.length != $detailsNotSummaryContents.length) {
					// Wrap child text nodes in a `span` element
					$detailsNotSummaryContents.filter(function() {
						// Only keep the node in the collection if it’s a text node containing more than only whitespace
						// http://www.whatwg.org/specs/web-apps/current-work/multipage/common-microsyntaxes.html#space-character
						return this.nodeType == 3 && /[^ \t\n\f\r]/.test(this.data);
					}).wrap('<span>');
					// There are now no direct child text nodes anymore — they’re wrapped in `span` elements
					$detailsNotSummary = $details.children(':not(summary)');
				}

				// Hide content unless there’s an `open` attribute
				$details.prop('open', typeof $details.attr('open') == 'string');
				toggleOpen($details, $detailsSummary, $detailsNotSummary);

				// Add `role=button` and set the `tabindex` of the `summary` element to `0` to make it keyboard accessible
				$detailsSummary.attr('role', 'button').noSelect().prop('tabIndex', 0).on('click', function() {
					// Focus on the `summary` element
					$detailsSummary.focus();
					// Toggle the `open` and `aria-expanded` attributes and the `open` property of the `details` element and display the additional info
					toggleOpen($details, $detailsSummary, $detailsNotSummary, true);
				}).keyup(function(event) {
					if (32 == event.keyCode || (13 == event.keyCode && !isOpera)) {
						// Space or Enter is pressed — trigger the `click` event on the `summary` element
						// Opera already seems to trigger the `click` event when Enter is pressed
						event.preventDefault();
						$detailsSummary.click();
					}
				});

			});

		};

		details.support = isDetailsSupported;

	}

}(document, jQuery));
/**
 * Fallback for browsers not supporting native trim()
 */
if(typeof String.prototype.trim !== 'function') {
  String.prototype.trim = function() {
    return this.replace(/^\s+|\s+$/g, ''); 
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

    $('details').details();

    $('[name^=nojs]').remove();
});