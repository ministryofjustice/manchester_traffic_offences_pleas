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

      this.getRefreshHeaders();
      this.sessionRefreshAt = this.getRefreshTime();

      this.hashedFields = this.hashFields();

      this.bindEvents();
      this.enable();
    },

    bindEvents: function() {
      var self = this;

      $('form').on('submit', function() {
        self.disable();
      });

      // The second event here is used for testing, as there is no
      // other way of mocking a beforeunload event!
      $(window).on('beforeunload mock.beforeunload', function() {
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

      if (this.isMetaRefresh()) {
        this.disable();
      }

      if (this.isEnabled && this.fieldsHaveChanged()) {
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
      if (this.sessionRefreshAt) {
        var now = new Date().getTime() / 1000;

        if (now >= this.sessionRefreshAt) {
          return true;
        }
      }

      return false;
    },

    getRefreshHeaders: function() {
      var request = new XMLHttpRequest();
      request.open('GET', document.location, false);
      request.send(null);

      this.refreshHeader = request.getResponseHeader('Refresh');
      this.dateHeader = request.getResponseHeader('Date');
    },

    getRefreshTime: function() {
      var pageTime;

      if (this.refreshHeader === null) {
        return false;
      }

      if (this.dateHeader !== null) {
        pageTime = new Date(this.dateHeader);
      }
      else {
        pageTime = new Date();
      }

      return Math.floor(pageTime.getTime() / 1000) + parseInt(this.refreshHeader);
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
