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
      this.hashedFields = this.hashFields();
      this.bindEvents();
    },

    bindEvents: function() {
      var self = this;

      $('form').on('submit', function() {
        self.disable();
      });

      $(window).on('beforeunload', function() {
        self.runCheck();
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

      if (this.isEnabled && this.fieldsHaveChanged()) {
        return self.settings.message;
      }
    },

    enable: function() {
      this.isEnabled = true;
    },

    disable: function() {
      this.isEnabled = false;
    }
  };

  moj.Modules._PromptOnChange = PromptOnChange;

  moj.Modules.PromptOnChange = {
    init: function() {
      return new PromptOnChange();
    }
  };

}());