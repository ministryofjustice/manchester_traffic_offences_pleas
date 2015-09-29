describe("moj.FocusHandler", function(){
  // Remove moj.js log message for cleaner console output
  // moj.Modules.devs = {};

  describe("with success headers", function() {
    var $fixture = $(
      '<div class="test_control">' +
      ' <section class="success-header">' +
      '   <h1>Success header</h1>' +
      ' </section>' +
      '</div>'
    );

    beforeAll(function() {
      $fixture.appendTo('body');
      moj.init();
    });

    afterAll(function() {
      $('.test_control').remove();
    });

    it("should add a tabindex attribute to the success header element", function() {
      expect($('.success-header').eq(0).attr('tabindex')).toBe('0');
    });

    it("should focus on the first success header element", function() {
      expect($('.success-header')[0]).toBe(document.activeElement);
    });
  });

  describe("with error summaries", function() {
    var $fixture = $(
      '<div class="test_control">' +
      ' <section class="error-summary">' +
      '   <h1>Error heading</h1>' +
      ' </section>' +
      '</div>'
    );

    beforeAll(function() {
      $fixture.appendTo('body');
      moj.init();
    });

    afterAll(function() {
      $('.test_control').remove();
    });

    it("should add a tabindex attribute to the error element", function() {
      expect($('.error-summary').eq(0).attr('tabindex')).toBe('0');
    });

    it("should focus on the first error summary element", function() {
      expect($('.error-summary')[0]).toBe(document.activeElement);
    });
  });

  describe("with the 'skip to content' link", function() {
    var $fixture = $(
      '<div class="test_control">' +
      ' <a href="#content" class="skiplink">Skip to content</a>' +
      ' <div id="content">Main content</div>' +
      '</div>'
    );

    beforeAll(function() {
      $fixture.appendTo('body');
      moj.init();
    });

    afterAll(function() {
      $('.test_control').remove();
    });

    it("should add a tabindex attribute to the content", function() {
      expect($('#content').attr('tabindex')).toBe('-1');
    });

    it("should set the focus on the main content when clicked", function(){
      $('.skiplink').trigger('click');

      expect($('#content')[0]).toBe(document.activeElement);
    });
  });

  describe("with error links in summary", function() {
    var $fixture = $(
      '<div class="test_control">' +
      ' <section class="error-summary">' +
      '   <h1>Error heading</h1>' +
      '   <ul>' +
      '     <li><a href="#section_1">Error on question 1</a></li>' +
      '     <li><a href="#section_2">Error on question 2</a></li>' +
      '     <li><a href="#section_3">Error on question 3</a></li>' +
      '     <li><a href="#section_4">Error on question 4</a></li>' +
      '   </ul>' +
      ' </section>' +
      ' <form>' +
      '   <section id="section_1">' +
      '     <input id="input_1" type="text" />' +
      '   </section>' +
      '   <section id="section_2">' +
      '     <input id="radio_1" type="radio" name="radio" />' +
      '     <input id="radio_2" type="radio" name="radio" />' +
      '   </section>' +
      '   <section id="section_3">' +
      '     <textarea id="input_3"></textarea>' +
      '   </section>' +
      '   <section id="section_4">' +
      '     <select id="input_4"><option value="">Options one</option></select>' +
      '   </section>' +
      ' </form>' +
      '</div>'
    );

    beforeAll(function() {
      jasmine.clock().install();
      $fixture.appendTo('body');
      moj.init();
    });

    afterAll(function() {
      jasmine.clock().uninstall();
      $('.test_control').remove();
    });

    it("should focus the relevant field when the message is clicked", function() {
      $('a[href=#section_1]').trigger('click');
      jasmine.clock().tick(251);

      expect($('#input_1')[0]).toBe(document.activeElement);
    });

    it("should focus the first field in a group when the message is clicked", function() {
      $('a[href=#section_2]').trigger('click');
      jasmine.clock().tick(251);

      expect($('#radio_1')[0]).toBe(document.activeElement);
    });

    it("should work with textareas", function() {
      $('a[href=#section_3]').trigger('click');
      jasmine.clock().tick(251);

      expect($('#input_3')[0]).toBe(document.activeElement);
    });

    it("should work with select dropdowns", function() {
      $('a[href=#section_4]').trigger('click');
      jasmine.clock().tick(251);

      expect($('#input_4')[0]).toBe(document.activeElement);
    });
  });
});
