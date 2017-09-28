class YourPleaNotGuiltyPage < SitePrism::Page
  element :not_guilty, '#id_guilty_not_guilty'
  element :h3, 'h3'

  section :panel_indent, '.panel-indent' do
    elements :p, 'p'
    element :come_to_court_true, '#id_come_to_court_true'
    element :come_to_court_false, '#id_come_to_court_false'
    element :label_come_to_court, '#label_come_to_court'
  end

  section :not_guilty_interpreter_needed, '#label_interpreter_needed' do
    element :label_text, '.label-text'
  end

  section :section_interpreter_language, '#section_interpreter_language' do
    element :form_hint, '.form-hint'
    element :id_interpreter_language, '#id_interpreter_language'
  end

  section :section_witness_interpreter_language, '#section_witness_interpreter_language' do
    element :form_hint, '.form-hint'
    element :id_witness_interpreter_language, '#id_witness_interpreter_language'
  end

  section :section_not_guilty_extra, '#section_not_guilty_extra' do
    element :label_text, '.label-text'
    element :form_hint, '.form-hint'
    element :id_not_guilty_extra, '#id_not_guilty_extra'
  end
  section :section_disagree_with_evidence, '#section_disagree_with_evidence' do
    section :label_disagree_with_evidence, '#label_disagree_with_evidence' do
      element :label_text, '.label-text'
    end
  end

  section :section_disagree_with_evidence_details, '#section_disagree_with_evidence_details' do
    element :form_hint, '.form-hint'
    element :id_disagree_with_evidence_details, '#id_disagree_with_evidence_details'
  end

  section :section_witness_needed, '#section_witness_needed' do
    section :label_witness_needed, '#label_witness_needed' do
      element :label_text, '.label-text'
      element :form_hint, 'form-hint'
    end
  end

  section :section_witness_details, '#section_witness_details' do
    element :form_hint, '.form-hint'
    element :id_witness_details, '#id_witness_details'
  end

  sections :block_label, '.block-label' do
    element :id_interpreter_needed_true, '#id_interpreter_needed_true'
    element :id_interpreter_needed_false, '#id_interpreter_needed_false'
    element :id_disagree_with_evidence_true, '#id_disagree_with_evidence_true'
    element :id_disagree_with_evidence_false, '#id_disagree_with_evidence_false'
    element :id_witness_needed_true, '#id_witness_needed_true'
    element :id_witness_needed_false, '#id_witness_needed_false'
    element :id_witness_interpreter_needed_true, '#id_witness_interpreter_needed_true'
    element :id_witness_interpreter_needed_false, '#id_witness_interpreter_needed_false'
  end

  section :label_witness_needed, '.label_witness_needed' do
    element :label_text, '.label-text'
    element :form_hint, '.form-hint'
  end
  elements :errorlist, '.errorlist'
end
