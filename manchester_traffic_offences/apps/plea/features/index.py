from lettuce import *
from lxml import html

# from django.test.client import Client
from lettuce.django import django_url

from splinter.browser import Browser

# from selenium import webdriver
# import lettuce_webdriver.webdriver

@before.all
def set_browser():
    world.browser = Browser()
    # world.browser = webdriver.Firefox()

@step(r'I access the url "(.*)"')
def navigate_to_url(step, url):
    if not url.endswith('/'):
        url = url + "/"
    full_url = django_url(url)
    response = world.browser.visit(full_url)
    # world.dom = html.fromstring(response.content)

@step(r'see the text "(.*)"')
def see_header(step, text):
    assert world.browser.is_text_present(text)

@step(u'fill in "(.*)" with "(.*)"')
def enter_information(step, field, value):
    world.browser.fill(field, value)
    
@step(ur'press continue')
def continue_step(step):
    world.browser.find_by_css("button[type=submit]").click()

@step(ur'choose "(.*)" from "(.*)"')
def select_radio(step, option, group):
    world.browser.find_by_css("[name=%s][value=%s]" % (group, option))[0].click()

@step(ur'check "(.*)"')
def checkbox(step, field):
    world.browser.find_by_css("[name=%s]" % field)[0].click()

@after.all
def teardown(total):
    # import ipdb
    # ipdb.set_trace()
    world.browser.driver.close()