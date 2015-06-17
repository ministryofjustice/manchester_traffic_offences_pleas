describe("moj.SelectionButtons", function() {
  var $fixture = $(
        '<form id="test-form">' +
          '<label id="label1"><input id="radio1" type="radio" name="radio"></label>' +
          '<label id="label2"><input id="radio2" type="radio" name="radio"></label>' +
          '<label id="label3"><input id="radio3" type="radio" name="radio"></label>' +
          '<label id="label4"><input id="checkbox1" type="checkbox" name="checkbox"></label>' +
        '</form>'
      ),
      subject;

  beforeAll(function() {
    $fixture.clone().appendTo('body');
    $(moj.init);
  });

  afterAll(function() {
    $('#test-form').remove();
  });


  describe("focus and blur events", function() {
    it("should add the 'focused' class to the label around a focused element", function() {
      $('#radio1').focus();
      expect($('#label1').hasClass('focused')).toBe(true);
    });

    it("should remove the 'focused' class from the label on blur", function() {
      $('#radio1').bind('oasis', function() {
        return $(this).blur();
      });
      $('#radio1').trigger('oasis');
      expect($('#label2').hasClass('focused')).toBe(false);
    });
  });

  describe("change event", function() {
    it("should add the 'selected' class to the label around a selected element", function() {
      $('#radio1').click();
      expect($('#label1').hasClass('selected')).toBe(true);

      $('#checkbox1').click();
      expect($('#label4').hasClass('selected')).toBe(true);
    });

    it("should remove the 'selected' class from other radio buttons labels when one is selected", function() {
      $('#radio2').click();
      expect($('#label1').hasClass('selected')).toBe(false);
    });

    it("should remove the 'selected' class from the label on uncheck", function() {
      $('#checkbox1').click();
      expect($('#label4').hasClass('selected')).toBe(false);
    });
  });
});