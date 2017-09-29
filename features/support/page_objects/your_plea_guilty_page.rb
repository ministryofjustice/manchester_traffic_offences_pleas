class YourPleaGuiltyPage < SitePrism::Page
  element :guilty, '#id_guilty_guilty'
  section :panel_indent, '.panel-indent' do
    elements :p, 'p'
    element :come_to_court_true, '#id_come_to_court_true'
    element :come_to_court_false, '#id_come_to_court_false'
    element :label_come_to_court, '#label_come_to_court'
  end

  section :label_sjp_interpreter_needed, '#label_sjp_interpreter_needed' do
    element :label_text, '.label-text'
  end

  section :section_sjp_interpreter_language, '#section_sjp_interpreter_language' do
    element :form_hint, '.form-hint'
    element :id_sjp_interpreter_language, '#id_sjp_interpreter_language'
  end

  section :section_guilty_extra, '#section_guilty_extra' do
    element :label_text, '.label-text'
    element :form_hint, '.form-hint'
    element :form_hint_inline, '.form-hint-inline'
    element :id_guilty_extra, '#id_guilty_extra'
  end

  sections :block_label, '.block-label' do
    element :id_sjp_interpreter_needed_true, '#id_sjp_interpreter_needed_true'
    element :id_sjp_interpreter_needed_false, '#id_sjp_interpreter_needed_false'
  end
end
