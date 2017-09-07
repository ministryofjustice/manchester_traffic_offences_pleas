require 'yaml'
file = File.read(
    File.join(
        File.dirname(
            File.dirname(__FILE__)),
        "config.yml"))
config_yml = YAML.parse(file)

# Exit if ENDPOINT is not set
if !ENV.key?('ENDPOINT')
  puts "'ENDPOINT' environment variable must be set"
  Kernel.exit(1)
end


Capybara.configure do |config|
  driver = (ENV['DRIVER'].to_sym if ENV['DRIVER']) || :poltergeist
  Capybara.app_host = config_yml.to_ruby()[ENV["ENDPOINT"]]["app_endpoint"]
  config.default_driver = driver
  config.default_max_wait_time = 60
  config.match = :prefer_exact
  config.ignore_hidden_elements = false
  config.visible_text_only = true
end

Capybara.register_driver :poltergeist do |app|
  Capybara::Poltergeist::Driver.new(app, js_errors: false, timeout: 600)
end

Capybara.register_driver :firefox do |app|
  profile = Selenium::WebDriver::Firefox::Profile.new
  profile.enable_firebug
  profile['browser.cache.disk.enable'] = false
  profile['browser.cache.memory.enable'] = false
  profile.timeout = 1200
  Capybara::Selenium::Driver.new(app, browser: :firefox, profile: profile)
end

Capybara.register_driver :chrome do |app|
  Capybara::Selenium::Driver.new(app, browser: :chrome)
end

if ENV.key?('CIRCLE_ARTIFACTS')
  Capybara.save_and_open_page_path = ENV['CIRCLE_ARTIFACTS']
end

Capybara::Screenshot.register_driver(:chrome) do |driver, path|
  driver.browser.save_screenshot(path)
end

Capybara.register_driver :safari do |app|
  Capybara::Selenium::Driver.new(app, browser: :safari)
end

Capybara::Screenshot.register_filename_prefix_formatter(:cucumber) do |scenario|
  title = scenario.title.tr(' ', '-').gsub(%r{/^.*\/cucumber\//}, '')
  "screenshot_cucumber_#{title}"
end

Capybara.javascript_driver = Capybara.default_driver
Capybara.current_driver = Capybara.default_driver
