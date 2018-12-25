import json
from app import app, db, socketio, mqtt
from flask import render_template, redirect, url_for, request, flash
from app.forms import AddCarForm, LoginForm
from app.models import Car, User
from flask_login import current_user, login_user, login_required, logout_user
from flask_socketio import emit
from sqlalchemy import desc, and_, between
from werkzeug.urls import url_parse
from datetime import datetime, timedelta


#-----ROUTE-----
@app.route('/')
@app.route('/index')
def index():
    current_car=Car.query.filter(Car.depart_time == None).order_by((Car.entry_time)).all()
    #lastdepart_car=Car.query.filter(Car.depart_time != None).order_by(desc(Car.depart_time)).first()
    return render_template('index.html', car=current_car)

@app.route('/dayflow')
def dayflow():
    return render_template('dayflow.html')
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form=LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('無效或錯誤的帳號或密碼')
            return redirect(url_for('login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = (url_for('index'))
        return redirect(next_page)
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    else:
        logout_user()
        return redirect(url_for('index'))

@app.route('/test')
def test():
    return render_template('socketio_test.html') 

@app.route('/get_mqtt')
def get_mqtt():
    return render_template('mqtt_socketio.html') 

@app.route('/addcar', methods=['GET', 'POST']) #Simulate uploading a carplate and judge data in db
def plate_add():
    form=AddCarForm()
    if form.validate_on_submit():
        checked_car = Car.query.filter_by(number_plate=form.number_plate.data).first()
        if checked_car is None:
            car = Car(number_plate=form.number_plate.data)
            car.set_entrytime()
            db.session.add(car)
        else:
            checked_car.set_entrytime()
            db.session.add(checked_car)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('plate_add.html', form=form)

@app.route('/api/v1.0/mqtt/pub/<want_to_pub>', methods=['GET']) #Simulate publish a MQTT message
def pub_my_msg(want_to_pub):
    if len(want_to_pub) == 0:
        abort(404)
    mqtt.publish('carplate',want_to_pub )
    return want_to_pub
#-----/ROUTE-----

#-----SOCKETIO-----
@socketio.on('client_event', namespace='/ns_mqtt') #Get socket.emit msg
def client_msg(msg):
    emit('server_response', {'data': msg['data']}, broadcast=True, namespace='/ns_mqtt')
    #socketio.emit('server_response', {'data': 'test'}, broadcast=True, namespace='/ns_mqtt')
    
@socketio.on('connect_event', namespace='/ns_mqtt')  #First check connected
def connected_msg(msg):
    emit('server_response', car, namespace='/ns_mqtt')

@socketio.on('get_chart', namespace='/ns_mqtt')  #Make Chart data in json when get socket(get_chart)
def get_chart(msg):
    last_day = datetime.utcnow()
    first_day = last_day - timedelta(days=6)
    car_amount = Car.query.filter(Car.entry_time.between(first_day, last_day)).all()
    date = []
    quantity = [0]*7
    for i in range(7):
        date.append((first_day+timedelta(days=i, hours=8)).strftime("%Y-%m-%d"))
        for c in car_amount:
            if c.entry_time.date() == first_day.date()+timedelta(days=i):
                quantity[i]=quantity[i]+1
    msg={'label': date, 'data' : quantity}
    emit('chart_dayflow', msg, namespace='/ns_mqtt')

    current_car=Car.query.filter(Car.depart_time == None).order_by((Car.entry_time)).all()
    label = ['正常車輛','長期滯留車輛']
    data = [0]*2
    for c in current_car:
        if c.get_status()>=1:
            data[1]=data[1]+1
        else:
            data[0]=data[0]+1
    
    msg={'label': label, 'data' : data}
    print(msg)
    emit('chart_daystatus', msg, namespace='/ns_mqtt')
    
    
#-----/SOCKETIO-----

#-----MQTT-----
@mqtt.on_connect() #Create subscription and check if connected
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('carplate')

@mqtt.on_message() #Deal with subscription event
def handle_mqtt_message(client, userdata, message):
    payload = message.payload.decode()
    p = json.loads(payload)
    status = p['status']
    plate = p['plate']
    print("-------msg-------")
    print(p['status'],p['plate'], message.topic)
    checked_car = Car.query.filter_by(number_plate=plate).first()
    if status=='in':
        if checked_car is None:
            car = Car(number_plate=plate)
            car.set_entrytime()
            time=car.get_entrytime()
            db.session.add(car)
        else:
            checked_car.set_entrytime()
            checked_car.reset_departtime()
            time=checked_car.get_entrytime()
            db.session.add(checked_car)
        db.session.commit()
    elif status=='out':
        checked_car.set_departtime()
        time=checked_car.get_departtime()
        db.session.add(checked_car)
        db.session.commit()
    
    msg = {'status':status, 'carplate': plate, 'time': time}
    #car=Car.query.order_by((Car.entry_time)).all()
    socketio.emit('mqtt_message', msg, broadcast=True, namespace='/ns_mqtt')
    #socketio.emit('mqtt_message', car, broadcast=True, namespace='/ns_mqtt')
    #socketio.emit('update', car, broadcast=True, namespace='/ns_mqtt')
   
    
#-----/MQTT-----
    
    
    
