import mysql.connector
from datetime import date, timedelta
import random

START_OF_WORKDAY = "08:00:00"
END_OF_WORKDAY = "15:00:00"

def main():
      
    #Connection
    mydb = mysql.connector.connect(
        host = "*****",
        user = "root",
        passwd = "*****",
        database = "sql_factory"
        )

    #Gets the employee table from the database.
    employee_cursor = mydb.cursor()
    employee_cursor.execute("SELECT * FROM employees")
    employees = employee_cursor.fetchall()
    employee_cursor.close()

    #Gets the work_steps table from the database.
    work_steps_cursor = mydb.cursor()
    work_steps_cursor.execute("SELECT * FROM work_steps")
    work_steps = work_steps_cursor.fetchall()
    work_steps_cursor.close()

    for employee in employees: #Iterates through employees.

        if int(employee[0][0]) != 1: #Skips for managers.
            continue

        else:
            time = START_OF_WORKDAY
            working = True #Keeps if we started or finished a workstep.
            work_step = work_steps[0] #Check in work step
            
            while(int(time[:2]) < int(END_OF_WORKDAY[:2])): #Goes on until end of workday.
                
                mycursor = mydb.cursor()
                
                if working:
                    working = False
                else:
                    work_step = start_work_step(work_steps)
                    working = True
                

                sql = "INSERT INTO work_log(_date, _time, work_id, employee_id, amount, trash, trash_reason, productivity, work_step_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                trash_amount = set_trash_amount(working, work_step)
                if working:
                    setTime = add_small_time(time)
                else:
                    setTime = time
                val = (get_yesterday_date(), setTime, work_step[0], employee[0], set_amount(working, work_step), trash_amount, set_reason(trash_amount, working), calculate_productivity(working, work_step), work_step[1])
                mycursor.execute(sql, val)

                if(working): #Makes next workstep start immediatly after previous done workstep.
                    time = set_time(time)
                
                if int(time[:2]) == int(END_OF_WORKDAY[:2]): #We need to check out
                    if(working): #If we are working on something we should report the amounts done before checking out.
                        working = False
                        sql = "INSERT INTO work_log(_date, _time, work_id, employee_id, amount, trash, trash_reason, productivity, work_step_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        trash_amount = set_trash_amount(working, work_step)
                        val = (get_yesterday_date(), time, work_step[0], employee[0], set_amount(working, work_step), trash_amount, set_reason(trash_amount, working), calculate_productivity(working, work_step), work_step[1])
                        mycursor.execute(sql, val)
                    
                    mycursor.execute("INSERT INTO work_log(_date, _time, work_id, employee_id, amount, trash, trash_reason, productivity, work_step_name) VALUES ('" + get_yesterday_date() + "','" + add_small_time(time) + "', '99999','" + employee[0] + "', '', '', '', '', 'Check out')")

                mydb.commit()
                mycursor.close()


#Returns current date.
def get_yesterday_date():
    yesterday = date.today() - timedelta(days = 1)
    return yesterday.strftime('%d-%m-%Y')

#Sets the times for each workstep.
def set_time(prev_time):
    
    if(int(prev_time[:2]) < 13):
        return format_time(int(prev_time[:2]) + random.randint(1, 3)) + ":" + format_time(random.randint(0, 59)) + ":" + format_time(random.randint(0, 59))
    elif (int(prev_time[:2]) == 13):
        return format_time(int(prev_time[:2]) + 1) + ":" + format_time(random.randint(0, 59)) + ":" + format_time(random.randint(0, 59))
    else:
        return format_time(int(prev_time[:2]) + 1) + ":" + format_time(random.randint(0, 15)) + ":" + format_time(random.randint(0, 59))

#Formats time in the form of x to 0x
def format_time(minute):
    if len(str(minute)) != 2:
        return "0" + str(minute)
    else:
        return str(minute)

#Adds a few minutes and seconds
def add_small_time(time):
    hour = time[0:2]
    second = str(int(time[-2:]) + random.randint(0, 59))
    while(int(second) >= 60):
        second = str(int(second) - random.randint(1, 30))
    
    minute = str(int(time[-5:-3]) + random.randint(1, 2))
    return hour + ":" + format_time(minute) + ":" + format_time(second)
    

#Chooses a random workstep
def start_work_step(work_steps):
    return work_steps[random.randint(2, len(work_steps) - 1)]

#Sets the amount when we are finished with a workstep.
def set_amount(working, work_step):
    if not working and int(work_step[0]) != 0: #int(work_step[0]) != 0 make sures that no amount is set for the Check in.
        return str(random.randint(7, 21))
    else:
        return ""

#Sets the trash amount we are finished with a workstep.
def set_trash_amount(working, work_step):
    chance = random.randint(0, 5)
    if chance == 0 and not working and not int(work_step[0]) == 0:
        return str(random.randint(1, 5))
    elif int(work_step[0]) == 0 or working:
        return ""
    else:    
        return "0"

#If there is trash we set a random reason.
def set_reason(trash_amount, working):
    reasons = ["Broken part", "Accident", "Failed test", "Other"]
    if trash_amount != "" and trash_amount != "0" and not working:
        return reasons[random.randint(0, len(reasons) - 1)]
    else:
        return ""

# "Calculate"
def calculate_productivity(working, work_step):
    if not working and int(work_step[0]) != 0:
        return str(random.randint(65, 120)) + "%"
    else:
        return ""


if __name__ == "__main__":
    main()


