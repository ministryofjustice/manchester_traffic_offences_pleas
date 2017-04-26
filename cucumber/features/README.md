##Automated testing

##Dependances

You need to install:

Ruby

[Bundler](http://bundler.io/)

To install all of the required gems:
$ bundle install

[PhantomJS](https://github.com/teampoltergeist/poltergeist#installing-phantomjs)


###Rubocop

To assess Ruby code quality across the application we use
[Rubocop](https://github.com/bbatsov/rubocop)
To run the tool, use:
$ rubocop

###Running Cucumber scenarios

For integration and UI testing, we use [Cucumber](http://cukes.info/),
[Capybara](https://github.com/jnicklas/capybara)

To run the standard Cucumber test suite, use:
$ cucumber features 

To run the all scenarios in a particular feature file:
$ cucumber features/landing_page.feature  

To run a particular scenario:
$ cucumber features/landing_page.feature:10 

To run in a browser:
$ DRIVER=chrome cucumber
$ DRIVER=firefox cucumber


###Screenshots and html

To open screenshot or html:
$ open ./screenshot_cucumber_Start-now_2017-04-24-11-40-28.186.png
$ open ./screenshot_cucumber_Start-now_2017-04-24-11-40-28.186.html





