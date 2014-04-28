Recurly Subscription Retention Report
=========================

Recurly is a payment platform for managing subscription services. It has a built in report for tracking subscription retention rates by month at: https://your_account_name.recurly.com/reports/subscriber_retention

Recurly's built in report is great, but doesn't let you change the cohort size or reporting periods, which can come in very handle when analyzing churn.

This repo is a simple python script that will analyze your subscription data and generate a CSV with your retention rates by cohort & period. I recommend looking at your data broken down by a period of 1 day, and 7 days if you're just starting to dig into your churn rates. Using excel's conditional formatting and adding a color scale to the file in excel is also very handy.

## Usage

* Git clone this repo.
```bash
git clone https://github.com/MattTheRed/recurly_retention_reports
```

* Download a csv export of your subscription data from recurly at:
https://your_account_name.recurly.com/exports/new#subscriptions

* Run the following command. Filename is the only required arguement. The script will default to a start date of now, cohort size of 7 days, retention period size of 7 days, and no filtering on which plan code to analyze.
```bash
python churn_by_cohort.py -f [path to subscriptions csv export] 
```

Or included additional options.
```bash
python churn_by_cohort.py -f [path to subscriptions csv export] -p [plan code] -c [cohort size] -r=[retention unit size] -s [start date e.g. 03-07-13]
```

## Additional Options:
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
