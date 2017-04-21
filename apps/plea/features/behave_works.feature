Feature: Behave is integrated with Django

    Scenario: Django-behave can see this test and other tests still work
	Given django-behave is installed
	When the django-behave tests are invoked
	Then this test passes
	And other tests still run fine
