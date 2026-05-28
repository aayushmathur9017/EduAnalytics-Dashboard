from flask import jsonify, request
from email.mime import message
from google import genai
from flask_jwt_extended import (

    JWTManager,

    create_access_token,

    jwt_required,

    get_jwt_identity

)
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from flask_mail import (
    Mail,
    Message
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    send_file,
    flash,
    jsonify
)

from flask_sqlalchemy import SQLAlchemy

from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user
)

import pandas as pd
import plotly.express as px

app = Flask(__name__)
client = genai.Client(

    api_key="AIzaSyA5Ey03GfHT5RkT5QLdACOu0G_nhl1Y02k"

)


app.config['JWT_SECRET_KEY'] = 'eduanalytics_secret_key'

jwt = JWTManager(app)
# AI TRAINING DATA

training_data = [

    [95, 90, 92, 96, 3],
    [88, 85, 84, 90, 2],
    [70, 65, 60, 75, 1],
    [45, 40, 50, 60, 0],
    [30, 35, 25, 50, 0],
    [78, 80, 75, 85, 2],
    [92, 95, 90, 98, 3]

]

X = [
    data[:4]
    for data in training_data
]

y = [
    data[4]
    for data in training_data
]



app.secret_key = "student_secret_key"
UPLOAD_FOLDER = 'uploads'
# EMAIL CONFIG

app.config['MAIL_SERVER'] = 'smtp.gmail.com'

app.config['MAIL_PORT'] = 587

app.config['MAIL_USE_TLS'] = True

app.config['MAIL_USERNAME'] = 'aayushmathur006@gmail.com'

app.config['MAIL_PASSWORD'] = 'qgjv otuo imcp rerj'

mail = Mail(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# DATABASE CONFIG

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'

db = SQLAlchemy(app)

# LOGIN MANAGER

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"
# ACTIVITY LOG MODEL

class ActivityLog(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    action = db.Column(
        db.String(200)
    )

# USER MODEL

class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True
    )

    password = db.Column(
        db.String(100)
    )

# STUDENT MODEL

class Student(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100)
    )

    username = db.Column(
        db.String(100),
        unique=True
    )

    password = db.Column(
        db.String(100)
    )

    maths = db.Column(
        db.Integer
    )

    science = db.Column(
        db.Integer
    )

    english = db.Column(
        db.Integer
    )

    attendance = db.Column(
        db.Integer
    )
# USER LOADER

@login_manager.user_loader
def load_user(user_id):

    return User.query.get(
        int(user_id)
    )

# LOGIN ROUTE

@app.route('/login', methods=['GET', 'POST'])

def login():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:

            login_user(user)

            return redirect('/')

    return render_template('login.html')
# STUDENT LOGIN

@app.route('/student_login', methods=['GET', 'POST'])

def student_login():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        student = Student.query.filter_by(

            username=username,

            password=password

        ).first()

        if student:

            return redirect(

                f'/student_dashboard/{student.id}'
            )

    return render_template(
        'student_login.html'
    )
    # STUDENT DASHBOARD

@app.route('/student_dashboard/<int:id>')

def student_dashboard(id):

    student = Student.query.get(id)

    average = round(

        (
            student.maths +
            student.science +
            student.english
        ) / 3,

        2
    )

    prediction = (

        'Pass'

        if average >= 50

        else 'Fail'
    )

    return render_template(

        'student_dashboard.html',

        student=student,

        average=average,

        prediction=prediction
    )

# LOGOUT ROUTE

@app.route('/logout')

@login_required
def logout():

    logout_user()

    return redirect('/login')

# HOME ROUTE

@app.route('/')

