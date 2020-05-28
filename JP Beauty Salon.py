import sqlite3
import flask
import random
from datetime import date

app = flask.Flask(__name__)

def get_db():
    db = sqlite3.connect('jpbeautysalon.db')
    return db

@app.route('/')
def home():
    return flask.render_template('index.html')

@app.route('/addmember')
def addmember():
    return flask.render_template("addmember.html")

@app.route('/addedmember', methods = ['POST'])
def addedmember():
    name = flask.request.form['name']
    email = flask.request.form['email']
    gender = flask.request.form['gender']
    contact = flask.request.form['contact']
    address = flask.request.form['address']

    output = ""
    add = True
    if "" in [name,email,gender,contact,address]:
        output += "Please fill in all blanks!\n"
        add = False

    if contact.isdigit() == False or len(contact) != 8:
        output += "Please enter a 8 digit SG mobile number!\n"
        add = False

    if add is True:
        output = "%s has become a member!"%(name)
        db = get_db()
        cursor = db.execute("SELECT COUNT(*) FROM Member")
        memberID = cursor.fetchall()[0][0] + 1
        db.execute('INSERT into Member (Name, Email, Gender, ContactNo, MemberID, Address) VALUES (?,?,?,?,?,?)',(name,email,gender,contact,memberID,address))
    
        db.commit()
        db.close()
    else:
        output += "Addition Failed! Please click on 'Add Another Member' to retry."

    return flask.render_template('addedmember.html',new_member = output)


@app.route('/updatemember')
def updatemember():
    return flask.render_template("updatemember.html")


@app.route('/updatedmember', methods = ['POST'])
def updatedmember():
    memberid = flask.request.form['MemberID']
    newemail = flask.request.form['newemail']
    newmobile = flask.request.form['newmobile']
    
    db = get_db()
    cursor = db.execute("SELECT COUNT(*) FROM Member")
    membercount = cursor.fetchall()[0][0]
    update = True
    output = ""
    #print(membercount)
    if memberid != "" and memberid.isdigit():
        if int(memberid) > membercount:
            output += "Member does not exist.\n"
            update = False
        if (newmobile.isdigit() == False or len(newmobile) != 8) and newmobile != "":
            output += "Please enter a 8 digit SG mobile number!\n"
            update = False
    else:
        output += "Please enter a MemberID.\n"
        update = False
        
    if update is True:
        db = get_db()
        cursor = db.execute("SELECT name FROM Member WHERE MemberID = ?",(int(memberid),))
        name = cursor.fetchall()[0][0]
        output = "%s's details have been updated!"%(name)
        if newemail != "":
            db.execute("UPDATE Member SET Email = ? WHERE MemberID = ?", (newemail, memberid))
            db.commit()
        if newmobile != "":
            db.execute("UPDATE Member SET ContactNo = ? WHERE MemberID = ?", (newmobile, memberid))
            db.commit()

    else:
        output += "Update Failed. Please click on 'Update Member' to retry."
    
    return flask.render_template('updatedmember.html',updatemsg = output)


@app.route('/addtransaction')
def addtransaction():
    db = get_db()
    cursor = db.execute("SELECT COUNT(*) FROM 'Transaction'")
    nooftransactions = cursor.fetchall()[0][0] 
    return flask.render_template("addtransaction.html", nooftransactions = nooftransactions)

