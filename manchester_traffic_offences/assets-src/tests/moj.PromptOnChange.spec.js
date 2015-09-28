describe("moj.PromptOnChange", function() {
	var $fixture = $(
      '<div class="test_control">' +
        '<form class="test_control">' +
          '<input name="testField" type="text" value="test value" />' +
        '</form>' +
      '</div>'
    ),
    subject;

	beforeAll(function() {
		$fixture.clone().appendTo('body');
		subject = new moj.Modules._PromptOnChange();
	});

	afterAll(function() {
		$('.test_control').remove();
	});

	it("should be instantiated as an object", function() {
		expect(typeof subject).toBe('object');
	});

	it("should return defaults when no options are specified", function() {
    expect(JSON.stringify(subject.settings)).toBe(JSON.stringify(subject.defaults));
  });

	it("should create a hash of the form fields on load", function() {
		expect(subject.hashedFields).toBe('testField=test+value');
	});

	it("should check if fields have changed when an attempt to leave the page is made", function() {
		spyOn(subject, 'runCheck');
		// Mock the beforeunload event bind...
		$(window).trigger('mock.beforeunload');
		expect(subject.runCheck).toHaveBeenCalled();
	});

	it("should not prompt the user if the fields have not changed", function() {
		expect(subject.runCheck()).toBeUndefined();
	});

	it("should prompt the user if the fields have been changed", function() {
		$('[name=testField]').val('some other value');
		expect(subject.runCheck()).toBe('You have entered some information');
	});

  it("should set to disabled when a form is submitted", function() {
  	$('form').on('submit', function(e) {
  		e.preventDefault();
  	}).trigger('submit');
  	expect(subject.isEnabled).toBe(false);
  	expect(subject.runCheck()).toBeUndefined();
  });

	it("should update the prompt message default if a new one is specified as an option", function() {
    $('.test_control').remove();
    $fixture.clone().append('<input type="hidden" name="promptOnChangeMessage" value="New message">').appendTo('body');
    var options = {
      message: $('[name=promptOnChangeMessage]').val() || "You have entered some information"
    };
		subject = new moj.Modules._PromptOnChange(options);
		expect(subject.settings.message).toBe('New message');

		$('[name=testField]').val('some other value');
		expect(subject.runCheck()).toBe('New message');
	});

  it('should be able to get Refresh and Date HTTP headers', function() {
    expect(subject.refreshHeader).toBe(null);
    expect(subject.dateHeader).toBeDefined();
  });

  it("should set the page refresh time to false if the refresh header is not present", function() {
    expect(subject.getRefreshTime()).toBe(false);
  });

  it("should set the page refresh time if the refresh header is present", function() {
    // Fake headers
    var refresh = '60';
    var date = new Date();

    subject.refreshHeader = refresh;
    subject.dateHeader = date;

    subject.sessionRefreshAt = subject.getRefreshTime();

    expect(subject.sessionRefreshAt).toEqual((Math.floor(date.getTime() / 1000)) + 60);
  });

  it('should be disabled when the page is refreshed using a meta refresh tag', function() {
    jasmine.clock().install();
    jasmine.clock().mockDate();

    $('[name=testField]').val('some other value');
    expect(subject.runCheck()).toBe("New message");
    jasmine.clock().tick(61*1000);
    expect(subject.runCheck()).toBeUndefined();

    jasmine.clock().uninstall();
  });

});
