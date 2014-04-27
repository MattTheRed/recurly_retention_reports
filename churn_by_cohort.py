import csv
import datetime
from collections import defaultdict
from dateutil import parser
from copy import deepcopy
import sys, getopt
from collections import OrderedDict, Callable
import argparse

#http://stackoverflow.com/questions/6190331/can-i-do-an-ordered-default-dict-in-python
class DefaultOrderedDict(OrderedDict):
    def __init__(self, default_factory=None, *a, **kw):
        if (default_factory is not None and
            not isinstance(default_factory, Callable)):
            raise TypeError('first argument must be callable')
        OrderedDict.__init__(self, *a, **kw)
        self.default_factory = default_factory
    def __getitem__(self, key):
        try:
            return OrderedDict.__getitem__(self, key)
        except KeyError:
            return self.__missing__(key)
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = value = self.default_factory()
        return value
    def __reduce__(self):
        if self.default_factory is None:
            args = tuple()
        else:
            args = self.default_factory,
        return type(self), args, None, None, self.items()
    def copy(self):
        return self.__copy__()
    def __copy__(self):
        return type(self)(self.default_factory, self)
    def __deepcopy__(self, memo):
        import copy
        return type(self)(self.default_factory,
                          copy.deepcopy(self.items()))
    def __repr__(self):
        return 'OrderedDefaultDict(%s, %s)' % (self.default_factory,
                                        OrderedDict.__repr__(self))


def build_cohorts(start_date, cohort_size, oldest_subscription_date):
    cohorts = DefaultOrderedDict(dict)
    while start_date > oldest_subscription_date:
        cohort_end_date = start_date
        cohort_start_date = start_date - datetime.timedelta(cohort_size)
        start_date = cohort_start_date
        cohort_name = "%s - %s" % (cohort_start_date.strftime("%D"), 
            (cohort_end_date - datetime.timedelta(1)).strftime("%D"))
        cohorts[cohort_name] = {}
        cohorts[cohort_name]["cohort_end_date"] = cohort_end_date
        cohorts[cohort_name]["cohort_start_date"] = cohort_start_date
        cohorts[cohort_name]["subscriptions"] = []
    return cohorts



def get_retention_by_cohort(csv_path, plan_code=None, cohort_size = 7, 
    retention_period_size = 7, start_date = datetime.datetime.now()):
    # Assume file in same directory, fall back to full path 
    try:
        data_file = open(os.getcwd() + "/" + csv_path)
    except:
        data_file = open(csv_path)

    data_reader = csv.reader(data_file)

    data = []
    start_date = start_date.replace(hour=0, minute=0, second=0,microsecond=0)
    oldest_subscription_date = start_date

    for row in data_reader:
        try:
            if not plan_code or plan_code in row[3]:
                subscription_activation_date = parser.parse(row[17]).replace(
                    tzinfo=None)
                if subscription_activation_date < oldest_subscription_date:
                    oldest_subscription_date = subscription_activation_date
            data.append(row)
        except ValueError:
            # Will choke on the first row (column headers)
            pass

    cohorts = build_cohorts(start_date, cohort_size, oldest_subscription_date)
    for row in data:
        if not plan_code or plan_code in row[3]:
            subscription = {}
            subscription["billing_account_code"] = row[1]
            subscription["state"] = row[4]
            subscription["unit_amount"] = row[8]
            subscription["activated_at"] = parser.parse(row[17]).replace(
                tzinfo=None)
            subscription["canceled_at"] = parser.parse(row[19]).replace(
                tzinfo=None)
            for cohort in cohorts:
                if subscription["activated_at"] >= cohorts[cohort]["cohort_start_date"]:
                    cohorts[cohort]["subscriptions"].append(subscription)
                    break

    out_path = "%s_churn_by_cohort_%s.csv" % (csv_path.split(".csv")[0], 
        datetime.datetime.now().strftime("%m_%d_%y_%s"))
    out_file = open(out_path, 'wb')
    writer = csv.writer(out_file, dialect = 'excel')
 
    periods = ["Period %d" % (x + 1) for x in xrange(
        (start_date - oldest_subscription_date).days / retention_period_size)
    ]
    columns = ["Cohort", "Total Subscriptions", "Total Churned", "Percent Retention", "Avg Subscription Length"]
    columns.extend(deepcopy(periods))
    writer.writerow(columns)

    for cohort in cohorts:
        cohorts[cohort]["churn_by_period"] = OrderedDict()
        total_subscriptions = len(cohorts[cohort]["subscriptions"])
        total_churned = 0
        total_subscription_length = 0
        period_start = cohorts[cohort]["cohort_start_date"]
        for period in periods:
            period_end = period_start + datetime.timedelta(retention_period_size)
            if start_date > period_start:
                cohorts[cohort]["churn_by_period"][period] = 0 
                period_start = period_end
            else:
                break
        for sub in cohorts[cohort]["subscriptions"]:
            if sub["state"] == "expired" or sub["state"] == "canceled":
                total_churned += 1
                subscription_length = sub["canceled_at"] - sub["activated_at"]
                total_subscription_length += subscription_length.days
                days_back = retention_period_size
                period_start = cohorts[cohort]["cohort_start_date"]
                for period in cohorts[cohort]["churn_by_period"]:
                    period_end = period_start + datetime.timedelta(retention_period_size)
                    if period_end <= start_date:
                        if sub["canceled_at"] <= period_end:
                            cohorts[cohort]["churn_by_period"][period] += 1
                        period_start = period_end
            else:
                total_subscription_length += (start_date - 
                    sub["activated_at"]).days
        if total_subscriptions > 0:
            avg_subscription_len = float(total_subscription_length)/float(total_subscriptions)
            percent_retention = float(total_subscriptions - total_churned)/float(total_subscriptions)
        else:
            avg_subscription_len = 0
            percent_retention = 0
        value_list = [cohort, total_subscriptions, total_churned, percent_retention, avg_subscription_len]
        for period in cohorts[cohort]["churn_by_period"]:
            if total_subscriptions > 0:
                percent_retention = float(
                        total_subscriptions - cohorts[cohort]["churn_by_period"][period])/float(total_subscriptions)
            else:
                percent_rention = 0
            value_list.append(percent_retention)
        writer.writerow(value_list)
    print "Your report has been generated: %s" % out_path

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description='Calculates retention by cohort and outputs the result to a CSV file')
    
    argparser.add_argument("-f", "--file", dest="file",
        help="Filename of subscriptions csv from exported from recurly")
    argparser.add_argument("-p", "--plan", dest="plan",
        help="Filter down to a specific subscription plan")
    argparser.add_argument("-c", "--cohort_size", dest="cohort_size",
        help="Define size of cohorts")
    argparser.add_argument("-r", "--retention_period_size", dest="retention_period_size",
        help="Define size of retention periods")
    argparser.add_argument("-s", "--start", dest="start_date",
        help="Define the start date of the period ")
    args = argparser.parse_args()
    arg_dict = {}

    if args.file:
        arg_dict["csv_path"] = args.file
    if args.cohort_size:
        arg_dict["cohort_size"] = int(args.cohort_size)
    if args.retention_period_size:
        arg_dict["retention_period_size"] = int(args.retention_period_size)
    if args.plan:
        arg_dict["plan_code"] = args.plan
    if args.start_date:
        arg_dict["start_date"] = parser.parse(args.start_date).replace(
                tzinfo=None)
    get_retention_by_cohort(**arg_dict)
