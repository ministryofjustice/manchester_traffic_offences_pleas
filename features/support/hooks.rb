require 'yaml'
require 'uri'

class TestFrameworkState

  attr :api_endpoint, true
  attr :api_stdin, true
  attr :api_stdout, true
  attr :api_stderr, true
  attr :api_wait_thr, true
  attr :api_pid, true
  attr :api_exit_status, true

  attr :app_endpoint, true
  attr :app_stdin, true
  attr :app_stdout, true
  attr :app_stderr, true
  attr :app_wait_thr, true
  attr :app_pid, true
  attr :app_exit_status, true
  
  attr :start_server, true

  def initialize()

    # Parse the config file
    file = File.read(
      File.join(
        File.dirname(
          File.dirname(__FILE__)),
        "config.yml"))
    config_yml = YAML.parse(file)

    # If ENV is local, start the services
    if ENV["ENDPOINT"] == "local"
      @start_server = true
    end

    @api_endpoint = config_yml.to_ruby()[ENV["ENDPOINT"]]["api_endpoint"]
    @app_endpoint = config_yml.to_ruby()[ENV["ENDPOINT"]]["app_endpoint"]

  end

end

$project_root = File.expand_path(
        File.dirname(
            File.dirname(
                File.dirname(__FILE__)
            )
        )
)

$python_bin = %x(which python).strip()
$wget_bin = %x(which wget).strip()
$state = TestFrameworkState.new()

# Before all
AfterConfiguration do |config|

    api_uri = URI.parse($state.api_endpoint)
    app_uri = URI.parse($state.app_endpoint)
    
    if $state.start_server == true

      # Don't block when launching the API
      $state.api_stdin, $state.api_stdout, $state.api_stderr, $state.api_wait_thr = Open3.popen3(
          {"DJANGO_SETTINGS_MODULE" => "api.settings.testing"},
          $python_bin,
          File.join($project_root, "manage.py"),
          "runserver",
          "--noreload",
          "#{api_uri.host}:#{api_uri.port}",
      )
      $state.api_pid = $state.api_wait_thr[:pid]
      #puts "Using API endpoint #{api_uri.to_s} with PID #{$state.api_pid}",

      # Don't block when launching the app
      $state.app_stdin, $state.app_stdout, $state.app_stderr, $state.app_wait_thr = Open3.popen3(
          {"DJANGO_SETTINGS_MODULE" => "make_a_plea.settings.testing"},
          $python_bin,
          File.join($project_root, "manage.py"),
          "runserver",
          "--noreload",
          "#{app_uri.host}:#{app_uri.port}",
      )

      $state.app_pid = $state.app_wait_thr[:pid]
      #puts "Using App endpoint #{app_uri.to_s} with PID #{$state.app_pid}"

      # Block while testing if the API is up, exit if not
      Open3.popen3(
              $wget_bin,
              "--retry-connrefused",
              "--waitretry=2",  # Wait for app to be listening
              "--read-timeout=20",  # Wait for app to respond
              "--timeout=15",  # Time from initial connection
              "-t 20",  # Give up after this many times
              "#{api_uri.to_s}",
      ) {|stdin, stdout, stderr, wait_thr|
          api_check_status = wait_thr.value.exitstatus

          if api_check_status == 0 or api_check_status == 6 # Auth error is OK
            puts "API is up"
          else
            puts "Could not launch API, exit status is #{api_check_status}, stderr is:"
            stderr.each { |line| puts line }
            Kernel.exit(1)
          end
      }
  
      # Block while testing if the app is up, exit if not
      Open3.popen3(
              $wget_bin,
              "--retry-connrefused",
              "--waitretry=2",  # Wait for app to be listening
              "--read-timeout=20",  # Wait for app to respond
              "--timeout=15",  # Time from initial connection
              "-t 20",  # Give up after this many times
              "#{app_uri.to_s}",
      ) {|stdin, stdout, stderr, wait_thr|
          app_check_status = wait_thr.value.exitstatus

          if app_check_status == 0
            puts "APP is up"
          else
            puts "Could not launch APP, exit status is #{app_check_status}, stderr is:"
            stderr.each { |line| puts line }
            Kernel.exit(1)
          end
      }
  
      # Block while loading fixtures
      puts "Loading fixtures..."
      Open3.popen3(
              {"DJANGO_SETTINGS_MODULE" => "make_a_plea.settings.testing"},
              $python_bin,
              File.join($project_root, "manage.py"),
              "fixtures",
              "--method", "load",
              "--category", "cucumber",
              "--count", "1",
      ) {|stdin, stdout, stderr, wait_thr|
          fixture_check_status = wait_thr.value.exitstatus

          if fixture_check_status == 0  # Auth error is OK
            puts "Fixtures are loaded"
          else
            puts "Could not load fixtures, exit status is #{fixture_check_status}, stderr is:"
            stderr.each { |line| puts line }
            Kernel.exit(1)
         end
      }
  
    end

  puts "Features dwell in #{config.feature_dirs}"

end

# After all
at_exit do

  if $state.start_server == true
      
    $state.api_stderr.each { |line| puts line }
    $state.app_stderr.each { |line| puts line }

    Process.kill(9, $state.app_pid)
    $state.app_stdin.close
    $state.app_stdout.close
    $state.app_stderr.close
    
    Process.kill(9, $state.api_pid)
    $state.api_stdin.close
    $state.api_stdout.close
    $state.api_stderr.close

  end

  Capybara.current_session.driver.quit()

end
