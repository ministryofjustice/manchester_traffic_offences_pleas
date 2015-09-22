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
