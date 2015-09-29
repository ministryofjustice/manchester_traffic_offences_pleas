describe("moj.CalculateTotals", function() {
  var $fixture = $(
      '<div class="test_control">' +
        '<input type="text" class="term" value="10">' +
        '<input type="text" class="term" value="5">' +
        '<input type="text" class="term">' +
        '<span class="term">7</span>' +
        '<div id="total" class="js-CalculateTotals" data-total-terms=".term" data-total-precision="2"></div>' +
      '</div>'
    ),
    subject;

  beforeAll(function() {
    $fixture.appendTo('body');
    subject = new moj.Modules._CalculateTotals($fixture.find('.js-CalculateTotals'));
  });

  afterAll(function() {
    $fixture.remove();
  });

  it("should be an object", function() {
    expect(typeof subject).toBe('object');
  });

  it("should return defaults when no options are specified", function() {
    expect(JSON.stringify(subject.settings)).toBe(JSON.stringify(subject.defaults));
  });

  it("should cache elements", function() {
    expect(subject.$total.length).toBe(1);
    expect(subject.$terms.length).toBe(4);
  });

  it("should call updateTotal() when moj.init() is fired", function() {
    spyOn(subject, 'updateTotal');
    moj.init();
    expect(subject.updateTotal).toHaveBeenCalled();
  });

  it("should call updateTotal() when the change event is fired on any of the terms elements", function() {
    spyOn(subject, 'updateTotal');
    $('.term:first').trigger('change');
    expect(subject.updateTotal).toHaveBeenCalled();
  });

  it("should ignore values which are not numerical", function() {
    $('.term:first').val('aaa').trigger('change');
    expect($('#total').text()).not.toBe('NaN');
  });

  it("should handle numbers with commas", function() {
    $('.term:first').val('1,000,000').trigger('change');
    expect($('#total').text()).toBe('1,000,012.00');
  });

  it("should render large totals with commas", function() {
    $('.term:first').val('1,000,000').trigger('change');
    expect($('#total').text()).toBe("1,000,012.00");
  });

  it("should match the precision set in the attribute", function() {
    $('.test_control').remove();
    $fixture = $(
      '<div class="test_control">' +
        '<input type="text" class="term" value="10">' +
        '<input type="text" class="term" value="5">' +
        '<input type="text" class="term">' +
        '<span class="term">7</span>' +
        '<div id="total" class="js-CalculateTotals" data-total-terms=".term" data-total-precision="4"></div>' +
      '</div>'
    );
    $fixture.appendTo('body');
    moj.init();

    expect($('#total').text()).toBe('22.0000');
  });

  it("should cascade down several totals", function() {
    $('.test_control').remove();
    $fixture = $(
      '<div class="test_control">' +
        '<input type="text" class="term-1" value="10">' +
        '<input type="text" class="term-1" value="10">' +
        '<div class="js-CalculateTotals intermediate-total" data-total-terms=".term-1" data-total-precision="2"></div>' +
      '</div>' +
      '<div class="test_control">' +
        '<input type="text" class="term-2" value="1">' +
        '<input type="text" class="term-2" value="1">' +
        '<div class="js-CalculateTotals intermediate-total" data-total-terms=".term-2" data-total-precision="2"></div>' +
      '</div>' +
      '<div class="test_control">' +
        '<div id="total" class="js-CalculateTotals" data-total-terms=".intermediate-total" data-total-precision="2"></div>' +
      '</div>'
    );
    $fixture.appendTo('body');
    moj.init();

    expect($('.intermediate-total:first').text()).toBe('20.00');
    expect($('.intermediate-total:last').text()).toBe('2.00');
    expect($('#total').text()).toBe('22.00');
  });
});
