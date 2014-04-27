recurly_retention_reports
=========================

Recurly is a payment platform for managing subscription services.

These are a set of command line tools that will help you analyze your retention 
rates for your subscription plans. You can run these reports against csv exports
of your account data, available at:

https://your_account_name.recurly.com/exports/new#subscriptions

*Usage*

Filename is the only required arguement. The script will default to a start date of now, cohort size of 7 days, retention period size of 7 days, and no filtering on which plan code to analyze.
```bash
python churn_by_cohort.py -f [path to subscriptions csv export] -p [plan code] - c-r=[retention unit size] -s [start date e.g. 03-07-13]
```

Options:
```bash
 -h, --help            show this help message and exit
  -f FILE, --file FILE  Filename of subscriptions csv from exported from
                        recurly
  -p PLAN, --plan PLAN  Filter down to a specific subscription plan
  -c COHORT_SIZE, --cohort_size COHORT_SIZE
                        Define size of cohorts
  -r RETENTION_PERIOD_SIZE, --retention_period_size RETENTION_PERIOD_SIZE
                        Define size of retention periods
  -s START_DATE, --start START_DATE
                        Define the start date of the period
```

For questions, comments, or suggestions contact me at mattthered@gmail.com
