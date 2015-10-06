/**
 * Page exit prompt
 *
 * Prompts the user upon leaving the page if they have changed
 * any data in any form.
 *
 * To set an alternative message or a session timeout timestamp
 * (after which the prompt will be disabled), declare the following
 * variables somewhere in the markup:
 *
 * <script>
 *   var promptOnChangeMessage = "Alternative message";
 *   var sessionTimeout = 123456789;
 * </script>
 */

(function(){
  'use strict';

  window.moj = window.moj || { Modules: {}, Events: $({}) };

  var PromptOnChange = function() {
    this.init();
    return this;
  };

  PromptOnChange.prototype = {
    init: function() {
      this.message = "You have entered some information";
      this.sessionTimeout = false;

      if (typeof promptOnChangeMessage === 'string') {
        this.message = promptOnChangeMessage;
      }
      if (typeof sessionTimeout === 'number') {
        this.sessionTimeout = sessionTimeout;
      }

      this.currentHash = this.hashFields();
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
      return this.hashFields() !== this.currentHash;
    },

    runCheck: function() {
      if (this.isSessionTimeoutRedirect()) {
        this.disable();
      }

      if (this.isEnabled && this.fieldsHaveChanged()) {
        return this.message;
      }
    },

    enable: function() {
      this.isEnabled = true;
    },

    disable: function() {
      this.isEnabled = false;
    },

    isSessionTimeoutRedirect: function() {
      if (this.sessionTimeout) {
        var now = Math.floor(new Date().getTime() / 1000);

        if (now >= this.sessionTimeout) {
          return true;
        }
      }

      return false;
    }
  };

  moj.Modules._PromptOnChange = PromptOnChange;

  moj.Modules.PromptOnChange = {
    init: function() {
      return new PromptOnChange();
    }
  };

}());
