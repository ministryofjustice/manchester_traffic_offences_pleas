class YourDetailsPage < SitePrism::Page
  section :section_first_name, '#section_first_name' do
    element :label_text, '.label-text'
    element :id_first_name, '#id_first_name'
  end
  section :section_middle_name, '#section_middle_name' do
    element :label_text, '.label-text'
    element :id_middle_name, '#id_middle_name'
  end
  section :section_last_name, '#section_last_name' do
    element :label_text, '.label-text'
    element :id_last_name, '#id_last_name'
  end
  element :id_correct_address_true, '#id_correct_address_true'
  element :id_correct_address_false, '#id_correct_address_false'
  section :section_correct_address, '#section_correct_address' do
    element :label_text, '.label-text'
  end
  section :section_updated_address, '#section_updated_address' do
    element :form_hint, '.form-hint'
    element :id_updated_address, '#id_updated_address'
  end
  section :section_contact_number, '#section_contact_number' do
    element :label_text, '.label-text'
    element :id_contact_number, '#id_contact_number'
    element :form_hint, '.form-hint'
    element :id_updated_address, '#id_updated_address'
  end
  section :section_email, '#section_email' do
    element :label_text, '.label-text'
    element :form_hint, '.form-hint'
    element :id_email, '#id_email'
  end
  section :section_date_of_birth, '#section_date_of_birth' do
    element :label_date_of_birth, '#label_date_of_birth'
    element :id_date_of_birth_0, '#id_date_of_birth_0'
    element :id_date_of_birth_1, '#id_date_of_birth_1'
    element :id_date_of_birth_2, '#id_date_of_birth_2'
  end
  section :section_have_ni_number, '#section_have_ni_number' do
    element :label_have_ni_number, '#label_have_ni_number'
  end
  element :id_have_ni_number_true, '#id_have_ni_number_true'
  element :id_have_ni_number_false, '#id_have_ni_number_false'
  section :section_ni_number, '#section_ni_number' do
    element :form_hint, '.form-hint'
    element :id_ni_number, '#id_ni_number'
  end
  element :id_have_driving_licence_number_true, '#id_have_driving_licence_number_true'
  element :id_have_driving_licence_number_false, '#id_have_driving_licence_number_false'
  section :section_have_driving_licence_number, '#section_have_driving_licence_number' do
    element :label_text, '.label-text'
    element :form_hint, '.form-hint'
  end
  section :section_driving_licence_number, '#section_driving_licence_number' do
    element :form_hint, '.form-hint'
    element :img, 'img'
    element :id_driving_licence_number, '#id_driving_licence_number'
  end
end
