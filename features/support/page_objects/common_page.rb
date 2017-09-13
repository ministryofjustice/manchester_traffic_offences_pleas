class CommonPage < SitePrism::Page
  element :h1, 'h1'
  section :error_summary, '.error-summary' do
    elements :h1, 'h1'
    elements :p, 'p'
    elements :link, 'li > a'
  end
end
