describe("moj.TemplatedElement", function() {
  var $fixture, subject;

	beforeEach(function() {
    $fixture = $(
      '<div class="test_control">'
      + '<input id="radio_1" name="testField" type="radio" value="one"/>'
      + '<input id="radio_2" name="testField" type="radio" value="two"/>'
      + '<input id="radio_3" name="testField" type="radio" value="three ignored"/>'
      + '<div class="js-TemplatedElement" data-template-trigger="testField" data-template="Templated content, value = {value}" data-template-defaults-for="three ignored">Default content</div>'
      + '</div>'
    );
    $fixture.appendTo('body');
    subject = new moj.Modules._TemplatedElement($('.js-TemplatedElement'));
  });

  afterEach(function() {
    $('body').find('.test_control').remove();
  });

  it("should be an instantiated object", function() {
    expect(typeof subject).toBe('object');
  });

  it('should return defaults when no options are specified', function() {
    expect(JSON.stringify(subject.settings)).toBe(JSON.stringify(subject.defaults));
  });

  it("should cache elements", function() {
    expect(subject.$element.length).toBe(1);
    expect(subject.$inputs.length).toBe(3);
  });

  it("should cache the original text, trigger, template and defaultsFor", function() {
    expect(subject.originalText).toBe('Default content');
    expect(subject.trigger).toBe('testField');
    expect(subject.template).toBe('Templated content, value = {value}');
    expect(subject.defaultsFor).toBe('three ignored');
  });

  it("should cache values that call for the original text", function() {
    expect(subject.defaultsFor).toBe('three ignored');
  });

  it("should call updateText() when the field change event is fired", function() {
    spyOn(subject, 'updateText');
    $('[name=testField]').trigger('change');
    expect(subject.updateText).toHaveBeenCalled();
  });

  it("should call updateText() when moj.Events' render event is fired", function() {
    spyOn(subject, 'updateText');
    moj.Events.trigger('render');
    expect(subject.updateText).toHaveBeenCalled();
  });

  it("should populate the element with the templated text if the value isn't excluded", function() {
    $('#radio_1').trigger('click');
    expect(subject.$element.text()).toBe('Templated content, value = one');
    $('#radio_2').trigger('click');
    expect(subject.$element.text()).toBe('Templated content, value = two');
  });

  it("should populate the element with the original text if the value is excluded", function() {
    $('#radio_3').trigger('click');
    expect(subject.$element.text()).toBe('Default content');
  });

  it("should use options provided if the data attributes are missing", function() {
    var options = {
      trigger: 'testField',
      template: 'Templated content, value = {value}',
      defaultsFor: 'three'
    };

    $('body').find('.test_control').remove();
    $fixture = $(
      '<div class="test_control">'
      + '<input id="radio_1" name="testField" type="radio" value="one"/>'
      + '<input id="radio_2" name="testField" type="radio" value="two"/>'
      + '<input id="radio_3" name="testField" type="radio" value="three"/>'
      + '<div class="js-TemplatedElement">Default content</div>'
      + '</div>'
    );
    subject = new moj.Modules._TemplatedElement($fixture.find('.js-TemplatedElement'), options);

    expect(subject.originalText).toBe('Default content');
    expect(subject.trigger).toBe('testField');
    expect(subject.template).toBe('Templated content, value = {value}');
    expect(subject.defaultsFor).toBe('three');
  });

  it('should delegate functionality to another element if the delegate attribute is set', function() {
    $fixture = $(
      '<div class="test_control">'
      + '<input id="radio_1" name="testField" type="radio" value="one"/>'
      + '<input id="radio_2" name="testField" type="radio" value="two"/>'
      + '<input id="radio_3" name="testField" type="radio" value="three"/>'
      + '<div class="js-TemplatedElement" data-template-trigger="testField" data-template="Templated content, value = {value}" data-template-defaults-for="three" data-template-delegate="#delegate">Default content</div>'
      + '<div id="delegate">Another element</div>'
      + '</div>'
    );
    $fixture.appendTo('body');
    subject = new moj.Modules._TemplatedElement($fixture.find('.js-TemplatedElement'));

    expect(subject.$element.attr('id')).toBe('delegate');
    expect(subject.originalText).toBe('Another element');

    $('#radio_1').trigger('click');
    expect($('#delegate').text()).toBe('Templated content, value = one');
  });
});