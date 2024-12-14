from webapp import app
from webapp import *

from pytz import timezone
uae = timezone('Asia/Dubai')

import logging

from datetime import datetime, timedelta

logging.basicConfig(level=logging.DEBUG)

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    nickname = db.Column(db.String(100), nullable=False)
    diet_type = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)

# Data model for user-maintained data
class UserData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    date = db.Column(db.Date, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    sleep = db.Column(db.Float, nullable=False)
    steps = db.Column(db.Integer, nullable=False)
    calories_in = db.Column(db.Float, nullable=False)
    calories_out = db.Column(db.Float, nullable=False)

    number_of_meals = db.Column(db.Integer, nullable=False)
    time_of_last_meal = db.Column(db.Time, nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(uae))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(uae), onupdate=datetime.now(uae))

# Training activity model
class TrainingActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.Date, nullable=False)
    body_area = db.Column(db.Text, nullable=True)
    activity_type = db.Column(db.Text, nullable=True)
    sport_specific = db.Column(db.Text, nullable=True)
    recovery_type = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(uae))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(uae), onupdate=datetime.now(uae))

# Flask-Admin setup
admin = Admin(app)
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(UserData, db.session))
admin.add_view(ModelView(TrainingActivity, db.session))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    print("Testing")
    if request.method == 'POST':

        try:
            logging.debug(request.form)  # Log form data
            print("Post Test")
            name = request.form['name']
            print(name)
            dob = datetime.strptime(request.form['dob'], '%Y-%m-%d') 
            print(dob)
            height = request.form['height']
            print(height)
            weight = request.form['weight']
            print(weight)
            nickname = request.form['nickname']
            print(nickname)
            diet_type = request.form['diet']
            print(diet_type)
            
            email = request.form['email']
            print(email)
            password = request.form['password']
            print(password)

            print("Collected all Data")
            
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(name=name, dob=dob, height=height, weight=weight, nickname=nickname, diet_type=diet_type, email=email, password=hashed_password)

            try:
                db.session.add(new_user)
                db.session.commit()
                flash('Registration successful! You can now log in.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                flash('Error: Email already exists.', 'danger')

        except Exception as e:
            logging.error(f"Registration error: {e}")
            flash('Registration failed. Check your input and try again.', 'danger')

        

        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    latest_user_data = UserData.query.filter_by(user_id=current_user.id).order_by(UserData.date.desc()).first()
    latest_training_activity = TrainingActivity.query.filter_by(user_id=current_user.id).order_by(TrainingActivity.date.desc()).first()

    last_entry = latest_user_data if latest_user_data else None

    if request.method == 'POST':
        date = datetime.strptime(request.form['date'], '%Y-%m-%d') 

        # Check for duplicate entry in UserData
        if UserData.query.filter_by(user_id=current_user.id, date=date).first():
            flash('User data for this date already exists.', 'danger')
            return redirect(url_for('dashboard'))

        weight = request.form['weight']
        sleep = request.form['sleep']
        steps = request.form['steps']
        calories_in = request.form['calories_in']
        calories_out = request.form['calories_out']

        number_of_meals = request.form['number_of_meals']
        time_of_last_meal_str = request.form['time_of_last_meal']

        # Convert the string to a `time` object
        try:
            time_of_last_meal = time.fromisoformat(time_of_last_meal_str)
        except ValueError:
            # Handle invalid time formats
            raise ValueError("Invalid time format. Please use HH:MM:SS format.")


        # Handle multiple selections for training activity fields
        body_area = ','.join(request.form.getlist('body_area'))
        activity_type = ','.join(request.form.getlist('activity_type'))
        sport_specific = ','.join(request.form.getlist('sport_specific'))
        recovery_type = ','.join(request.form.getlist('recovery'))

        print(body_area)
        print(activity_type)

        # Add user data
        new_user_data = UserData(
            user_id=current_user.id,
            date=date,
            weight=weight,
            sleep=sleep,
            steps=steps,
            calories_in=calories_in,
            calories_out=calories_out,
            number_of_meals=number_of_meals,
            time_of_last_meal=time_of_last_meal
        )
        db.session.add(new_user_data)

        # Add training activity
        new_training_activity = TrainingActivity(
            user_id=current_user.id,
            date=date,
            body_area=body_area,
            activity_type=activity_type,
            sport_specific=sport_specific,
            recovery_type=recovery_type
        )
        db.session.add(new_training_activity)

        db.session.commit()
        flash('Data added successfully!', 'success')

        return redirect(url_for('dashboard'))

    return render_template('dashboard.html', last_entry=last_entry,user_data=latest_user_data, training_activity=latest_training_activity)





@app.route('/all-data')
@login_required
def all_data():
    all_user_data = UserData.query.filter_by(user_id=current_user.id).order_by(UserData.date.desc()).all()
    all_training_activities = TrainingActivity.query.filter_by(user_id=current_user.id).order_by(TrainingActivity.date.desc()).all()
    return render_template('all_data.html', all_user_data=all_user_data, all_training_activities=all_training_activities)


@app.route('/progress')
@login_required
def progress():
    return render_template('progress.html')

@app.route('/progress-data', methods=['GET'])
@login_required
def progress_data():
    metric = request.args.get('metric', 'weight')
    view = request.args.get('view', 'days')

    user_data = UserData.query.filter_by(user_id=current_user.id).order_by(UserData.date).all()

    labels = []
    data_points = {'calories_in': [], 'calories_out': []} if metric == 'calories' else []

    if view == 'days':
        labels = [data.date.strftime('%Y-%m-%d') for data in user_data]
        if metric == 'calories':
            data_points['calories_in'] = [data.calories_in for data in user_data]
            data_points['calories_out'] = [data.calories_out for data in user_data]
        else:
            data_points = [getattr(data, metric) for data in user_data]

    elif view == 'weeks':
        weekly_data = {}
        for data in user_data:
            week_start = data.date - timedelta(days=data.date.weekday())
            if week_start not in weekly_data:
                weekly_data[week_start] = []
            weekly_data[week_start].append(data)

        labels = [week.strftime('%Y-%m-%d') for week in weekly_data.keys()]
        if metric == 'calories':
            data_points['calories_in'] = [
                sum(data.calories_in for data in week) / len(week) for week in weekly_data.values()
            ]
            data_points['calories_out'] = [
                sum(data.calories_out for data in week) / len(week) for week in weekly_data.values()
            ]
        else:
            data_points = [
                sum(getattr(data, metric) for data in week) / len(week) for week in weekly_data.values()
            ]

    elif view == 'months':
        monthly_data = {}
        for data in user_data:
            month_start = data.date.replace(day=1)
            if month_start not in monthly_data:
                monthly_data[month_start] = []
            monthly_data[month_start].append(data)

        labels = [month.strftime('%Y-%m') for month in monthly_data.keys()]
        if metric == 'calories':
            data_points['calories_in'] = [
                sum(data.calories_in for data in month) / len(month) for month in monthly_data.values()
            ]
            data_points['calories_out'] = [
                sum(data.calories_out for data in month) / len(month) for month in monthly_data.values()
            ]
        else:
            data_points = [
                sum(getattr(data, metric) for data in month) / len(month) for month in monthly_data.values()
            ]

    return jsonify({'labels': labels, 'data': data_points})


@app.route('/dashboard/edit', methods=['POST'])
@login_required
def edit_last_entry():
    entry_id = request.form.get('id')
    entry = UserData.query.filter_by(id=entry_id, user_id=current_user.id).first()

    if entry:
        entry.date = datetime.strptime(request.form['date'], '%Y-%m-%d') 
        entry.weight = request.form['weight']
        entry.sleep = request.form['sleep']
        entry.steps = request.form['steps']
        entry.calories_in = request.form['calories_in']
        entry.calories_out = request.form['calories_out']
        entry.number_of_meals = request.form['number_of_meals']
        time_of_last_meal_str = request.form['time_of_last_meal']

        time_of_last_meal_str = request.form['time_of_last_meal']

        # Convert the string to a `time` object
        try:
            entry.time_of_last_meal = time.fromisoformat(time_of_last_meal_str)
        except ValueError:
            # Handle invalid time formats
            raise ValueError("Invalid time format. Please use HH:MM:SS format.")

        entry.updated_at = datetime.now(uae)

        db.session.commit()
        flash("Last entry updated successfully!", "success")
    else:
        flash("Unable to update the entry.", "danger")

    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
