# Make a Plea public API

The Make a Plea service provides a public API for stats, which is used to provide the Make a Plea dashboard with relevant data, but is also publicly available.

## 8.1 API root URL

The API resources can be accessed at the following root URL: `https:/api.makeaplea.service.gov.uk/v0/`

## 8.2 Rate limiting

The public API is rate limited by IP address, allowing up to 100 queries per IP per day.

## 8.3 Response formats

The public API is available in application/json and the [Django Browsable API](http://www.django-rest-framework.org/api-guide/renderers/#browsableapirenderer) formats. Set the format parameter as required: `https://api.makeaplea.service.gov.uk/v0/stats/?format=json` or `https://api.makeaplea.service.gov.uk/v0/stats/?format=api`. Providing no format parameter defaults to the Browsable API response format.

## 8.4 Submission Totals

Most endpoints return a set of stats known as Submission Totals, which contains the following properties:

- `submissions`: total number of Submissions
- `pleas`: total number of Pleas
- `guilty`: total number of Guilty pleas
- `not_guilty`: total number of Not guilty pleas

Example:
```json
{
    "pleas": 13679,
    "guilty": 12035,
    "submissions": 11726,
    "not_guilty": 1644
}

```

## 8.5 Endpoints

### 8.5.1 GET /stats/
Returns the Submissions Totals for all courts.

#### Parameters

##### start (optional)

Exclude stats _before_ the start of the given date. Format: `YYYY-MM-DD`

`/stats/?start=2015-10-31`

##### end (optional)

Exclude stats _after_ the start of the given date. Format: `YYYY-MM-DD`

`/stats/?end=2015-12-21`

#### Note

The API treats any given start or end date as a 'before or after' _based on the start of the given date_. This means that, to query only the 1st of January 2015, the start date needs to be the 1st January and the end date the 2nd, like so:

`/stats/?start=2015-01-01&end=2015-01-02`


#### Example response

```json
{
    "pleas": 13679,
    "guilty": 12035,
    "submissions": 11726,
    "not_guilty": 1644
}
```

### 8.5.2 GET /stats/days_from_hearing/

Returns the total number of submissions based on the number of days left before the hearing, or before the SJP deadline, for 60 days.

This endpoint takes no parameters.

#### Example response

```json
{
    "0": 0,
    "1": 484,
    "2": 397,
    ...
    "58": 43,
    "59": 23
}
```

### 8.5.3 GET /stats/by_hearing/

Returns the Submission Totals for each of the current week's hearing dates. Also returns:

- `hearing_day`: the date of hearing for this set of stats. Format: `YYYY-MM-DD`

This endpoint takes no parameters.

#### Example response

```json
[
    {
        "hearing_day": "2015-12-28",
        "submissions": 5,
        "pleas": 6,
        "guilty": 5,
        "not_guilty": 1
    },
    {
        "hearing_day": "2015-12-29",
        "submissions": 43,
        "pleas": 45,
        "guilty": 42,
        "not_guilty": 3
    },
    ...
]
```

### 8.5.4 GET /stats/all_by_hearing/

Returns the Submission Totals for all recorded hearing dates. Also returns:

- `hearing_day`: the date of hearing for this set of stats. Format: `YYYY-MM-DD`

This endpoint takes no parameters.

#### Example response

```json
[
    {
        "hearing_day": "2014-08-29",
        "submissions": 1,
        "pleas": 1,
        "guilty": 1,
        "not_guilty": 0
    },
    {
        "hearing_day": "2014-09-19",
        "submissions": 1,
        "pleas": 1,
        "guilty": 1,
        "not_guilty": 0
    },
    ...
]
```


### 8.5.5 GET /stats/by_week/

Returns online and postal submission stats for each week for the last 6 months.

- `id`: (deprecated)
- `start_date`: start of the week
- `postal_requisitions`: total postal requisitions/SJP notices sent. `Null` if no data available
- `online_submissions`: total online submissions
- `online_guilty_pleas`: total online Guilty pleas
- `online_not_guilty_pleas`: total online Not guilty pleas
- `postal_responses`: total postal submissions. `Null` if no data available

This endpoint takes no parameters.

#### Example response

```json
[
    {
        "id": 63,
        "start_date": "2015-07-13",
        "online_submissions": 147,
        "online_guilty_pleas": 147,
        "online_not_guilty_pleas": 23,
        "postal_requisitions": null,
        "postal_responses": null
    },
    {
        "id": 64,
        "start_date": "2015-07-20",
        "online_submissions": 196,
        "online_guilty_pleas": 189,
        "online_not_guilty_pleas": 20,
        "postal_requisitions": null,
        "postal_responses": null
    },
    ...
]
```


### 8.5.6 GET /stats/by_court/

Returns Submission Totals for each court. Also returned:

- `region_code`: the region code for the court
- `court_name`: the name of the court

#### Parameters

##### start (optional)

Exclude stats _before_ the start of the given date. Format: `YYYY-MM-DD`

`/stats/?start=2015-10-31`

##### end (optional)

Exclude stats _after_ the start of the given date. Format: `YYYY-MM-DD`

`/stats/?end=2015-12-21`

#### Example response

```json
[
    {
        "region_code": "06",
        "court_name": "Manchester and Salford Magistrates' Court",
        "submissions": 5132,
        "pleas": 5625,
        "not_guilty": 653,
        "guilty": 4972,
    },
    {
        "pleas": 392,
        "region_code": "02",
        "not_guilty": 47,
        "submissions": 390,
        "guilty": 345,
        "court_name": "Lavender Hill Magistrates' Court"
    },
    ...
]
```

