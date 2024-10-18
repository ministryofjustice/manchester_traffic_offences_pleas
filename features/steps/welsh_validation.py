from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

@then(u'I should see the Welsh validation message')
def step_impl(context):
    expected_text = "Yn anffodus, nid yw'r cyfeirnod unigryw yn ddilys"
    try:
        WebDriverWait(context.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{expected_text}')]"))
        )
    except TimeoutException:
        print(f"Welsh validation message not found")
        print(f"Current URL: {context.browser.current_url}")
        raise AssertionError(f"Welsh validation message not found")
