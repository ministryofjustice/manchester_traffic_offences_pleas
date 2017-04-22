class LandingPage < BasePage
  set_url '/make-a-plea'

  section :content, '#content' do
    element :page_header, 'h1'
    element :get_started_intro, '#get-started-intro'
    element :start_now_button, '#get-started'
  end

  def load_page(page_version = nil)
    load(v: page_version)
  end
end