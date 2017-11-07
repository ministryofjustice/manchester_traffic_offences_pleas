class YourPleaPage < SitePrism::Page
  elements :block_label, '.block-label'

  section :panel_grey, '.panel-grey' do
    element :p, 'p'
    elements :li, 'li'
  end
  elements :block_label, '.block-label'
  element :heading_small, '.heading-small'
  section :label_charge, '#label_charge' do
    element :label_text, '.label-text'
  end
  section :details_trigger, '.details-trigger' do
    element :summary, '.summary'
  end
  element :charge_details, '#charge-details > p'
  element :guilty, '#id_guilty_guilty'
  element :not_guilty, '#id_guilty_not_guilty'
end
