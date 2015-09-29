describe("moj.TemplatedElement", function() {
  var $fixture = $(
      '<div class="test_control">' +
      ' <label><input id="radio_1" name="testField" type="radio" value="one"/> One</label>' +
      ' <label><input id="radio_2" name="testField" type="radio" value="two"/> Two</label>' +
      ' <label><input id="radio_3" name="testField" type="radio" value="three"/> Three (ignored)</label>' +
      ' <div id="templated" data-template="Templated content, value = {value}" data-template-trigger="testField" data-template-defaults-for="Three (ignored)">Default content</div>' +
      '</div>'
  ),
  subject;

	beforeAll(function() {
    $fixture.clone().appendTo('body');
    subject = new moj.Modules._TemplatedElement($('[data-template]'));
  });

  afterAll(function() {
    $('.test_control').remove();
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

  it("should cache the original text, trigger, template, and defaultsFor", function() {
    expect(subject.originalText).toBe('Default content');
    expect(subject.trigger).toBe('testField');
    expect(subject.template).toBe('Templated content, value = {value}');
    expect(subject.defaultsFor).toBe('Three (ignored)');
  });

  it("should cache values that call for the original text", function() {
    expect(subject.defaultsFor).toBe('Three (ignored)');
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

  it("should populate the element with the templated text if the value isn't excluded", function() {
    $('#radio_1').trigger('click');
    expect($('#templated').text()).toBe('Templated content, value = one');
    $('#radio_2').trigger('click');
    expect($('#templated').text()).toBe('Templated content, value = two');
  });

  it("should render the template with the value of the data-value attribute instead of the value one if one is specified", function() {
    $('#radio_1').attr('data-template-value', 'One (from data attribute)').trigger('click');
    expect($('#templated').text()).toBe('Templated content, value = one (from data attribute)');
  });

  it("should populate the element with the original text if the value is excluded", function() {
    $('#radio_3').trigger('click');
    expect($('#templated').text()).toBe('Default content');
  });

  it("should use options provided if the data attributes are missing", function() {
    var options = {
      trigger: 'testField',
      template: 'Templated content, value = {value}',
      defaultsFor: 'Three (ignored)'
    };

    $('.test_control').remove();
    $fixture = $(
      '<div class="test_control">' +
      ' <label><input id="radio_1" name="testField" type="radio" value="one"/> One</label>' +
      ' <label><input id="radio_2" name="testField" type="radio" value="two"/> Two</label>' +
      ' <label><input id="radio_3" name="testField" type="radio" value="three"/> Three (ignored)</label>' +
      ' <div class="js-TemplatedElement">Default content</div>' +
      '</div>'
    );
    $fixture.appendTo('body');
    subject = new moj.Modules._TemplatedElement($('.js-TemplatedElement'), options);

    expect(subject.originalText).toBe('Default content');
    expect(subject.trigger).toBe('testField');
    expect(subject.template).toBe('Templated content, value = {value}');
    expect(subject.defaultsFor).toBe('Three (ignored)');
  });

  it('should delegate functionality to the contents of another element if the delegate attribute is set', function() {
    $('.test_control').remove();
    $fixture = $(
      '<div class="test_control">' +
      ' <label><input id="radio_1" name="testField" type="radio" value="one"/> One</label>' +
      ' <label><input id="radio_2" name="testField" type="radio" value="two"/> Two</label>' +
      ' <label><input id="radio_3" name="testField" type="radio" value="three"/> Three (ignored)</label>' +
      ' <div data-template="Templated content, value = {value}" data-template-trigger="testField" data-template-defaults-for="Three (ignored)" data-template-delegate="#delegate">Default content</div>' +
      ' <div id="delegate">Another element</div>' +
      '</div>'
    );
    $fixture.appendTo('body');
    subject = new moj.Modules._TemplatedElement($('[data-template]'));

    expect(subject.$element.attr('id')).toBe('delegate');
    expect(subject.originalText).toBe('Another element');

    $('#radio_1').trigger('click');
    expect($('#delegate').text()).toBe('Templated content, value = one');
  });

  it('should use the default text from the first element only', function() {
    $('.test_control').remove();
    $fixture = $(
      '<div class="test_control">' +
      ' <label><input id="radio_1" name="testField" type="radio" value="one"/> One</label>' +
      ' <label><input id="radio_2" name="testField" type="radio" value="two"/> Two</label>' +
      ' <div data-template="Templated content, value = {value}" data-template-trigger="testField" data-template-defaults-for="Two" data-template-delegate=".delegate">Default content</div>' +
      ' <div class="delegate">Another element</div>' +
      ' <div class="delegate">Yet another element</div>' +
      '</div>'
    );
    $fixture.appendTo('body');
    subject = new moj.Modules._TemplatedElement($('[data-template]'));

    expect(subject.originalText).toBe('Another element');
  });
});
