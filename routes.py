from init import *
from decorators import *

API_KEY = os.getenv('API_KEY')


@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Server'] = 'WeatherForecast_SERVER'
    return response

@require_origin
@app.route('/weather', methods=['GET', 'POST'])
def get_weather():
    city = request.json.get('location')
    days = request.json.get('days', 15) # Default to 4 days
    if not city:
        return jsonify({'error': 'City is required'}), 400
    
    # Fetch current weather
    weather_url = f'http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}'
    forecast_url = f'http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city}&days={days}'

    try:
        weather_response = requests.get(weather_url)
        forecast_response = requests.get(forecast_url)
        weather_data = weather_response.json()
        forecast_data = forecast_response.json()

        if 'error' in weather_data:
            return jsonify({'error': weather_data['error']['message']}), 400

        if 'error' in forecast_data:
            return jsonify({'error': forecast_data['error']['message']}), 400
        

        return jsonify({
            'current': weather_data,
            'forecast': forecast_data
        })
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@require_origin
@app.route('/weather-by-location', methods=['GET', 'POST'])
def get_weather_by_location():
    lat = request.json.get('lat')
    lon = request.json.get('lon')

    if not lat or not lon:
        return jsonify({'error': 'Latitude and longitude are required'}), 400

    # Construct the URL for fetching weather info based on latitude and longitude
    weather_url = f'http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={lat},{lon}'
    forecast_url = f'http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={lat},{lon}&days=15'

    try:
        weather_response = requests.get(weather_url)
        forecast_response = requests.get(forecast_url)
        weather_data = weather_response.json()
        forecast_data = forecast_response.json()

        if 'error' in weather_data:
            return jsonify({'error': weather_data['error']['message']}), 400

        if 'error' in forecast_data:
            return jsonify({'error': forecast_data['error']['message']}), 400

        return jsonify({
            'current': weather_data,
            'forecast': forecast_data
        })
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500
    

def generate_otp():
    return secrets.token_hex(3)


def send_otp(email_receiver, subject, body):
    otp = generate_otp()


    otp_dict[email_receiver] = otp
    try:
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(body + otp)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())
        return otp
    except Exception as e:
        raise Exception(str(e))

@require_origin
@app.route('/send_otp_email', methods=['POST'])
def send_otp_email():
    data = request.json
    email_receiver = data.get('email')

    if not email_receiver:
        return jsonify({'error': 'Email is required'}), 400

    try:
        existing_user = supabase.table('subscriptions').select('email').eq('email', email_receiver).execute()
    
        if existing_user.data:
            return jsonify({'message': "User already exists in the database."}), 400
        else:
            otp = send_otp(
                email_receiver,
                "Your verification code from Weather App",
                "This is your OTP code: "
            )
            return jsonify({'message': "OTP sent successfully!"}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@require_origin
@app.route('/send_unsubscribe_otp', methods=['POST'])
def send_unsubscribe_otp():
    data = request.json
    email_receiver = data.get('email')

    if not email_receiver:
        return jsonify({'error': 'Email is required'}), 400
    
    try:
        existing_user = supabase.table('subscriptions').select('email').eq('email', email_receiver).execute()
    
        if existing_user.data:
            otp = send_otp(
                email_receiver,
                "Your unsubscribe verification code from Weather App",
                "This is your unsubscribe OTP code: "
            )
            return jsonify({'message': "Unsubscribe OTP sent successfully!"}), 200
        else:
            return jsonify({'message': "User does not subscribe"}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def verify_otp(email, user_otp, action):
    if email in otp_dict and user_otp == otp_dict[email]:
        del otp_dict[email]
        return True
    return False


@require_origin
@app.route('/verify_otp', methods=['POST'])
def verify_email():
    data = request.json
    email = data.get('email')
    user_otp = data.get('otp')
    if verify_otp(email, user_otp, 'subscribe'):
        # Insert into database or other actions for subscription
        existing_user = supabase.table('subscriptions').select('email').eq('email', email).execute()
            
        if not existing_user.data:
                # Add user to the database
            supabase.table('subscriptions').insert([{'email': email, 'confirmed': True}]).execute()
        return jsonify({'message': 'Email verification successful!'}), 200
    return jsonify({'error': 'Invalid OTP'}), 400


@require_origin
@app.route('/verify_unsubscribe_otp', methods=['POST'])
def verify_unsubscribe_otp():
    data = request.json
    email = data.get('email')
    user_otp = data.get('otp')
    if verify_otp(email, user_otp, 'unsubscribe'):
        existing_user = supabase.table('subscriptions').select('email').eq('email', email).execute()
            
        if existing_user.data:
                # Add user to the database
            supabase.table('subscriptions').delete().eq('email', email).execute()
        return jsonify({'message': 'Unsubscribed successfully!'}), 200
    return jsonify({'error': 'Invalid OTP'}), 400

