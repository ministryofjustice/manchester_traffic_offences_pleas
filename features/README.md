Behaviour Driven Development
============================

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
