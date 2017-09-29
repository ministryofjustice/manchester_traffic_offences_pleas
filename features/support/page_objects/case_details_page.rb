class CaseDetailsPage < SitePrism::Page
  section :posting_date, '#label_posting_date' do
    element :label_text, '.label-text'
    element :form_hint, '.form-hint'
  end
  element :day, '#id_posting_date_0'
  element :month, '#id_posting_date_1'
  element :year, '#id_posting_date_2'
  section :number_of_charges, '#section_number_of_charges' do
    element :label_text, '.label-text'
    element :form_hint, '.form-hint'
  end
  element :id_number_of_charges, '#id_number_of_charges'
  section :section_plea_made_by, '#section_plea_made_by' do
    element :label_text, '.label-text'
    element :form_hint, '.form-hint'
  end
  element :plea_made_by_defendant, '#id_plea_made_by_defendant'
  element :plea_made_by_company_rep, '#id_plea_made_by_company-representative'
end
