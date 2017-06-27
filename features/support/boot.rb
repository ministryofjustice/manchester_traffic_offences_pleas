require 'pry'
require 'site_prism'
require 'capybara'
require 'capybara/dsl'
require 'capybara/cucumber'
require 'capybara/poltergeist'
require 'capybara-screenshot/cucumber'

require File.dirname(__FILE__) + '/../support/capybara_driver_helper'
require File.dirname(__FILE__) + '/../support/site_prism_config'

# Get the endpoint for the enmvironment
require 'yaml'    
ENV['TEST_ENV'] ||= 'local'
project_root = File.expand_path('../..', __FILE__)
$BASE_URL = YAML.load_file(project_root + "/config/config.yml")[ENV['TEST_ENV']][:url]

