class CompanyDetailsPage < SitePrism::Page
  section :panel_grey, '.panel-grey' do
    element :heading_small, '.heading-small'
    element :p, 'p'
  end
  sections :form_group, '.form-group' do
    element :label_text, '.label-text'
    element :form_hint, '.form-hint'
  end
  section :section_company_name, '#section_company_name' do
    element :id_company_name, '#id_company_name'
  end
  section :section_correct_address, '#section_correct_address' do
    element :label_correct_address, '#label_correct_address'
    sections :block_label, '.block-label' do
      element :id_correct_address_true, '#id_correct_address_true'
      element :id_correct_address_false, '#id_correct_address_false'
    end
  end
  element :id_updated_address, '#id_updated_address'
  section :section_first_name, '#section_first_name' do
    element :label_text, '.label-text'
    element :id_first_name, '#id_first_name'
  end
  section :section_last_name, '#section_last_name' do
    element :label_text, '.label-text'
    element :id_last_name, '#id_last_name'
  end
  section :section_position_in_company, '#section_position_in_company' do
    element :label_position_in_company, '#label_position_in_company'
    elements :block_label, '.block-label'
    element :id_position_director, '#id_position_in_company_director'
    element :id_position_secretary, '#id_position_in_company_company-secretary'
    element :id_position_solicitor, '#id_position_in_company_company-solicitor'
  end
  section :section_contact_number, '#section_contact_number' do
    element :label_text, '.label-text'
    element :form_hint, '.form-hint'
    element :id_contact_number, '#id_contact_number'
  end
end
