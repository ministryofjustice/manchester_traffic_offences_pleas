class CommonPage < SitePrism::Page
  element :h1, 'h1'
  element :h2, 'h2'
  element :label, '.label-text'
  section :error_summary, '.error-summary' do
    elements :h1, 'h1'
    elements :p, 'p'
    elements :link, 'li > a'
  end
  element :button, '.button'
  element :help_image, '.help-image'
end
