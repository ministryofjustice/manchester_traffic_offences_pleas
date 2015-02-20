describe("moj.Conditional", function() {
	var $fixture, subject;

	beforeEach(function() {
		$fixture = $(
      '<div class="test_control">'
      + '<input id="radio_1" type="radio" name="trigger_name" value="regex">'
      + '<input id="radio_2" type="radio" name="trigger_name" value="another value">'
      + '<div class="js-Conditional" id="target_1" data-conditional-trigger="trigger_name" data-conditional-value="^regex$">...</div>'
      + '</div>'
		);
    $fixture.appendTo('body');
    subject = new moj.Modules._Conditional($('.js-Conditional'));
	});

  afterEach(function() {
    $('body').find('.test_control').remove();
  });


  it("should be an object", function() {
    expect(typeof subject).toBe('object');
  });

  it("should cache elements", function() {
    expect(subject.$conditional.length).toBe(1);
    expect(subject.$inputs.length).toBe(2);
  });

  it("should add ARIA attributes to the inputs", function() {
    expect(subject.$inputs.attr('aria-controls')).toBeDefined();
  });

  it("should call toggle() when the input's change event is fired", function() {
    spyOn(subject, 'toggle');
    subject.$inputs.trigger('change');
    expect(subject.toggle).toHaveBeenCalled();
  });

  it("should call toggle() when moj.Events' render even is fired", function() {
    spyOn(subject, 'toggle');
    moj.Events.trigger('render');
    expect(subject.toggle).toHaveBeenCalled();
  });

  it("should not show the conditional if no input is checked", function() {
    moj.Events.trigger('render');
    expect($('.js-Conditional')).toBeHidden();
  });
  
  it("should show the conditional if the value matches", function() {
    $('#radio_1').trigger('click');
    expect($('.js-Conditional')).toBeVisible();
    expect($('.js-Conditional').attr('aria-expanded')).toBe('true');
    expect($('.js-Conditional').attr('aria-hidden')).toBe('false');
  });

  it("should hide the conditional if the value doesn't match", function() {
    $('#radio_2').trigger('click');
    expect($('.js-Conditional')).toBeHidden();
    expect($('.js-Conditional').attr('aria-expanded')).toBe('false');
    expect($('.js-Conditional').attr('aria-hidden')).toBe('true');
  });

});