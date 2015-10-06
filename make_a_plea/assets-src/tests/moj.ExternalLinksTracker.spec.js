describe("moj.ExternalLinksTracker", function() {
  var $fixture, subject;

  $fixture = $(
    '<div class="test_controls">' +
      '<a id="internal" href="/">Internal link</a>' +
      '<a id="external" rel="external" href="http://www.example.com">External same window</a>' +
      '<a id="external_new_window" rel="external" href="http://www.example.com" target="_blank">External new window</a>' +
    '</div>'
  );

  describe("without Google Analytics available", function() {
    beforeAll(function() {
      $fixture.appendTo('body');
      subject = new moj.Modules._ExternalLinksTracker($('a[rel=external]'));
    });

    afterAll(function() {
      $('.test_controls').remove();
    });

    it("should bail on init", function() {
      spyOn(subject, "cacheElements");
      spyOn(subject, "bindEvents");

      expect(subject.settings).toBeUndefined();
      expect(subject.cacheElements).not.toHaveBeenCalled();
      expect(subject.bindEvents).not.toHaveBeenCalled();
    });
  });

  describe("with Google Analytics available", function() {
    beforeEach(function() {
      // Fake Google Analytics
      ga = function(a, b, c, d, e, f) {
        if (f.hasOwnProperty("hitCallback") && typeof f.hitCallback === "function") {
          f.hitCallback();
        }
      };

      $fixture.appendTo('body');
      subject = new moj.Modules._ExternalLinksTracker($('a[rel=external]'));
    });

    afterEach(function() {
      $('.test_controls').remove();
    });

    it("should be an object", function() {
      expect(typeof subject).toBe('object');
    });

    it('should use defaults when no options are specified', function() {
      expect(JSON.stringify(subject.settings)).toBe(JSON.stringify(subject.defaults));
    });

    it("should cache elements", function() {
      expect(subject.$links.length).toBe(2);
    });

    it("should accept options", function() {
      var options = {
        "eventCategory": "test",
        "eventAction": "testAlso"
      };
      subject = new moj.Modules._ExternalLinksTracker($('a[rel=external]'), options);

      expect(subject.settings).toEqual(options);
    });

    it("should send GA event when an external link is clicked", function() {
      spyOn(subject, "sendGAEvent");
      $("#external").click();

      expect(subject.sendGAEvent).toHaveBeenCalled();
    });

    it("should open the link once event is sent", function() {
      spyOn(subject, "openLink");

      $("#external").click();
      expect(subject.openLink).toHaveBeenCalledWith("http://www.example.com", undefined);

      $("#external_new_window").click();
      expect(subject.openLink).toHaveBeenCalledWith("http://www.example.com", "_blank");
    });
  });
});
