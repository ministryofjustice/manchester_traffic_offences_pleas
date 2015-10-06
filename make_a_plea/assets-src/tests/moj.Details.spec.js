describe("moj.Details", function() {
	var $fixture = $(
        '<div id="fixture_1" class="test_control">' +
          '<div class="js-Details">' +
            '<a class="details-trigger" href="#details-content"><span class="summary">View details</span></a>' +
            '<div class="details-content" id="details-content">Content</div>' +
          '</div>' +
        '</div>' +

        '<div id="fixture_2" class="test_control">' +
          '<div class="js-Details open">' +
            '<a class="details-trigger" href="#details-content"><span class="summary">View details</span></a>' +
            '<div class="details-content" id="details-content">Content</div>' +
          '</div>' +
        '</div>' +

        '<div id="fixture_3" class="test_control">' +
          '<div class="js-Details" data-summary-open="Alternative text">' +
            '<a class="details-trigger" href="#details-content"><span class="summary">View details</span></a>' +
            '<div class="details-content" id="details-content">Content</div>' +
          '</div>' +
        '</div>'
      ),
      subject;

  beforeAll(function() {
    $fixture.appendTo('body');
    subject = new moj.Modules._Details($('#fixture_1 .js-Details'));
    moj.init();
  });

  afterAll(function() {
    $('.test_control').remove();
  });

  describe("default setup", function() {
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
      expect($('#fixture_1').find('.details-trigger').attr('role')).toBe('button');
      expect($('#fixture_1').find('.details-trigger').attr('aria-controls')).toBe('details-content');
      expect($('#fixture_1').find('.details-trigger').attr('aria-expanded')).toBe('false');

      expect($('#fixture_1').find('.details-content').attr('id')).toBeDefined('details-content');
      expect($('#fixture_1').find('.details-content').attr('aria-live')).toBe('polite');
    });

    it("should hide the content to start with", function() {
      expect($('#fixture_1').find('.details-content')).toBeHidden();
      expect($('#fixture_1').find('.details-content').attr('aria-hidden')).toBe('true');
      expect($('#fixture_1').find('.details-content').prop('hidden')).toBe(true);
    });

    it("should show the content when summary is clicked", function() {
      $('#fixture_1').find('.details-trigger').click();
      expect($('#fixture_1').find('.details-content')).toBeVisible();
      expect($('#fixture_1').find('.details-trigger').attr('aria-expanded')).toBe('true');
      expect($('#fixture_1').find('.details-content').attr('aria-hidden')).toBeUndefined();
      expect($('#fixture_1').find('.js-Details').hasClass('open')).toBe(true);
    });

    it("should hide the content when clicked again", function() {
      $('#fixture_1').find('.details-trigger').click();
      expect($('#fixture_1').find('.details-content')).toBeHidden();
      expect($('#fixture_1').find('.details-trigger').attr('aria-expanded')).toBe('false');
      expect($('#fixture_1').find('.details-content').attr('aria-hidden')).toBe('true');
      expect($('#fixture_1').find('.details-content').prop('hidden')).toBe(true);
      expect($('#fixture_1').find('.js-Details').hasClass('open')).toBe(false);
    });
  });

  describe("already open setup", function() {
    it("should add ARIA attributes to the elements", function() {
      expect($('#fixture_2').find('.details-trigger').attr('aria-expanded')).toBe('true');
      expect($('#fixture_2').find('.details-content').attr('aria-hidden')).toBeUndefined();
    });

    it("should show the content to start with", function() {
      expect($('#fixture_2').find('.details-content')).toBeVisible();
    });

    it("should hide the content when summary is clicked", function() {
      $('#fixture_2').find('.details-trigger').click();
      expect($('#fixture_2').find('.details-content')).toBeHidden();
      expect($('#fixture_2').find('.details-trigger').attr('aria-expanded')).toBe('false');
      expect($('#fixture_2').find('.details-content').attr('aria-hidden')).toBe('true');
      expect($('#fixture_2').find('.details-content').prop('hidden')).toBe(true);
      expect($('#fixture_2').find('.js-Details').hasClass('open')).toBe(false);
    });

    it("should show the content when clicked again", function() {
      $('#fixture_2').find('.details-trigger').click();
      expect($('#fixture_2').find('.details-content')).toBeVisible();
      expect($('#fixture_2').find('.details-trigger').attr('aria-expanded')).toBe('true');
      expect($('#fixture_2').find('.details-content').attr('aria-hidden')).toBeUndefined();
      expect($('#fixture_2').find('.js-Details').hasClass('open')).toBe(true);
    });
  });

  describe("alternative text setup", function() {
    it("should change the text when open", function() {
      $('#fixture_3').find('.details-trigger').click();
      expect($('#fixture_3').find('.details-trigger .summary').text()).toBe("Alternative text");
    });

    it("should revert to original text when clicked again", function() {
      $('#fixture_3').find('.details-trigger').click();
      expect($('#fixture_3').find('.details-trigger .summary').text()).toBe("View details");
    });
  });

});