@login_required
def home():

    students = Student.query.all()
    activities = ActivityLog.query.order_by(
    ActivityLog.id.desc()
).limit(5).all()

    data = []

    for student in students:

        average = round(

            (
                student.maths +
                student.science +
                student.english
            ) / 3,

            2
        )
         
        if average >= 90:
            ai_level= "Excellent"
        elif average >= 75:
            ai_level= "Good"                    
        elif average >= 50:
            ai_level= "Average"
        else:
            ai_level= "Needs Improvement"       
        data.append({

            'id': student.id,

            'Name': student.name,

            'Maths': student.maths,

            'Science': student.science,

            'English': student.english,

            'Attendance': student.attendance,

            'Average': average,
            
            'AI_Level': ai_level,
            'Prediction': (
                'Pass'
                if average >= 50
                else 'Fail'
            )
        })
    df = pd.DataFrame(data)

    # EMPTY CHECK

    if df.empty:

        return render_template(

            'index.html',

            average=0,
            topper="No Data",
            total_students=0,
            weak_count=0,
            chart="",
            students=[],
            pass_percentage=0,
            fail_percentage=0,
            best_subject="No Data",
            weak_attendance=0,
            pie_chart=""
        )

    # RANK SYSTEM

    df['Rank'] = df['Average'].rank(

        ascending=False,

        method='dense'

    ).astype(int)

    # UPDATE RANK IN DATA

    for i in range(len(data)):

        data[i]['Rank'] = int(
            df.iloc[i]['Rank']
        )
        # TOP 3 STUDENTS

    top_students = df.sort_values(

    by='Average',

    ascending=False

).head(3).to_dict(
    orient='records'
)
     
    # DASHBOARD DATA

    class_average = round(
        df['Average'].mean(),
        2
    )

    topper = df.loc[
        df['Average'].idxmax(),
        'Name'
    ]

    weak_students = df[
        df['Average'] < 50
    ]

    # ANALYTICS INSIGHTS

    pass_percentage = round(

        (
            len(df[df['Average'] >= 50])
            / len(df)
        ) * 100,

        2
    )

    fail_percentage = round(

        (
            len(df[df['Average'] < 50])
            / len(df)
        ) * 100,

        2
    )

    subject_averages = {

        'Maths': df['Maths'].mean(),

        'Science': df['Science'].mean(),

        'English': df['English'].mean()
    }

    best_subject = max(
        subject_averages,
        key=subject_averages.get
    )

    weak_attendance = len(
        df[df['Attendance'] < 75]
    )
    # AI INSIGHTS

    ai_insights = []

    if class_average >= 75:

     ai_insights.append(
        "Overall class performance is excellent."
     )

    elif class_average >= 50:

     ai_insights.append(
        "Overall class performance is average."
     )
    else:

     ai_insights.append(
        "Class performance needs improvement."
    )   
        
    
     
    # MAIN BAR CHART

    fig = px.bar(

        df,

        x='Name',
        y='Average',

        color='Average',

        text='Average',

        title='Student Performance Analysis',

        template='plotly_dark'
    )

    chart = fig.to_html(
        full_html=False
    )

    # PASS FAIL PIE CHART

    pie_df = pd.DataFrame({

        'Result': [

            'Pass',
            'Fail'
        ],

        'Count': [

            len(df[df['Average'] >= 50]),

            len(df[df['Average'] < 50])
        ]
    })

    pie_fig = px.pie(

        pie_df,

        names='Result',

        values='Count',

        title='Pass vs Fail Ratio',

        template='plotly_dark'
    )

    pie_chart = pie_fig.to_html(
        full_html=False
    )

    return render_template(

        'index.html',

        average=class_average,

        topper=topper,

        total_students=len(df),

        weak_count=len(weak_students),

        chart=chart,

        students=data,

        pass_percentage=pass_percentage,

        fail_percentage=fail_percentage,

        best_subject=best_subject,

        weak_attendance=weak_attendance,

        pie_chart=pie_chart,
top_students=top_students,

ai_insights=ai_insights,
activities=activities

    )
# CSV UPLOAD

@app.route('/upload_csv', methods=['POST'])

@login_required

def upload_csv():

    file = request.files['file']

    if file:

        filepath = f"{app.config['UPLOAD_FOLDER']}/{file.filename}"

        file.save(filepath)

        df = pd.read_csv(filepath)

        for _, row in df.iterrows():

            student = Student(

                name=row['Name'],

                maths=row['Maths'],

                science=row['Science'],

                english=row['English'],

                attendance=row['Attendance']
            )

            db.session.add(student)
        log = ActivityLog(
           action="CSV file uploaded"
       )

        db.session.add(log)
        db.session.commit()

        flash("CSV Uploaded Successfully!")

    return redirect('/')
# ADD STUDENT

@app.route('/add', methods=['POST'])

