describe("moj.PromptOnChange", function() {
	var $fixture, subject;

	beforeEach(function() {
		$fixture = $(
			'<form>'
        + '<input name="testField" type="text" value="test value" />'
      + '</form>'
    );
		$fixture.appendTo('body');
		subject = new moj.Modules._PromptOnChange();
	});

	afterEach(function() {
		$('body').find('form').remove();
	});



	it('should be instantiated as an object', function() {
		expect(typeof subject).toBe('object');
	});

	it('should return defaults when no options are specified', function() {
    expect(JSON.stringify(subject.settings)).toBe(JSON.stringify(subject.defaults));
  });

	it('should create a hash of the form fields on load', function() {
		moj.Events.trigger('render');
		expect(subject.hashedFields).toBe('testField=test+value');
	});

	it('should check if fields have changed when an attempt to leave the page is made', function() {
		spyOn(subject, 'runCheck');
		// Mock the beforeunload event bind...
		$(window).on('leaving_the_page', function() {
			subject.runCheck();
		}).trigger('leaving_the_page');
		expect(subject.runCheck).toHaveBeenCalled();
	});

	it('should not prompt the user if the fields have not changed', function() {
		expect(subject.runCheck()).toBeUndefined();
	});

	it('should prompt the user if the fields have been changed', function() {
		$('[name=testField]').val('some other value');
		expect(subject.runCheck()).toBe('You have entered some information');
	});

  it('should set to disabled if a form is submitted', function() {
  	$('form').on('submit', function(e) {
  		e.preventDefault();
  	}).trigger('submit');
  	expect(subject.isEnabled).toBe(false);
  	expect(subject.runCheck()).toBeUndefined();
  });

	it('should update the prompt message default if a new one is specified as an option', function() {
		subject = new moj.Modules._PromptOnChange({message: 'New message'});
		expect(subject.settings.message).toBe('New message');
		
		$('[name=testField]').val('some other value');
		expect(subject.runCheck()).toBe('New message');
	});

});