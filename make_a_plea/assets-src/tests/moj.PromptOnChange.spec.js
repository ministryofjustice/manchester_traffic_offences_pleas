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
    jasmine.clock().uninstall();
		$fixture.clone().appendTo('body');
		subject = new moj.Modules._PromptOnChange();
	});

	afterAll(function() {
		$('.test_control').remove();
	});

	it("should be instantiated as an object", function() {
		expect(typeof subject).toBe('object');
	});

	it("should create a hash of the form fields on load", function() {
		expect(subject.currentHash).toBe('testField=test+value');
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

  it("should not prompt the user when a form is submitted", function() {
  	$('form').on('submit', function(e) {
  		e.preventDefault();
  	}).trigger('submit');

    expect(subject.isEnabled).toBe(false);
  	expect(subject.runCheck()).toBeUndefined();
  });

  it("should update the prompt message if promptOnChangeMessage is defined", function() {
    $('.test_control').remove();
    $fixture.clone().append('<script>var promptOnChangeMessage = "New message";</script>').appendTo('body');
    subject = new moj.Modules._PromptOnChange();

    expect(subject.message).toBe('New message');

    $('[name=testField]').val('some other value');
    expect(subject.runCheck()).toBe('New message');
  });

  it("should update the sessionTimeout setting if it is defined", function() {
    var pageLoadTime = Math.floor(new Date().getTime() / 1000);
    var sessionTimeout = pageLoadTime + 60;

    $('.test_control').remove();
    $fixture.clone().append('<script>var sessionTimeout = ' + sessionTimeout + ';</script>').appendTo('body');
    moj.init();
    subject = new moj.Modules._PromptOnChange();

    expect(subject.sessionTimeout).toBe(sessionTimeout);
  });

  it("should not prompt the user when the page is refreshed due to a session timeout redirect", function() {
    jasmine.clock().install();
    jasmine.clock().mockDate();

    $('[name=testField]').val('yet another value');

    expect(subject.isSessionTimeoutRedirect()).toBe(false);
    expect(subject.runCheck()).toBe('New message');

    jasmine.clock().tick(60*1000);

    expect(subject.isSessionTimeoutRedirect()).toBe(true);
    expect(subject.runCheck()).toBeUndefined();

    jasmine.clock().uninstall();
  });

});
