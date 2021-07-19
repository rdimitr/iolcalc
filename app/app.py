# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, flash, Markup, jsonify, redirect, url_for

from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField, BooleanField, PasswordField, IntegerField, TextField,\
    FormField, SelectField, FieldList, FloatField, TextAreaField
from wtforms.validators import DataRequired, Length, Regexp
#from wtforms.widgets.html5 import NumberInput
from wtforms.fields import *

from flask_bootstrap import Bootstrap
#from flask_sqlalchemy import SQLAlchemy

import csv
import hashlib
from calc import getPowerIOL, is_number

app = Flask(__name__)
app.secret_key = 'dev'

app.config['BOOTSTRAP_BTN_STYLE'] = 'primary'
app.config['BOOTSTRAP_BTN_SIZE'] = 'sm'

bootstrap = Bootstrap(app)
csrf = CSRFProtect(app)

IOLdictionary = []
AconstDictionary = []


def readIOLs():
    IOLdict = []
    AconstDict = []

    with open('.\data\LensesDot.csv') as f:
         reader = csv.reader(f, delimiter=':')
         for row in reader:
             if row: 
                IOLdict.append((row[0],row[1]))
                AconstDict.append((row[0],row[2]))
    return IOLdict, AconstDict
    
    
def readTextIOLs():    
    try:
        with open('.\data\LensesDot.csv', 'r') as f:
             cont_txt = f.read()
    except Exception:
        cont_txt = ""
    finally:
        f.close()
    return cont_txt

                

class AuthForm(FlaskForm):
    usertxt = StringField('Пользователь', validators=[DataRequired(), Length(8, 150)])
    passtxt = PasswordField('Пароль', validators=[DataRequired(), Length(8, 150)])
    submit = SubmitField(label="Войти")


class IolForm(FlaskForm):
    k1_field = FloatField(label="Длина глаза, мм", validators=[DataRequired()], default=0)
    k2_field = FloatField(label="Планируемая рефракция, D", validators=[DataRequired()], default=0)
    k3_field = FloatField(label="Меридиан 1, D", validators=[DataRequired()], default=0)
    k4_field = FloatField(label="Меридиан 2, D", validators=[DataRequired()], default=0)
    iol_list1 = SelectField(label="Вариант линзы №1", choices=IOLdictionary)
    iol_list2 = SelectField(label="Вариант линзы №2", choices=IOLdictionary)
    submit = SubmitField(label="Расчет")
	
	
class ResCalcForm(FlaskForm):
    #res_iol_calc = TextAreaField(label="", default="<h1>HELLO</h1>")
    back = SubmitField(label="Новый расчет")
    
    
class SettingsForm(FlaskForm):
    #iols_field = TextAreaField("Редактирование списка ИОЛ", default="", render_kw={'class': 'form-control', 'rows': 20})
    iols_field = TextAreaField("Редактирование списка ИОЛ", render_kw={'class': 'form-control', 'rows': 20})
    savebutton = SubmitField(label="Сохранить")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/iol', methods=['GET', 'POST'])
def iol_func():
    iol_form = IolForm()
    IOLdictionary, AconstDictionary = readIOLs()
    iol_form.iol_list1.choices = IOLdictionary
    iol_form.iol_list2.choices = IOLdictionary
    return render_template('iol.html', form=iol_form)   
    

@app.route('/settings', methods=['GET', 'POST'])
def settings_func():
    if request.method == "POST":
       req = request.form
       iols_text = str(request.form.get("iols_field"))
       correct_text = iols_text.replace("\n", "")
       try:
          f = open('.\data\LensesDot.csv', 'w')
          f.write(correct_text)
          f.close()
       except Exception:
          f.close()
          return redirect(url_for('test_flash', id_mess=4))
    
       f.close()
       return redirect(url_for('test_flash', id_mess=3))
       
    set_form = SettingsForm()
    content = readTextIOLs()
    set_form.iols_field.data = content
    return render_template('set.html', form=set_form , render_kw={'class': 'form-control', 'value': '20'})  


@app.route('/auth', methods=['GET', 'POST'])
def authentification():
    if request.method == "POST":
        req = request.form
        usr_text = str(request.form.get("usertxt"))
        psw_text = str(request.form.get("passtxt"))
        if (hashlib.md5(usr_text.encode()).hexdigest() != "21232f297a57a5a743894a0e4a801fc3")\
           or (hashlib.md5(psw_text.encode()).hexdigest() != "2d40873337540a22414fb1f7b4308544"):
              return redirect(url_for('test_flash', id_mess=1)) 
        else:
           return redirect(url_for('settings_func'))
    auth_form = AuthForm()	
    return render_template('auth.html', form=auth_form) 


@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    if request.method == "POST":
        req = request.form
	
    res_calc_form = ResCalcForm()
    listIOL=["",""]
    const1 = 0
    const2 = 0
    
    index1 = str(request.form.get("iol_list1"))
    index2 = str(request.form.get("iol_list2"))
    for i in range(len(AconstDictionary)):
        if AconstDictionary[i][0] == index1:
           const1 = AconstDictionary[i][1]
           listIOL[0] = IOLdictionary[i][1]
        if AconstDictionary[i][0] == index2:
           const2 = AconstDictionary[i][1]
           listIOL[1] = IOLdictionary[i][1]  

    eye_length = request.form.get("k1_field")
    plan_refr = request.form.get("k2_field")
    meridian1 = request.form.get("k3_field")
    meridian2 = request.form.get("k4_field")
    
    if (not is_number(eye_length)) or (not is_number(plan_refr)) or (not is_number(meridian1)) or (not is_number(meridian2)):
       return redirect(url_for('test_flash', id_mess=2))
    
    lense1 = getPowerIOL(const1, eye_length, plan_refr, meridian1, meridian2)	
    lense2 = getPowerIOL(const2, eye_length, plan_refr, meridian1, meridian2)           
	
    return render_template('res_calc.html', form=res_calc_form, dl_gl=eye_length, pl_refr=plan_refr,
    merid1 = meridian1, merid2 = meridian2,
    Aconst1 = const1, Aconst2 = const2, NamesIol = listIOL, lense1=lense1, lense2=lense2)


@app.route('/flash/<id_mess>')
def test_flash(id_mess):
    if id_mess == "1":
       flash('Неверное имя пользователя или пароль! Повторите ввод', 'warning')
    elif id_mess == "2":
       flash(Markup('Данные введены неверно! Требуются <b>числовые значения</b>, использование букв, нулей и спецсимволов недопустимо!'), 'warning')
    elif id_mess == "3":
       flash('Данные успешно сохранены!', 'success')    
    elif id_mess == '4':
       flash('Данные не сохранены! Обратитесь к администратору или повторите ввод', 'warning')    
    return render_template('flash.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
