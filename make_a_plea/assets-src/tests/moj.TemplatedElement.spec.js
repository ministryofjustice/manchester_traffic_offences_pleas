describe("moj.TemplatedElement", function() {
  var $fixture = $(
      '<div class="test_control">' +
      ' <label><input id="radio_1" name="testField" type="radio" value="one"/> One</label>' +
      ' <label><input id="radio_2" name="testField" type="radio" value="two"/> Two</label>' +
      ' <label><input id="radio_3" name="testField" type="radio" value="three"/> Three</label>' +
      ' <div id="templated">Default content</div>' +
      '</div>'
  ),
  subject,
  options = {
    "trigger": "[name=testField]",
    "templates": {
      "one": "Templated content, value = one",
      "two": "Templated content, value = two"
    }
  };

	beforeAll(function() {
    $fixture.clone().appendTo('body');
    subject = new moj.Modules._TemplatedElement($('#templated'), options);
  });

  afterAll(function() {
    $('.test_control').remove();
  });

  it("should be an instantiated object", function() {
    expect(typeof subject).toBe('object');
  });

  it("should cache elements", function() {
    expect(subject.$element.length).toBe(1);
    expect(subject.$inputs.length).toBe(3);
  });

  it("should cache the original text and the trigger selector", function() {
    expect(subject.originalText).toBe('Default content');
    expect(subject.trigger).toBe('[name=testField]');
  });

  it("should call updateText() when the field change event is fired", function() {
    spyOn(subject, 'updateText');
    $('[name=testField]').trigger('change');
    expect(subject.updateText).toHaveBeenCalled();
  });

  it("should call updateText() when moj.init() is fired", function() {
    spyOn(subject, 'updateText');
    moj.init();
    expect(subject.updateText).toHaveBeenCalled();
  });

  it("should populate the element with the relevant text if there is a template for the given value", function() {
    $('#radio_1').trigger('click');
    expect($('#templated').text()).toBe('Templated content, value = one');
    $('#radio_2').trigger('click');
    expect($('#templated').text()).toBe('Templated content, value = two');
  });

  it("should populate the element with the original text if the value doesn't have a template assigned", function() {
    $('#radio_3').trigger('click');
    expect($('#templated').text()).toBe('Default content');
  });

  it('should use the default text from the first element only', function() {
      $('.test_control').remove();
      $fixture = $(
        '<div class="test_control">' +
        ' <label><input id="radio_1" name="testField" type="radio" value="one"/> One</label>' +
        ' <label><input id="radio_2" name="testField" type="radio" value="two"/> Two</label>' +
        ' <div class="templated">Default content</div>' +
        ' <div class="templated">Different content</div>' +
        '</div>'
      );
      $fixture.appendTo('body');
      subject = new moj.Modules._TemplatedElement($('.templated'), options);

      expect(subject.originalText).toBe('Default content');
    });

});
