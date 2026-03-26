from flask import Flask, render_template
import os

application = Flask(__name__)

# API Configuration
LOAN_API_URL = 'https://72xiv7vsp6.execute-api.us-east-1.amazonaws.com/prod'
INSURANCE_API_URL = 'https://dx9lk0qa66.execute-api.us-east-1.amazonaws.com/prod'
EXCHANGE_RATE_API_KEY = '95edf59d41cc15cdd983df04'

@application.route('/')
def home():
    return render_template('index.html', active_page='home')

@application.route('/services')
def services():
    return render_template('services.html', active_page='services')

@application.route('/loan')
def loan():
    return render_template('loan.html', active_page='services')

@application.route('/insurance')
def insurance():
    return render_template('insurance.html', active_page='services')

@application.route('/tax')
def tax():
    return render_template('tax.html', active_page='services')

@application.route('/health')
def health():
    return {
        'status': 'healthy',
        'service': 'scalable-financial-suite',
        'version': '2.0.0',
        'apis': {
            'loan': LOAN_API_URL,
            'insurance': INSURANCE_API_KEY,
            'currency': 'exchangerate-api.com'
        }
    }

if __name__ == '__main__':
    application.run(debug=True)
