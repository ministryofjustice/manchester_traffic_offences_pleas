def wait_for
  Timeout.timeout(Capybara.default_max_wait_time) do
    begin
      loop until yield
    rescue # rubocop:disable Lint/HandleExceptions
      # ignored
    end
  end
end

def wait_for_ajax
  wait_for { page.evaluate_script('jQuery.active').zero? }
end

def wait_for_document_ready
  wait_for { page.evaluate_script('document.readyState').eql? 'complete' }
end

def wait_for_dropdown_change(dropdown, expected_value)
  wait_for { dropdown.value == expected_value }
end

def scroll_down
  Capybara.execute_script('window.scrollBy(0,1000)')
end

def scroll_to_bottom
  WaitUntil.wait_until(3, 'Failed as browser hasnt reached bottom of window') do
    page.execute_script 'window.scrollTo(0,$(document).height())'
    y_position = page.evaluate_script 'window.scrollY'
    browser_height = page.evaluate_script '$(window).height();'
    doc_height = page.evaluate_script '$(document).height();'
    (y_position + browser_height).eql?(doc_height)
  end
end

module WaitUntil
  def self.wait_until(timeout = 10, message = nil, &block)
    wait = Selenium::WebDriver::Wait.new(timeout: timeout, message: message)
    wait.until(&block)
  end
end
