from datetime import datetime, timedelta
#1
now = datetime.now()
past = now-timedelta(days=5)
print(past)

print("\n")
#2
today = datetime.today()
tommorow = datetime.today()+timedelta(days=1)
yesterday = datetime.today()-timedelta(days=1)
print(yesterday)
print(today)
print(tommorow)

print("\n")
#3
def del_microsecs(now):
    now_without_milliseconds = now.replace(microsecond=0)
    print(now_without_milliseconds)

del_microsecs(now)
print("\n")
#4
def diff_in_seconds(t1,t2):
    res=t1-t2
    print(res.total_seconds())
t1=datetime.now()
t2 = datetime(2000,1,10,1,10,12)
diff_in_seconds(t1,t2)