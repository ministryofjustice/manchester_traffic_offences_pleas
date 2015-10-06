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
