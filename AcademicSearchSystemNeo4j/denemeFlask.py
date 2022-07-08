from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable

class AppNeo4j:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def create_friendship(self, person1_name, person2_name):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self._create_and_return_friendship, person1_name, person2_name)
            for row in result:
                print("Created friendship between: {p1}, {p2}".format(p1=row['p1'], p2=row['p2']))

    @staticmethod
    def _create_and_return_friendship(tx, person1_name, person2_name):
        # To learn more about the Cypher syntax, see https://neo4j.com/docs/cypher-manual/current/
        # The Reference Card is also a good resource for keywords https://neo4j.com/docs/cypher-refcard/current/
        query = (
            "CREATE (p1:Person { name: $person1_name }) "
            "CREATE (p2:Person { name: $person2_name }) "
            "CREATE (p1)-[:KNOWS]->(p2) "
            "RETURN p1, p2"
        )
        result = tx.run(query, person1_name=person1_name, person2_name=person2_name)
        try:
            return [{"p1": row["p1"]["name"], "p2": row["p2"]["name"]}
                    for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def find_person(self, person_name, sec, ekip):
        with self.driver.session() as session:
            result = session.read_transaction(self._find_and_return_person, person_name, sec, ekip)
            for row in result:
                print("Found person: {row}".format(row=row))
            return result

    @staticmethod
    def _find_and_return_person(tx, person_name, sec, ekip):
        if(person_name != "1"):
            if ekip == "1":
                print("ekip")
                query = (
                    "MATCH p=(a)-[r:ekip]->(b:yayinlarr {YayinAdi: $person_name})-[c]->(d)"
                    # "MATCH (n:arastirmacirr) "
                    # "WHERE n.ArastirmaciAdi = $person_name "
                    # "RETURN n"
                    "RETURN a,b,d"
                )
                result = tx.run(query, person_name=person_name)
                return [[row[0]["ArastirmaciID"],row[0]["ArastirmaciAdi"],row[0]["ArastirmaciSoyadi"],row[1]["YayinAdi"],row[1]["YayinYili"],row[2]["Tur"],row[2]["Yer"]]  for row in result]
            else:
                query = (
                    "MATCH p = (a:arastirmacirr)-[r]->(b)-[c:CONTAIN1]->(d) "
                    # "MATCH (n:arastirmacirr) "
                    # "WHERE n.ArastirmaciAdi = $person_name "
                    # "RETURN n"
                    "RETURN a,b,d"
                )
            print(person_name)
            result = tx.run(query, person_name=person_name)
            if sec == "1":
                sec_text = "ArastirmaciID"
                sec_num = 0
            elif sec == "2":
                sec_text = "ArastirmaciAdi"
                sec_num = 0
            elif sec == "3":
                sec_text = "ArastirmaciSoyadi"
                sec_num = 0
            elif sec == "4":
                sec_text = "YayinAdi"
                sec_num = 1
            elif sec == "5":
                sec_text = "YayinYili"
                sec_num = 1
            elif sec == "6":
                sec_text = "Tur"
                sec_num = 2
            else :
                sec_text = "Yer"
                sec_num = 2
            print(sec_text)
            print(sec_num)
            print(sec)
            return [[row[0]["ArastirmaciID"],row[0]["ArastirmaciAdi"],row[0]["ArastirmaciSoyadi"],row[1]["YayinAdi"],row[1]["YayinYili"],row[2]["Tur"],row[2]["Yer"]]  for row in result if person_name in row[sec_num][sec_text]]
        print("Girdi == 1")

        query = (
            "MATCH p = (a:arastirmacirr)-[r]->(b)-[c:CONTAIN1]->(d) "
            #"MATCH (n:arastirmacirr) "
            #"WHERE n.ArastirmaciAdi = $person_name "
            #"RETURN n"
            "RETURN a,b,d"
        )
        print(person_name)
        result = tx.run(query, person_name=person_name)
        # [[row[0]["ArastirmaciID"],row[0]["ArastirmaciAdi"],row[0]["ArastirmaciSoyadi"],row[1]["YayinAdi"],row[1]["YayinYili"],row[2]["Tur"],row[2]["Yer"]]
        return [[row[0]["ArastirmaciID"],row[0]["ArastirmaciAdi"],row[0]["ArastirmaciSoyadi"],row[1]["YayinAdi"],row[1]["YayinYili"],row[2]["Tur"],row[2]["Yer"]]  for row in result]

    def createAc(self, a_id, a_ad, a_soyad, y_ad, y_yil, t_ad, t_yer, sec):
        with self.driver.session() as session:
            result = session.write_transaction(
                self.create_Ac, a_id, a_ad, a_soyad, y_ad, y_yil, t_ad, t_yer, sec)

            for row in result:
                print("Created person: {row}".format(row=row))

    @staticmethod
    def create_Ac(tx, a_id, a_ad, a_soyad, y_ad, y_yil, t_ad, t_yer, sec):
        if sec == "1":
            query0 = (
            "MATCH (a:arastirmacirr), (b:yayinlarr) WHERE a.ArastirmaciID = $a_id AND b.YayinAdi = $y_ad "
            "CREATE (a)-[r: ekip]->(b)"
            "RETURN a,b"
            )

            result0 = tx.run(query0, a_ad=a_ad, a_id=a_id, a_soyad=a_soyad, y_ad=y_ad, y_yil=y_yil, t_ad=t_ad, t_yer=t_yer)

            # [[row[0]["ArastirmaciID"],row[0]["ArastirmaciAdi"],row[0]["ArastirmaciSoyadi"],row[1]["YayinAdi"],row[1]["YayinYili"],row[2]["Tur"],row[2]["Yer"]]
            return [[row[0],row[1]]
                    for row in result0]

        query = (
            "MERGE (a:arastirmacirr {ArastirmaciAdi: $a_ad, ArastirmaciID: $a_id, ArastirmaciSoyadi: $a_soyad})"
            "MERGE (n:yayinlarr {YayinAdi: $y_ad, YayinYili: $y_yil})"
            "MERGE (c:turr {Tur: $t_ad, Yer: $t_yer})"
            "RETURN a,n,c"
        )
        result = tx.run(query, a_ad=a_ad, a_id=a_id, a_soyad=a_soyad, y_ad=y_ad, y_yil=y_yil, t_ad=t_ad, t_yer=t_yer)

        # iliski olusturma

        query1 = (
            "MATCH (a:arastirmacirr), (b:yayinlarr) WHERE a.ArastirmaciID = $a_id AND b.YayinAdi = $y_ad "
            "CREATE (a)-[r: CONTAIN1]->(b)"
            "RETURN a,b"
        )
        result1 = tx.run(query1, a_ad=a_ad, a_id=a_id, a_soyad=a_soyad, y_ad=y_ad, y_yil=y_yil, t_ad=t_ad, t_yer=t_yer)

        query2 = (
            "MATCH (a:yayinlarr),(b:turr) WHERE a.YayinAdi = $y_ad AND b.Tur = $t_ad "
            "CREATE (a)-[r: CONTAIN1]->(b)"
            "RETURN a,b"
        )
        result2 = tx.run(query2, a_ad=a_ad, a_id=a_id, a_soyad=a_soyad, y_ad=y_ad, y_yil=y_yil, t_ad=t_ad, t_yer=t_yer)

        # [[row[0]["ArastirmaciID"],row[0]["ArastirmaciAdi"],row[0]["ArastirmaciSoyadi"],row[1]["YayinAdi"],row[1]["YayinYili"],row[2]["Tur"],row[2]["Yer"]]
        return [[row[0]["ArastirmaciID"],row[0]["ArastirmaciAdi"],row[0]["ArastirmaciSoyadi"],row[1]["YayinAdi"],row[1]["YayinYili"],row[2]["Tur"],row[2]["Yer"]]
                for row in result]

    def ekipOlustur(self, a_id, y_ad):
        with self.driver.session() as session:
            result = session.write_transaction(
                self.ekipOlustur, a_id, y_ad)

            for row in result:
                print("Add Crew person: {row}".format(row=row))

    @staticmethod
    def ekipOlustur(tx, a_id, y_ad):
        query = (
            "MATCH (a:arastirmacirr), (b:yayinlarr) WHERE a.ArastirmaciID = $a_id AND b.YayinAdi = $y_ad "
            "CREATE (a)-[r: ekip]->(b)"
            "RETURN a,b"
        )
        print(a_id)
        print(y_ad)
        result = tx.run(query, a_id=a_id, y_ad=y_ad)

        # [[row[0]["ArastirmaciID"],row[0]["ArastirmaciAdi"],row[0]["ArastirmaciSoyadi"],row[1]["YayinAdi"],row[1]["YayinYili"],row[2]["Tur"],row[2]["Yer"]]
        return [[row[0],row[1]]
                for row in result]



app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = '1a2b3c4d5e'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_DB'] = 'login_register_pure_coding'

# Intialize MySQL
mysql = MySQL(app)

uri = "neo4j+s://6483a2ed.databases.neo4j.io"
user = "neo4j"
password = "R04v3VsdWSxBdpviGNoCxNpEFdXWpkynY2S0NDKF9X4"
appneo4j = AppNeo4j(uri, user, password)

# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests
@app.route('/', methods=['GET', 'POST'])
def login():
# Output message if something goes wrong...
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
                # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes

            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['email'] = account['email']
            session['password'] = account['password']

            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            flash("Incorrect username/password!", "danger")
    return render_template('auth/login.html',title="Login")



# http://localhost:5000/pythinlogin/register
# This will be the registration page, we need to use both GET and POST requests
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
                # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('SELECT * FROM accounts WHERE username = %s', (username))
        cursor.execute( "SELECT * FROM users WHERE username LIKE %s", [username] )
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            flash("Account already exists!", "danger")
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash("Invalid email address!", "danger")
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash("Username must contain only characters and numbers!", "danger")
        elif not username or not password or not email:
            flash("Incorrect username/password!", "danger")
        else:
        # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO users VALUES (NULL, %s, %s, %s)', (username,email, password))
            mysql.connection.commit()
            flash("You have successfully registered!", "success")
            return redirect(url_for('login'))

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash("Please fill out the form!", "danger")
    # Show registration form with message (if any)
    return render_template('auth/register.html',title="Register")

# http://localhost:5000/pythinlogin/home
# This will be the home page, only accessible for loggedin users

@app.route('/pythonlogin/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        if session['username'] == "admin":
            return render_template('home/home.html', username=session['username'], title="Home")
        else :
            return render_template('home/home_user.html', username=session['username'],title="Home")
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/pythonlogin/profile', methods=['GET', 'POST'])
def profile():

    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        #graphs = []
        #graphs.append(resAc)

        resAc_1 = appneo4j.find_person(person_name="1",sec="",ekip="")

        if request.method == 'POST' and 'araD' in request.form:
            resAc_1 = appneo4j.find_person(person_name=request.form['araD'],sec=request.form['sec'],ekip=request.form['ekip'])

        if session['username'] == "admin":
            return render_template('auth/profile.html',
                                   headings=["AkademikID ", "AkademikAD ", "AkademikSoyad ", "YayinAd ", "YayinYili ",
                                             "YayinTur ", "YayinYer "], data=resAc_1)

        else :
            return render_template('auth/profile_user.html',
                                   headings=["AkademikID ", "AkademikAD ", "AkademikSoyad ", "YayinAd ", "YayinYili ",
                                             "YayinTur ", "YayinYer "], data=resAc_1)

        #return render_template("auth/profile.html",list = graphs)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/pythonlogin/create_person', methods=['GET', 'POST'])
def create_person():

    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        #graphs = []
        #graphs.append(resAc)

        if request.method == 'POST' and 'akademikID' in request.form:
            print(request.form)
            appneo4j.createAc(request.form['akademikID'],request.form['akademikAd'],request.form['akademikSoyad'],
                              request.form['yayinAd'],request.form['yayinYili'],request.form['yayinTur'],
                              request.form['yayinYer'],request.form['sec'])

        resAc_1 = appneo4j.find_person(person_name="1",sec="",ekip="")

        return render_template('auth/create_person.html', headings=["AkademikID ","AkademikAD ","AkademikSoyad ","YayinAd ","YayinYili ","YayinTur ","YayinYer "], data=resAc_1)
        #return render_template("auth/profile.html",list = graphs)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# @app.route('/pythonlogin/ara', methods=['GET', 'POST'])
# def ara():
#
#     # Check if user is loggedin
#     if 'loggedin' in session:
#         # User is loggedin show them the home page
#         #graphs = []
#         #graphs.append(resAc)
#
#         resAc_1 = appneo4j.find_person(person_name="1")
#
#         if request.method == 'POST' and 'ara' in request.form:
#             resAc_1 = appneo4j.find_person(person_name=request.form['ara'])
#
#         return render_template('auth/profile.html', headings=["AkademikID ","AkademikAD ","AkademikSoyad ","YayinAd ","YayinYili ","YayinTur ","YayinYer "], data=resAc_1)
#         #return render_template("auth/profile.html",list = graphs)
#     # User is not loggedin redirect to login page
#     return redirect(url_for('login'))


if __name__ =='__main__':
	app.run(debug=True)