def add_student():

    new_student = Student(

        name=request.form['name'],
        
        username=request.form['username'],
        
        password=request.form['password'],

        maths=request.form['maths'],

        science=request.form['science'],

        english=request.form['english'],

        attendance=request.form['attendance']
    )

    db.session.add(new_student)

    # ACTIVITY LOG

    log = ActivityLog(
        action=f"{request.form['name']} added"
    )

    db.session.add(log)

    # EMAIL ALERT

    msg = Message(

        'Student Performance Alert',

        sender=app.config['MAIL_USERNAME'],

        recipients=[
            app.config['MAIL_USERNAME']
        ]
    )

    msg.body = f"""

New student added:

Name:
{request.form['name']}

Maths:
{request.form['maths']}

Science:
{request.form['science']}

English:
{request.form['english']}

Attendance:
{request.form['attendance']}
"""

    mail.send(msg)

    db.session.commit()

    flash("Student Added Successfully!")

    return redirect('/')

# EDIT STUDENT

@app.route('/edit/<int:id>', methods=['GET', 'POST'])

def edit_student(id):

    student = Student.query.get(id)

    if request.method == 'POST':

        student.name = request.form['name']

        student.maths = request.form['maths']

        student.science = request.form['science']

        student.english = request.form['english']

        student.attendance = request.form['attendance']
        log = ActivityLog(
            action=f"{student.name} updated"
        )

        db.session.add(log)
        db.session.commit()

        return redirect('/')

    return render_template(
        'edit.html',
        student=student
    )
# STUDENT PROFILE PAGE

@app.route('/student/<int:id>')

@login_required

def student_profile(id):

    student = Student.query.get(id)

    average = round(

        (
            student.maths +
            student.science +
            student.english
        ) / 3,

        2
    )

    prediction = (

        "Pass"
        if average >= 50
        else "Fail"
    )

    return render_template(

        'student_profile.html',

        student=student,

        average=average,

        prediction=prediction
    )
# DELETE STUDENT

@app.route('/delete/<int:id>')

def delete_student(id):

    student = Student.query.get(id)
    log = ActivityLog(
        action=f"{student.name} deleted"
    )

    db.session.add(log)

    db.session.delete(student)

    db.session.commit()

    return redirect('/')

# EXPORT EXCEL

@app.route('/export')

@login_required
def export_excel():

    students = Student.query.all()

    data = []

    for student in students:

        average = round(

            (
                student.maths +
                student.science +
                student.english
            ) / 3,

            2
        )

        data.append({

            'Name': student.name,

            'Maths': student.maths,

            'Science': student.science,

            'English': student.english,

            'Attendance': student.attendance,

            'Average': average
        })

    df = pd.DataFrame(data)

    file_path = 'student_report.xlsx'

    df.to_excel(
        file_path,
        index=False
    )

    return send_file(
        file_path,
        as_attachment=True
    )

# PDF REPORT

@app.route('/pdf_report')

@login_required
def pdf_report():

    students = Student.query.all()

    pdf_file = "student_report.pdf"

    doc = SimpleDocTemplate(pdf_file)

    styles = getSampleStyleSheet()

    elements = []

    title = Paragraph(
        "Student Performance Report",
        styles['Title']
    )

    elements.append(title)

    elements.append(
        Spacer(1, 20)
    )

    data = [[

        'Name',
        'Maths',
        'Science',
        'English',
        'Attendance',
        'Average'
    ]]

    for student in students:

        average = round(

            (
                student.maths +
                student.science +
                student.english
            ) / 3,

            2
        )

        data.append([

            student.name,

            student.maths,

            student.science,

            student.english,

            student.attendance,

            average
        ])

    table = Table(data)

    table.setStyle(

        TableStyle([

            ('BACKGROUND', (0,0), (-1,0), colors.grey),

            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),

            ('ALIGN', (0,0), (-1,-1), 'CENTER'),

            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),

            ('BOTTOMPADDING', (0,0), (-1,0), 12),

            ('BACKGROUND', (0,1), (-1,-1), colors.beige),

            ('GRID', (0,0), (-1,-1), 1, colors.black)

        ])
    )

    elements.append(table)

    doc.build(elements)

    return send_file(
        pdf_file,
        as_attachment=True
    )
# API - ALL STUDENTS

@app.route('/api/students')

def api_students():

    students = Student.query.all()

    data = []

    for student in students:

        average = round(

            (
                student.maths +
                student.science +
                student.english
            ) / 3,

            2
        )

        data.append({

            'id': student.id,

            'name': student.name,

            'maths': student.maths,

            'science': student.science,

            'english': student.english,

            'attendance': student.attendance,

            'average': average
        })

    return jsonify(data)

# API - TOPPER

@app.route('/api/topper')

