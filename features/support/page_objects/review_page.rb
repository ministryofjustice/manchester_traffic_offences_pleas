class ReviewPage < SitePrism::Page
  section :case_details, '#case-details' do
    element :h2, 'h2'
    elements :dt, 'dt'
    elements :dd, 'dd'
    elements :change_link_dl, '.change-link-dl'
  end
  section :your_details, '#your-details' do
    element :h2, 'h2'
    elements :dt, 'dt'
    elements :dd, 'dd'
    element :change_link, '.change-link'
  end
  section :your_plea, '#your-plea' do
    element :h2, 'h2'
    elements :dt, 'dt'
    elements :dd, 'dd'
    element :change_link, '.change-link'
  end
  section :form_group_wide, '.form-group-wide' do
    element :h2, 'h2'
    element :important, '.important'
    element :id_understand, '#id_understand'
    element :checkbox_text, '.checkbox-text'
  end
  element :button_large, '.button-large'
end
