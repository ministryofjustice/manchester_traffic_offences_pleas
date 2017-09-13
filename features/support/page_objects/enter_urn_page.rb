class EnterUrnPage < SitePrism::Page
  set_url '/plea/enter_urn'

  element :page_header, 'h1'

  section :section_urn, '#section_urn' do
    element :text, '#section_urn > label > span.label-text'
    element :hint, '#section_urn > label > span.form-hint'
    element :urn_field, '#id_urn'
  end

  element :continue_button, '.form-submit button'

  def load_page(page_version = nil)
    load(v: page_version)
  end
end
