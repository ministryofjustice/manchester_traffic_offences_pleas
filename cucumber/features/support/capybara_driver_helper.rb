Capybara.configure do |config|
  config.default_driver = (ENV['DRIVER'].to_sym if ENV['DRIVER']) || :poltergeist
  config.default_max_wait_time = 30
  config.match = :prefer_exact
  config.ignore_hidden_elements = false
  config.visible_text_only = true
end

Capybara.register_driver :poltergeist do |app|
  Capybara::Poltergeist::Driver.new(app, js_errors: false, timeout: 60)
end

Capybara.register_driver :firefox do |app|
  profile = Selenium::WebDriver::Firefox::Profile.new
  profile.enable_firebug
  profile['browser.cache.disk.enable'] = false
  profile['browser.cache.memory.enable'] = false
  Capybara::Selenium::Driver.new(app, browser: :firefox, profile: profile)
end

Capybara.register_driver :chrome do |app|
  Capybara::Selenium::Driver.new(app, browser: :chrome)
end

Capybara.save_and_open_page_path = ENV['CIRCLE_ARTIFACTS'] if ENV.key?('CIRCLE_ARTIFACTS')

Capybara::Screenshot.register_driver(:chrome) do |driver, path|
  driver.browser.save_screenshot(path)
end

Capybara.register_driver :safari do |app|
  Capybara::Selenium::Driver.new(app, browser: :safari)
end

Capybara::Screenshot.register_filename_prefix_formatter(:cucumber) do |scenario|
  "screenshot_cucumber_#{scenario.title.tr(' ', '-').gsub(%r{/^.*\/cucumber\//}, '')}"
end

Capybara.javascript_driver = Capybara.default_driver
Capybara.current_driver = Capybara.default_driver
#Capybara.app_host = ENV['HOST'] if ENV['HOST']
# TODO: get this running locally http://127.0.0.1:
Capybara.app_host = "https://www.makeaplea.service.gov.uk#{Capybara.server_port}"