describe("moj.Details", function() {
	var $fixture = $(
        '<div class="js-Details">' +
          '<a class="details-trigger" href="#details-content"><span class="summary">View details</span></a>' +
          '<div class="details-content" id="details-content">Content</div>' +
        '</div>'
      ),
      subject;

  describe("default setup", function() {
    beforeAll(function() {
      $fixture.clone().appendTo('body');
      subject = new moj.Modules._Details($('.js-Details'));
    });

    afterAll(function() {
      $('body').find('.js-Details').remove();
    });


    it("should be an object", function() {
      expect(typeof subject).toBe('object');
    });

    it("should cache elements", function() {
      expect(subject.$details.length).toBe(1);
      expect(subject.$summary.length).toBe(1);
      expect(subject.$content.length).toBe(1);
      expect(subject.$icon.length).toBe(1);
    });

    it("should add ARIA attributes to the elements", function() {
      expect($('.details-trigger').attr('role')).toBe('button');
      expect($('.details-trigger').attr('aria-controls')).toBe('details-content');
      expect($('.details-trigger').attr('aria-expanded')).toBe('false');


      expect($('.details-content').attr('id')).toBeDefined('details-content');
      expect($('.details-content').attr('aria-live')).toBe('polite');
    });

    it("should hide the content to start with", function() {
      expect($('.details-content')).toBeHidden();
      expect($('.details-content').attr('aria-hidden')).toBe('true');
      expect($('.details-content').prop('hidden')).toBe(true);
    });

    it("should show the content when summary is clicked", function() {
      $('.details-trigger').click();
      expect($('.details-content')).toBeVisible();
      expect($('.details-trigger').attr('aria-expanded')).toBe('true');
      expect($('.details-content').attr('aria-hidden')).toBeUndefined();
      expect($('.js-Details').hasClass('open')).toBe(true);
    });

    it("should hide the content when clicked again", function() {
      $('.details-trigger').click();
      expect($('.details-content')).toBeHidden();
      expect($('.details-trigger').attr('aria-expanded')).toBe('false');
      expect($('.details-content').attr('aria-hidden')).toBe('true');
      expect($('.details-content').prop('hidden')).toBe(true);
      expect($('.js-Details').hasClass('open')).toBe(false);
    });
  });

  describe("already open setup", function() {
    beforeAll(function() {
      $fixture.clone().appendTo('body');
      $('.js-Details').addClass('open');
      subject = new moj.Modules._Details($('.js-Details'));
    });

    afterAll(function() {
      $('body').find('.js-Details').remove();
    });

    it("should add ARIA attributes to the elements", function() {
      expect($('.details-trigger').attr('aria-expanded')).toBe('true');
      expect($('.details-content').attr('aria-hidden')).toBeUndefined();
    });

    it("should show the content to start with", function() {
      expect($('.details-content')).toBeVisible();
    });

    it("should hide the content when summary is clicked", function() {
      $('.details-trigger').click();
      expect($('.details-content')).toBeHidden();
      expect($('.details-trigger').attr('aria-expanded')).toBe('false');
      expect($('.details-content').attr('aria-hidden')).toBe('true');
      expect($('.details-content').prop('hidden')).toBe(true);
      expect($('.js-Details').hasClass('open')).toBe(false);
    });

    it("should show the content when clicked again", function() {
      $('.details-trigger').click();
      expect($('.details-content')).toBeVisible();
      expect($('.details-trigger').attr('aria-expanded')).toBe('true');
      expect($('.details-content').attr('aria-hidden')).toBeUndefined();
      expect($('.js-Details').hasClass('open')).toBe(true);
    });
  });

  describe("alternative text setup", function() {
    beforeAll(function() {
      $fixture.clone().appendTo('body');
      $('.js-Details').attr("data-summary-open", "Alternative text");
      subject = new moj.Modules._Details($('.js-Details'));
    });

    afterAll(function() {
      $('body').find('.js-Details').remove();
    });

    it("should change the text when open", function() {
      $('.details-trigger').click();
      expect($('.details-trigger .summary').text()).toBe("Alternative text");
    });

    it("should revert to original text when clicked again", function() {
      $('.details-trigger').click();
      expect($('.details-trigger .summary').text()).toBe("View details");
    });
  });

});
