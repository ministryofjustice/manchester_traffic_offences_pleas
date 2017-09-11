class CommonPage < BasePage 
  element :h1, 'h1'
  section :error_summary, '.error-summary' do
    elements :h1, 'h1'
    elements :p, 'p'
    element :link, 'a'
  end
end