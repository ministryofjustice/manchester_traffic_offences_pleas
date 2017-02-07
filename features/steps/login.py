from selenium import webdriver


class AdminLoginPage(webdriver.Firefox):

    LOGIN = 'http://127.0.0.1:8000/admin/login'
    LOGOUT = 'http://127.0.0.1/admin/logout'

    def log_in(self, username, password):
        """
        Locate and input values to the user and password fields and submit the form
        :param username: The username to login with
        :param password: The password to login with
        """
        self.open(AdminLoginPage.LOGIN)
        username_field = self.query_selector_css(
            '.form-control[name="username"]')
        username_field.send_keys(username)
        password_field = self.query_selector_css(
            '.form-control[name="password"]')
        password_field.send_keys(password)
        login_button = self.query_selector_css(
            '.btn-success')
        login_button.click()

    def log_out(self):
        """
        Visit the logout page
        """
        self.open(AdminLoginPage.LOGOUT)
