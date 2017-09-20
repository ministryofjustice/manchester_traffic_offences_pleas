URN = {
  # All have posting date: 11/09/2017
  # your notice page loads
  valid: '98FF1234583',
  # your notice page loads
  valid_2: '98FF1234583',
  # urn is not valid
  invalid: '020124567',
  # you cannot make a plea online
  dob_postcode_unknown: '97FF1234585',
  # your case continued
  dob_postcode_known: '98BB1234587',
  # enter dob, not postcode
  dob_known: '98BB1234588',
  # enter postcode
  dob_unknown: '98BB1234587'
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

def notice_type_page
  @notice_type_page ||= NoticeTypePage.new
end

def case_details_page
  @case_details_page ||= CaseDetailsPage.new
end

def your_details_page
  @your_details_page ||= YourDetailsPage.new
end
