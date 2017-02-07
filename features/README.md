Behaviour Driven Development
============================

Running the tests
-----------------

The feature files (and steps) at this level are run from the project root with:

``script
behave
```

If it makes sense to move features into the app, django-behave can run them with:

```script
python manage.py tests --settings=makeaplea.settings.bdd
```

run_tests.sh calls these tests with coverage.

If it makes sense to move them into a higher level cross-app BDD project then that's also an option.

Writing BDD statements
----------------------

 * Look at the existing statements to see what can be re-used
 * environment.py is for feature/scenario/step setup/teardown
 * common.py is for steps that are used by more than one feature file
 * helpers.py is for helper functions
 * The feature files are named after the ticket number and the feature description

Writing step definitions
------------------------

Some conventions used by the current test suite:

 * Don't take shortcuts (don't manipulate applications internals)
   * load fixtures the way you would import data; the "as a" for this is the sysadmin
   * 
 * Create one or more fixture sets to test a feature or scenario
 * Use the mangled name of the bdd statement. This has certain benefits:
   * there is no additional layer of abstraction
   * there are no naming decisions to regret
   * pyflakes doesn't complain about duplicate step implementations
   * steps can be reused easily by other steps. if it's too long to be used easily the alias it where you use it
 * TODO: Confirm: Background givens that install fixtures are available to all scenarios

