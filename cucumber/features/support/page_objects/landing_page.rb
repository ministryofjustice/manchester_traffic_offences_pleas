class LandingPage < BasePage
  set_url '/make-a-plea'

  section :content, '#content' do
    element :page_header, 'h1'
    element :get_started_intro, '.get-started-intro'
    element :available_in_welsh, '.application-notice p'
    element :available_in_welsh_link, '.application-notice a'
    element :start_now_button, '#get-started a'
    element :before_you_start, '#before-you-start'
    element :before_you_start_link, '#before-you-start > p:nth-child(4) > a'
    element :get_help_link, '#before-you-start > p:nth-child(5) > a'
  end

  def load_page(page_version = nil)
    load(v: page_version)
  end
end