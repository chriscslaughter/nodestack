import datetime, time

def utc_now():
  return datetime.datetime.now(datetime.timezone.utc)

def date_to_utc_datetime(date: datetime.date):
  dt = datetime.datetime.combine(date, datetime.time.min)
  dt = dt.replace(tzinfo=datetime.timezone.utc)
  return dt

def round_lattice(time_: datetime.datetime, granularity: int):
  utime = time_.timestamp()
  utime_ = utime + (-utime) % granularity
  start = datetime.datetime.fromtimestamp(utime_, datetime.timezone.utc)
  return start

def is_lattice(time_: datetime.datetime, granularity: int):
  return (time_ - round_lattice(time_, granularity)).total_seconds() == 0.0

def datetime_from_utc_timestamp(stamp):
  dt = datetime.datetime.utcfromtimestamp(stamp)
  dt = dt.replace(tzinfo=datetime.timezone.utc)
  return dt

def datetime_from_iso_8601(iso):
  if "+00:00" in iso:
    iso = iso.split("+")[0] + "Z"
  elif "Z" not in iso and "z" not in iso:
    iso = iso + "Z"
  iso = iso.upper()
  if '.' in iso:
    dt = datetime.datetime.strptime(iso, "%Y-%m-%dT%H:%M:%S.%fZ")
  else:
    dt = datetime.datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ")
  dt = dt.replace(tzinfo=datetime.timezone.utc)
  return dt

def clean_date(str_date):
  return date_to_utc_datetime(datetime.datetime.strptime(str_date, "%Y-%m-%d").date())

def clean_english_date(str_date):
  month, day, year = str_date.split(' ')
  day = day.replace(',', '')
  month = {
    "Jan": "01",
    "Feb": "02",
    "Mar": "03",
    "Apr": "04",
    "May": "05",
    "Jun": "06",
    "Jul": "07",
    "Aug": "08",
    "Sep": "09",
    "Oct": "10",
    "Nov": "11",
    "Dec": "12"
  }[month]
  return clean_date("{}-{}-{}".format(year, month, day))