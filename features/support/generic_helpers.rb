URN = {
  valid: '98FF1234583', # your notice page loads
  valid_2: '98FF1234583', # your notice page loads
  invalid: '020124567', # urn is not valid
  dob_postcode_unknown: '97FF1234585', # you cannot make a plea online
  dob_postcode_known: '98BB1234587', # your case continued
  dob_known: '98BB1234588', # enter dob, not postcode
  dob_unknown: '98BB1234587' # enter postcode
}.freeze

def wait_for
  Timeout.timeout(Capybara.default_max_wait_time) do
    begin
      loop until yield
    rescue # rubocop:disable Lint/HandleExceptions
      # ignored
    end
  end
end

def wait_for_document_ready
  wait_for { page.evaluate_script('document.readyState').eql? 'complete' }
end

def wait_for_dropdown_change(dropdown, expected_value)
  wait_for { dropdown.value == expected_value }
end

def common_page
  @common_page ||= CommonPage.new
end

def enter_urn_page
  @enter_urn_page ||= EnterUrnPage.new
end

def your_case_continued_page
  @your_case_continued_page ||= YourCaseContinuedPage.new
end
