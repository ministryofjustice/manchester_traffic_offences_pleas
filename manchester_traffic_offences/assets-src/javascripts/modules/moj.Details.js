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
        "aria-hidden": "true",
        "aria-live": "polite"
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
        this.$content.show().removeAttr("aria-hidden").removeProp('hidden');
        this.$icon.removeClass("arrow-closed").addClass("arrow-open").text("\u25bc");

        if (this.openText) {
          this.$summaryText.text(this.openText);
        }
      }
      else {
        this.$summary.attr("aria-expanded", "false");
        this.$content.hide().attr("aria-hidden", "true").prop("hidden", true);
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
