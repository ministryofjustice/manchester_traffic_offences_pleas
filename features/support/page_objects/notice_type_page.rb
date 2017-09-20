class NoticeTypePage < SitePrism::Page
  element :label_sjp, '#label_sjp'
  sections :block_label, '.block-label' do
    element :sjp_true, '#id_sjp_true'
    element :sjp_false, '#id_sjp_false'
  end
end
