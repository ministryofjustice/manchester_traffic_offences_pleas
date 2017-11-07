class CompanyPleaPage < SitePrism::Page
  section :panel_indent, '.panel-indent' do
    element :p, 'p'
  end
  section :section_not_guilty_extra, '#section_not_guilty_extra' do
    element :form_hint, '.form-hint'
  end
  section :label_interpreter_needed, '#label_interpreter_needed' do
    element :label_text, '.label-text'
  end
end
