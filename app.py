import numpy as np
from flask import Flask,request,jsonify,render_template,redirect,url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pickle
import email_validator
import sqlite3
import os
import jinja2
from plotly.offline import plot
import plotly.graph_objs as go
from plotly.graph_objs import Scatterpolar
from flask import Markup
import plotly.express as px
import pandas as pd

file_path = os.path.abspath(os.getcwd())+"\database.db"
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+file_path
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from app import db

db.metadata.clear()
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

#db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return '<h1>Invalid username or password</h1>'
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return '<h1>New user has been created!</h1>'
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup.html', form=form)

@app.route('/dashboard')
def dashboard():
    file=pd.read_csv('ST.csv')
    file2=pd.read_csv('cb.csv')
    file3=pd.read_csv('CM.csv')
    
    priceplot=plot(px.bar(file,x='age',y='value_eur',color='value_eur',title='Giá trị tiền đạo theo độ tuổi',template='plotly_white'),output_type='div')
    dataprice=[['15-19',753406],['20-23',2179141],['24-26',3295961],['27-30',3788079],['31-35',4142474],['36-39',1673511]]
    valueage=pd.DataFrame(dataprice,columns=['age','value'])
    meanpricelot=plot(px.bar(valueage,x='age',y='value',color='age',title='giá trị trung bình tiền đạo theo độ tuổi',template='plotly_white'),output_type='div')
    
    cbplot=plot(px.bar(file2,x='age',y='value_eur',color='value_eur',title='Giá trị hậu vệ theo độ tuổi',template='plotly_white'),output_type='div')
    cbdataprice=[['15-19',721185],['20-23',1807811],['24-26',2984756],['27-30',2870351],['31-35',2054562],['36-39',3072727]]
    cbvalueage=pd.DataFrame(cbdataprice,columns=['age','value'])
    cbmeanpricelot=plot(px.bar(cbvalueage,x='age',y='value',color='age',title='giá trị trung bình hậu vệ theo độ tuổi',template='plotly_white'),output_type='div')

    cmplot=plot(px.bar(file2,x='age',y='value_eur',color='value_eur',title='Giá trị tiền vệ theo độ tuổi',template='plotly_white'),output_type='div')
    cmdataprice=[['15-19',683832],['20-23',2560044],['24-26',4049088],['27-30',4166879],['31-35',2586337],['36-39',426428]]
    cmvalueage=pd.DataFrame(cmdataprice,columns=['age','value'])
    cmmeanpricelot=plot(px.bar(cmvalueage,x='age',y='value',color='age',title='giá trị trung bình tiền vệ theo độ tuổi',template='plotly_white'),output_type='div')

    return render_template('dashboard.html',priceholder=Markup(priceplot),priceholder2=Markup(meanpricelot),cbholder=Markup(cbplot),
    cbholder2=Markup(cbmeanpricelot),cmholder=Markup(cmplot),cmholder2=Markup(cmmeanpricelot))

@app.route('/chose')
@login_required
def chose():
    return render_template('chose.html')

@app.route('/cbmodel1',methods=['POST'])
def cbmodel1():
    model3=pickle.load(open('cbmodel.pkl','rb'))
    int_features = [int(x) for x in request.form.values()]
    final_features = [np.array(int_features)]
    prediction = model3.predict(final_features)
    output = round(prediction[0], 2)

    df = pd.DataFrame(dict(
    r=int_features[1:],
    theta=['Phong độ','Tiềm năng','Phòng thủ','Tì đè','Tắc bóng','Xoạc bóng',
                            'Chính xác','Đánh đầu','Sức mạnh']))
    myplot=plot(px.line_polar(df,r='r',theta='theta',line_close=True),output_type='div')

    if(output<0):
       return render_template('cbpredictprice.html',cbprediction_text='Giá trị cầu thủ quá nhỏ để định giá')
    else:
       return render_template('cbpredictprice.html',cbdiv_placeholder=Markup(myplot), cbprediction_text='Giá trị của cầu thủ là:  {} euro'.format(output))

@app.route('/cbmodel2',methods=['POST'])
def cbmodel2():
    model4=pickle.load(open('cbmodel2.pkl','rb'))
    int_features = [int(x) for x in request.form.values()]
    final_features = [np.array(int_features)]
    prediction = model4.predict(final_features)

    output = round(prediction[0], 2)

    df = pd.DataFrame(dict(
    r=int_features[1:],
    theta=['Phong độ','Phòng thủ','Tì đè','Tắc bóng','Xoạc bóng',
                            'Chính xác','Đánh đầu','Sức mạnh']))
    myplot=plot(px.line_polar(df,r='r',theta='theta',line_close=True),output_type='div')


    
    if(output<70):
       return render_template('cbpredictpotential.html',cbdiv_placeholder=Markup(myplot), cbprediction_text='Hậu vệ thuộc dạng trung bình yếu trong tương lai {}/99'.format(output))
    if(output>=70) and (output <75):
        return render_template('cbpredictpotential.html',cbdiv_placeholder=Markup(myplot) ,cbprediction_text='Hậu vệ thuộc dạng trung bình trong tương lai  {}/99'.format(output))
    if(output>=75) and (output<80):
        return render_template('cbpredictpotential.html',cbdiv_placeholder=Markup(myplot),cbprediction_text='Hậu vệ thuộc dạng trung bình khá trong tương lai {}/99'.format(output))
    if(output>=80) and (output<84):
        return render_template('cbpredictpotential.html',cbdiv_placeholder=Markup(myplot),cbprediction_text='Hậu vệ thuộc dạng khá trong tương lai {}/99'.format(output))
    if(output>=84) and (output<87):
        return render_template('cbpredictpotential.html',cbdiv_placeholder=Markup(myplot),cbprediction_text='Hậu vệ thuộc dạng giỏi trong tương lai {}/99'.format(output))
    if(output>=87) and (output<=90):
        return render_template('cbpredictpotential.html',cbdiv_placeholder=Markup(myplot),cbprediction_text='Hậu vệ thuộc dạng siêu sao trong tương lai {}/99'.format(output))
    if(output>=90) :
        return render_template('cbpredictpotential.html',cbdiv_placeholder=Markup(myplot),cbprediction_text='Hậu vệ thuộc dạng huyền thoại trong tương lai {}/99'.format(output))
    

