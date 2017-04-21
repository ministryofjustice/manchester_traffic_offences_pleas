class YourCasePage < BasePage
  set_url '/plea/enter_urn/'

  section :content, 'content' do
    element :page_header, 'h1'
  end
end