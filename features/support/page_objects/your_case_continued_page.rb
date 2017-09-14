class YourCaseContinuedPage < SitePrism::Page
  element :page_header, 'h1'
  element :number_of_charges, '#id_number_of_charges'
  elements :label_text, '.label-text'
  elements :form_hint, '.form-hint'
  element :id_postcode, '#id_postcode'
  element :section_date_of_birth, '#section_date_of_birth'
  element :day, '#id_date_of_birth_0'
  element :month, '#id_date_of_birth_1'
  element :year, '#id_date_of_birth_2'
  sections :error_list, '.errorlist' do
    element :li, 'li'
  end
end
