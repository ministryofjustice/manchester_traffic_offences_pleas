class CommonPage < SitePrism::Page
  section :content_header, '.content-header' do
    element :h1, 'h1'
    element :p, 'p'
  end
  element :h2, 'h2'
  elements :label_text, '.label-text'
  elements :form_hint, '.form-hint'
  section :error_summary, '.error-summary' do
    elements :h1, 'h1'
    elements :p, 'p'
    elements :link, 'li > a'
  end
  element :button, '.button'
  element :help_image, '.help-image'
end
