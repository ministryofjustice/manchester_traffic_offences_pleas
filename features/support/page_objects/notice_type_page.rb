class NoticeTypePage < SitePrism::Page
  include Capybara::DSL
  sections :block_label, '.block-label' do
    element :sjp_true, '#id_sjp_true'
    element :sjp_false, '#id_sjp_false'
  end
end
