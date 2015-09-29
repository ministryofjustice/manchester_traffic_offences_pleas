describe("moj.SelectionButtons", function() {
  // Remove moj.js log message for cleaner console output
  moj.Modules.devs = {};

  var $fixture = $(
        '<div class="test_control">' +
          '<form id="test-form">' +
            '<label id="label1"><input id="radio1" type="radio" name="radio"></label>' +
            '<label id="label2"><input id="radio2" type="radio" name="radio"></label>' +
            '<label id="label3"><input id="radio3" type="radio" name="radio"></label>' +
            '<label id="label4"><input id="checkbox1" type="checkbox" name="checkbox"></label>' +
          '</form>' +
        '</div>'
      );

  beforeAll(function() {
    $fixture.clone().appendTo('body');
    moj.init();
  });

  afterAll(function() {
    $('.test_control').remove();
  });

  describe("focus and blur events", function() {
    it("should add the 'focused' class to the label around a focused element", function() {
      $('#radio1').focus();
      expect($('#label1').hasClass('focused')).toBe(true);
    });

    it("should remove the 'focused' class from the label on blur", function() {
      $('#radio1').bind('oasis', function() {
        return $(this).blur();
      }).trigger('oasis');
      expect($('#label2').hasClass('focused')).toBe(false);
    });
  });

  describe("change event", function() {
    it("should add the 'selected' class to the label around a selected element", function() {
      $('#radio1').click();
      expect($('#label1').hasClass('selected')).toBe(true);

      $('#checkbox1').prop('checked', true).trigger('change');
      expect($('#label4').hasClass('selected')).toBe(true);
    });

    it("should remove the 'selected' class from other radio buttons labels when one is selected", function() {
      $('#radio2').click();
      expect($('#label1').hasClass('selected')).toBe(false);
    });

    it("should remove the 'selected' class from the label on uncheck", function() {
      $('#checkbox1').removeProp('checked').trigger('change');
      expect($('#label4').hasClass('selected')).toBe(false);
    });
  });
});
