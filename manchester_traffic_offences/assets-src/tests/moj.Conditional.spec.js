describe("moj.Conditional", function() {
	var $fixture = $(
    '<div class="test_control">' +
      '<input id="radio_1" type="radio" name="trigger_name" value="regex">' +
      '<input id="radio_2" type="radio" name="trigger_name" value="another value" aria-controls="test">' +
      '<input id="radio_3" type="radio" name="trigger_name" value="yet another value" aria-controls="target_1">' +
      '<div id="target_1" data-conditional="trigger_name" data-conditional-value="^regex$">...</div>' +
    '</div>'
  );
  var subject;

  beforeAll(function() {
    $fixture.appendTo('body');
    subject = new moj.Modules._Conditional($('[data-conditional]'));
  });

  afterAll(function() {
    $fixture.remove();
  });

  it("should be an object", function() {
    expect(typeof subject).toBe('object');
  });

  it("should cache elements", function() {
    expect(subject.$conditional.length).toBe(1);
    expect(subject.$inputs.length).toBe(3);
  });

  it("should call toggle() when moj.init() is fired", function() {
    spyOn(subject, 'toggle');
    moj.init();
    expect(subject.toggle).toHaveBeenCalled();
  });

  it("should add ARIA attributes", function() {
    expect($('#radio_1').attr('aria-controls')).toBe('target_1');
    expect($('#target_1').attr('aria-expanded')).toBe('false');
    expect($('#target_1').attr('aria-live')).toBe('polite');
  });

  it("should not remove existing ARIA attributes if they are already set", function() {
    expect($('#radio_2').attr('aria-controls')).toBe('test target_1');
  });

  it("should only add ARIA attributes if they don't exist", function() {
    expect($('#radio_3').attr('aria-controls')).toBe('target_1');
  });

  it("should not show the conditional if no input is checked", function() {
    expect($('#target_1')).toBeHidden();
  });

  it("should call toggle() when the input's change event is fired", function() {
    spyOn(subject, 'toggle');
    subject.$inputs.trigger('change');
    expect(subject.toggle).toHaveBeenCalled();
  });

  it("should show the conditional if the value matches", function() {
    $('#radio_1').trigger('click');
    expect($('#target_1')).toBeVisible();
    expect($('#target_1').attr('aria-expanded')).toBe('true');
    expect($('#target_1').attr('aria-hidden')).toBeUndefined();
    expect($('#target_1').prop('hidden')).toBe(false);
  });

  it("should hide the conditional if the value doesn't match", function() {
    $('#radio_2').trigger('click');
    expect($('#target_1')).toBeHidden();
    expect($('#target_1').attr('aria-expanded')).toBe('false');
    expect($('#target_1').attr('aria-hidden')).toBe('true');
    expect($('#target_1').prop('hidden')).toBe(true);
  });

});