@app.route('/addedtransaction', methods = ['POST'])
def addedtransaction():
    name = flask.request.form['name']
    db = get_db()
    create = True
    output = ""

    memberornot = flask.request.form['memberornot']
    services = flask.request.form.getlist('svc')
    costs = []
    cost = db.execute("SELECT Price from Services").fetchall()
    cost = [i[0] for i in cost]
    allsvc = db.execute("SELECT Service from Services").fetchall()
    allsvc = [i[0] for i in allsvc]
    #print(cost, allsvc)
    totalcost = 0.00
    
    for service in services:
        costs.append(cost[allsvc.index(service)])

    totalcost = sum(costs)

    if name == "":
        output += "Please enter a name.\n"
        create = False
    elif memberornot == "No":
        memberid = '0'
        discount = 0.00
    elif memberornot == "Yes":
        totalcost *= 0.9
        discount = totalcost/9
        memberid = flask.request.form['MemberID']
        cursor = db.execute("SELECT COUNT(*) FROM Member")
        membercount = cursor.fetchall()[0][0]
        if memberid == "" or memberid.isdigit() == False:
            output+="Please enter a MemberID.\n"
            create = False 
        elif int(memberid) > membercount:
            output += "Member does not exist.\n"
            create = False
        

    if create == True:    
        datedate = date.today()
    
        cursor = db.execute("SELECT COUNT(*) FROM 'Transaction'")
        invoiceno = cursor.fetchall()[0][0] + 1
        output = "%s's transaction has been recorded! Here is the invoice:"%(name)
        db.execute('INSERT into "Transaction" (Name, InvoiceNo, TotalAmount, Date, MemberID) VALUES (?,?,?,?,?)',(name,invoiceno,totalcost,datedate,memberid))
        db.commit()
        #services = ", ".join(services) #typo table
        for s in services:
            db.execute('INSERT into TransactionDetails (InvoiceNo, Service) VALUES (?, ?)',(invoiceno, s))
            db.commit()

        rows = []  
        for ind in range(0, len(costs)):
            rows.append([services[ind], "S$%s"%(costs[ind])])
        
    else:
        rows = []
        output += "Create Failed! Please click on 'Add Another Transaction' to retry."
        db.close()
        return flask.render_template('addedtransaction.html', createmsg = output, rows=rows, invoicenumber="nil", date="nil", name="nil", memberid="nil", discount="nil", payable="nil")
        
    db.close()

    
    discount = "S$"+str(discount)+"0"
    totalcost = "S$"+str(totalcost)+"0"
    
    return flask.render_template('addedtransaction.html', createmsg = output, rows=rows, invoicenumber=invoiceno, date=datedate, name=name, memberid=memberid, discount=discount, payable=totalcost)
    

@app.route('/viewtransaction')
def viewtransaction():
    return flask.render_template('viewtransaction.html')

@app.route('/viewingtransaction', methods = ['POST'])
def viewingtransaction():
    datedate = flask.request.form['datedate']
    db = get_db()
    rows = db.execute("SELECT * FROM 'Transaction' WHERE DATE = ?", (datedate,)).fetchall()    
    db.close()
    return flask.render_template('viewingtransaction.html', rows=rows)
    



@app.route('/viewrevenue')
def viewrevenue():
    return flask.render_template('viewrevenue.html')


@app.route('/viewingrevenue', methods = ['POST'])
def viewingrevenue():
    yearyear = flask.request.form['year']
    monthmonth = flask.request.form['month']
    display = True
    if "%s-%s-01"%(yearyear, monthmonth) > str(date.today()):
        display = False

    if display == True:
        if len(monthmonth) == 1:
            monthmonth = "0"+monthmonth
        lowerdate = "%s-%s-01"%(yearyear,monthmonth)
        if monthmonth == "12":
            monthmonth = "1"
            yearyear = str(int(yearyear)+1)
        else:
            monthmonth = str(int(monthmonth)+1) 
        if len(monthmonth) == 1:
            monthmonth = "0"+monthmonth
        upperdate = "%s-%s-01"%(yearyear,monthmonth)
        db = get_db()
        
        revenue = db.execute("SELECT SUM(TotalAmount) FROM 'Transaction' WHERE DATE < ? AND DATE >= ?", (upperdate,lowerdate)).fetchall()[0][0]
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    
        revenue = "%s Revenue: S$%s"%(months[int(monthmonth)-2],revenue)
        db.close()
    else:
        revenue = "Query failed."
    return flask.render_template('viewingrevenue.html', revenue=revenue)
    
@app.route('/viewhistory')
def viewhistory():
    return flask.render_template('viewhistory.html')

@app.route('/viewinghistory', methods = ['POST'])
def viewinghistory():
    memberid = flask.request.form['memberid']
    view = True
    db = get_db()
    cursor = db.execute("SELECT COUNT(*) FROM Member")
    membercount = cursor.fetchall()[0][0]
    historymsg = ""
    if int(memberid) != "" and memberid.isdigit():
        if int(memberid) > membercount:
            historymsg = "Member does not exist.\n"
            view = False
    else:
        historymsg = "Please enter a valid MemberID.\n"
        view=False
    if view == True:
        db = get_db()
        rows = db.execute("SELECT * FROM 'Transaction' WHERE MemberID = ?", (memberid,)).fetchall()
        name = db.execute("SELECT Name FROM Member WHERE MemberID = ?", (memberid, )).fetchall()[0][0]
        db.close()
        
        return flask.render_template('viewinghistory.html', rows=rows, historymsg="%s's transaction history."%(name))
    return flask.render_template('viewinghistory.html', rows=[], historymsg=historymsg)
rng = random.randint(1,20)
pork = 11000+rng

if __name__ == '__main__':
    app.run(port = pork, debug=False)

app.run(debug=False)