@app.route('/predictprice')
def predictprice():
    return render_template('predictprice.html')

@app.route('/cbpredictprice')
def cbpredictprice():
    return render_template('cbpredictprice.html')

@app.route('/cbpredictpotential')
def cbpredictpotential():
    return render_template('cbpredictpotential.html')


@app.route('/predictpotential')
def predictpotential():
    return render_template('predictpotential.html')

@app.route('/model2',methods=['POST'])
def model2():
    model2=pickle.load(open('model2.pkl','rb'))
    int_features = [int(x) for x in request.form.values()]
    final_features = [np.array(int_features)]
    prediction = model2.predict(final_features)

    output = round(prediction[0], 2)

    df = pd.DataFrame(dict(
    r=int_features[1:],
    theta=['Phong độ','Tốc độ','Dứt điểm','Tì đè','Sút chính xác','Đánh đầu',
                            'Tăng tốc','Thăng bằng','Lực sút']))
    myplot=plot(px.line_polar(df,r='r',theta='theta',line_close=True),output_type='div')


    
    if(output<70):
       return render_template('predictpotential.html',div_placeholder=Markup(myplot), prediction_text='Tiền đạo thuộc dạng trung bình yếu trong tương lai {}/99'.format(output))
    if(output>=70) and (output <75):
        return render_template('predictpotential.html',div_placeholder=Markup(myplot) ,prediction_text='Tiền đạo thuộc dạng trung bình trong tương lai {}/99'.format(output))
    if(output>=75) and (output<80):
        return render_template('predictpotential.html',div_placeholder=Markup(myplot),prediction_text='Tiền đạo thuộc dạng trung bình khá trong tương lai {}/99'.format(output))
    if(output>=80) and (output<84):
        return render_template('predictpotential.html',div_placeholder=Markup(myplot),prediction_text='Tiền đạo thuộc dạng khá trong tương lai {}/99'.format(output))
    if(output>=84) and (output<87):
        return render_template('predictpotential.html',div_placeholder=Markup(myplot),prediction_text='Tiền đạo thuộc dạng giỏi trong tương lai {}/99'.format(output))
    if(output>=87) and (output<=90):
        return render_template('predictpotential.html',div_placeholder=Markup(myplot),prediction_text='Tiền đạo thuộc dạng siêu sao trong tương lai {}/99'.format(output))
    if(output>=90) :
        return render_template('predictpotential.html',div_placeholder=Markup(myplot),prediction_text='Tiền đạo thuộc dạng huyền thoại trong tương lai {}/99'.format(output))
    

@app.route('/model1',methods=['POST'])
def model1():
    model=pickle.load(open('model.pkl','rb'))
    int_features = [int(x) for x in request.form.values()]
    final_features = [np.array(int_features)]
    prediction = model.predict(final_features)
    output = round(prediction[0], 2)

    df = pd.DataFrame(dict(
    r=int_features[1:],
    theta=['Phong độ','Tiềm năng','Tốc độ','Dứt điểm','Tì đè','Sút chính xác','Đánh đầu',
                            'Tăng tốc','Thăng bằng','Lực sút']))
    myplot=plot(px.line_polar(df,r='r',theta='theta',line_close=True),output_type='div')

    if(output<0):
       return render_template('predictprice.html',prediction_text='Giá trị cầu thủ quá nhỏ để định giá')
    else:
       return render_template('predictprice.html',div_placeholder=Markup(myplot), prediction_text='Giá trị của cầu thủ là:  {} euro'.format(output))

@app.route('/results2',methods=['POST'])
def results2():
    data2 = request.get_json(force=True)
    prediction2 = model2.predict([np.array(list(data.values()))])

    output = prediction2[0]
    return jsonify(output)

@app.route('/results',methods=['POST'])
def results():

    data = request.get_json(force=True)
    prediction = model.predict([np.array(list(data.values()))])

    output = prediction[0]
    return jsonify(output)

@app.route('/cbresults',methods=['POST'])
def cbresults():

    data3 = request.get_json(force=True)
    prediction = model3.predict([np.array(list(data.values()))])

    output = prediction[0]
    return jsonify(output)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)