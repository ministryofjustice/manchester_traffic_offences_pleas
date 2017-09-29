class YourPleaPage < SitePrism::Page
  element :guilty, '#id_guilty_guilty'
  element :not_guilty, '#id_guilty_not_guilty'
  elements :block_label, '.block-label'

  section :panel_grey, '.panel-grey' do
    element :p, 'p'
    elements :li, 'li'
  end
  section :label_charge, '#label_charge' do
    element :label_text, '.label-text'
  end
end
