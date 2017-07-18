class YourCaseContinuedPage < BasePage
  set_url '/plea/your_case_continued'

  element :page_header, 'h1'
  element :number_of_charges, '#id_number_of_charges'
  elements :label_text, '.label-text'
  elements :form_hint, '.form-hint'
  element :day, '#id_date_of_birth_0'
  element :month, '#id_date_of_birth_1'
  element :year, '#id_date_of_birth_2'
  element :button, '.button'
  section :error_summary, '.error-summary' do
    element :h1, 'h1'
    element :p, 'p'
    sections :li, 'li' do
      elements :link, 'a'
    end
  end

  sections :error_list, '.errorlist' do
    element :li, 'li'
  end

  def load_page(page_version = nil)
    load(v: page_version)
  end
end