def api_topper():

    students = Student.query.all()

    topper = None

    highest = 0

    for student in students:

        average = (
            student.maths +
            student.science +
            student.english
        ) / 3

        if average > highest:

            highest = average

            topper = {

                'name': student.name,

                'average': round(
                    average,
                    2
                )
            }

    return jsonify(topper)

# API - ANALYTICS

@app.route('/api/analytics')

def api_analytics():

    students = Student.query.all()

    total_students = len(students)

    weak_students = 0

    for student in students:

        average = (
            student.maths +
            student.science +
            student.english
        ) / 3

        if average < 50:

            weak_students += 1

    return jsonify({

        'total_students': total_students,

        'weak_students': weak_students
    })

# CREATE DATABASE

with app.app_context():

    db.create_all()

    if not User.query.filter_by(
        username='admin'
    ).first():

        admin = User(
            username='admin',
            password='admin123'
        )

        db.session.add(admin)

        db.session.commit()

# RUN APP
# DASHBOARD PAGE

@app.route('/dashboard')

def dashboard_page():

    students = Student.query.all()

    total_students = len(students)

    if total_students > 0:

        averages = []

        topper_name = ""

        highest_average = 0

        for student in students:

            avg = (

                student.maths +

                student.science +

                student.english

            ) / 3

            averages.append(avg)

            if avg > highest_average:

                highest_average = avg

                topper_name = student.name

        class_average = round(

            sum(averages) / total_students,

            2

        )

    else:

        class_average = 0

        topper_name = "No Data"

    return render_template(

        'dashboard.html',

        average=class_average,

        topper=topper_name

    )

    students=students,

    average=0,
    topper="No Data",
    total_students=len(students),
    weak_count=0,
    chart=""
    
    


# REPORTS PAGE

@app.route('/reports')

@login_required
def reports_page():

    activities = ActivityLog.query.order_by(
        ActivityLog.id.desc()
    ).limit(5).all()

    return render_template(

        'reports.html',

        activities=activities
    )


# SETTINGS PAGE

@app.route('/settings')

@login_required
def settings_page():

    return render_template(
        'settings.html'
    )
    # API PAGE

@app.route('/api_page')

@login_required
def api_page():

    return render_template(
        'api.html'
    )
    # AI INSIGHTS PAGE

@app.route('/ai_insights')

@login_required
def ai_insights_page():

    return render_template(
        'ai_insights.html'
    )
# =========================
# STUDENTS PAGE
# =========================

@app.route('/students')

@login_required
def students_page():

    students = Student.query.all()

    return render_template(

        'students.html',

        students=students
    )


# =========================
# ANALYTICS PAGE
# =========================

@app.route('/analytics')

@login_required
def analytics_page():

    return render_template(

        'analytics.html',

        pass_percentage=0,
        fail_percentage=0,
        best_subject="N/A",
        weak_attendance=0,
        pie_chart=""
    )


# =========================
# RUN APP
# =========================
# =========================
# JWT LOGIN API
# =========================

@app.route('/api/login', methods=['POST'])

def api_login():

    username = request.json.get('username')

    password = request.json.get('password')

    user = User.query.filter_by(
        username=username
    ).first()

    if user and user.password == password:

        access_token = create_access_token(
            identity=username
        )

        return jsonify({

            'token': access_token

        })

    return jsonify({

        'message': 'Invalid credentials'

    }), 401
    # =========================
# PROTECTED JWT API
# =========================

@app.route('/api/protected')

@jwt_required()
def protected():

    current_user = get_jwt_identity()

    return jsonify({

        'message':
        f'Welcome {current_user}',

        'status': 'Authorized'

    })
@app.route('/chatbot', methods=['POST'])

def chatbot():

    data = request.get_json()

    message = data.get(
        'message',
        ''
    ).lower()

    if "topper" in message:

        reply = (
            "🏆 Topper is Aayush."
        )

    elif "attendance" in message:

        reply = (
            "📉 Low attendance students detected."
        )

    elif "ai" in message:

        reply = (
            "🤖 AI means Artificial Intelligence."
        )

    elif "python" in message:

        reply = (
            "🐍 Python is a programming language."
        )

    else:

        reply = (
            "🤖 Ask me about topper, AI, "
            "attendance or Python."
        )

    return jsonify({

        'reply': reply

    })
if __name__ == '__main__':

    app.run(

    host='0.0.0.0',

    port=5000,

    debug=True

)