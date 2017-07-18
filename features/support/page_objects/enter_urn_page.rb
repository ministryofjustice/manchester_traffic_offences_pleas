class EnterUrnPage < BasePage
  set_url '/plea/enter_urn'

  section :section_urn, '#section_urn' do
    element :text, '#section_urn > label > span.label-text'
    element :hint, '#section_urn > label > span.form-hint'
    element :urn_field, '#id_urn'
  end

  section :error_summary, '.error-summary' do
    element :link, 'a'
    elements :h1, 'h1'
    elements :p, 'p'
  end

  element :continue_button, '.form-submit button'
  element :get_started_button, '#get-started'

  def load_page(page_version = nil)
    load(v: page_version)
  end
end
