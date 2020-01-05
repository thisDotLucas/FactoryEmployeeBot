import mysql.connector
from datetime import datetime
import random

START_OF_WORKDAY = "08:00"
END_OF_WORKDAY = "15:00"

def main():
      
    #Connection
    mydb = mysql.connector.connect(
        host = "factorymanager.cnkiejckzy7g.us-east-2.rds.amazonaws.com",
        user = "root",
        passwd = "038913641249",
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
                val = (get_today_date(), time, work_step[0], employee[0], set_amount(working, work_step), trash_amount, set_reason(trash_amount, working), calculate_productivity(working, work_step), work_step[1])
                mycursor.execute(sql, val)

                if(working): #Makes next workstep start immediatly after previous done workstep.
                    time = set_time(time)
                
                if int(time[:2]) == int(END_OF_WORKDAY[:2]): #We need to check out
                    if(working): #If we are working on something we should report the amounts done before checking out.
                        working = False
                        sql = "INSERT INTO work_log(_date, _time, work_id, employee_id, amount, trash, trash_reason, productivity, work_step_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        trash_amount = set_trash_amount(working, work_step)
                        val = (get_today_date(), time, work_step[0], employee[0], set_amount(working, work_step), trash_amount, set_reason(trash_amount, working), calculate_productivity(working, work_step), work_step[1])
                        mycursor.execute(sql, val)
                    
                    mycursor.execute("INSERT INTO work_log(_date, _time, work_id, employee_id, amount, trash, trash_reason, productivity, work_step_name) VALUES ('" + get_today_date() + "','" + time + "', '99999','" + employee[0] + "', '', '', '', '', 'Check out')")

                mydb.commit()
                mycursor.close()


#Returns current date.
def get_today_date():
    return datetime.today().strftime('%d-%m-%Y')

#Sets the times for each workstep.
def set_time(prev_time):
    
    if(int(prev_time[:2]) < 13):
        return format_time(int(prev_time[:2]) + random.randint(1, 3)) + ":" + format_time(random.randint(0, 59))
    elif (int(prev_time[:2]) == 13):
        return format_time(int(prev_time[:2]) + 1) + ":" + format_time(random.randint(0, 59))
    else:
        return format_time(int(prev_time[:2]) + 1) + ":" + format_time(random.randint(0, 15))

#Formats time in the form of x to 0x
def format_time(minute):
    if len(str(minute)) != 2:
        return "0" + str(minute)
    else:
        return str(minute)

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
    if chance == 0 and not working:
        return str(random.randint(1, 5))
    elif int(work_step[0]) == 0:
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


