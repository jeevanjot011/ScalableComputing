from flask import Flask, render_template_string
import os

application = Flask(__name__)

# API Endpoints
LOAN_API_URL = 'https://72xiv7vsp6.execute-api.us-east-1.amazonaws.com/prod'
INSURANCE_API_URL = 'https://dx9lk0qa66.execute-api.us-east-1.amazonaws.com/prod'

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Financial Calculator Suite</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 {
            text-align: center;
            color: white;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .calculator-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }
        .calculator-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .calculator-card h2 {
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }
        .form-group { margin-bottom: 15px; }
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 600;
        }
        input[type="number"], input[type="text"], select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
        }
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }
        button:hover { opacity: 0.9; }
        button:disabled { opacity: 0.6; cursor: not-allowed; }
        .result {
            margin-top: 20px;
            padding: 20px;
            background: #f7f7f7;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            display: none;
        }
        .result.show { display: block; animation: slideIn 0.3s ease; }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .result h3 { color: #667eea; margin-bottom: 10px; }
        .result-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e0e0e0;
        }
        .result-item:last-child { border-bottom: none; }
        .result-value { font-weight: bold; color: #333; }
        .error {
            color: #e74c3c;
            background: #fdf2f2;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            display: none;
        }
        .loading {
            text-align: center;
            color: #667eea;
            margin-top: 15px;
            display: none;
        }
        .status-bar {
            background: rgba(255,255,255,0.1);
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
            background: #2ecc71;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .placeholder {
            color: #888;
            text-align: center;
            padding: 40px 0;
        }
        .api-status {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            margin-left: 10px;
        }
        .api-online { background: #2ecc71; color: white; }
        .api-offline { background: #e74c3c; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>💰 Financial Calculator Suite</h1>
        
        <div class="status-bar">
            <span class="status-indicator"></span>
            <span>API Status:</span>
            <span id="loanStatus" class="api-status api-offline">Loan: Checking...</span>
            <span id="insuranceStatus" class="api-status api-offline">Insurance: Checking...</span>
        </div>

        <div class="calculator-grid">
            <!-- Loan Calculator -->
            <div class="calculator-card">
                <h2>🏠 Loan Calculator</h2>
                <form id="loanForm">
                    <div class="form-group">
                        <label for="loanPrincipal">Principal Amount (₹)</label>
                        <input type="number" id="loanPrincipal" value="500000" min="1" required>
                    </div>
                    <div class="form-group">
                        <label for="loanRate">Annual Interest Rate (%)</label>
                        <input type="number" id="loanRate" value="7.5" step="0.1" min="0" required>
                    </div>
                    <div class="form-group">
                        <label for="loanYears">Loan Tenure (Years)</label>
                        <input type="number" id="loanYears" value="20" min="1" max="30" required>
                    </div>
                    <button type="submit" id="loanSubmit">Calculate EMI</button>
                </form>
                <div class="loading" id="loanLoading">Calculating...</div>
                <div class="error" id="loanError"></div>
                <div class="result" id="loanResult">
                    <h3>Loan Summary</h3>
                    <div class="result-item">
                        <span>Monthly EMI:</span>
                        <span class="result-value" id="loanEmi">₹0</span>
                    </div>
                    <div class="result-item">
                        <span>Total Payment:</span>
                        <span class="result-value" id="loanTotal">₹0</span>
                    </div>
                    <div class="result-item">
                        <span>Total Interest:</span>
                        <span class="result-value" id="loanInterest">₹0</span>
                    </div>
                    <div class="result-item">
                        <span>Loan Tenure:</span>
                        <span class="result-value" id="loanMonths">0 months</span>
                    </div>
                </div>
            </div>

            <!-- Insurance Calculator -->
            <div class="calculator-card">
                <h2>🛡️ Insurance Calculator <span id="insuranceApiBadge" style="font-size:12px; background:#667eea; color:white; padding:2px 6px; border-radius:4px;">LIVE</span></h2>
                <form id="insuranceForm">
                    <div class="form-group">
                        <label for="insAge">Age</label>
                        <input type="number" id="insAge" value="30" min="18" max="65" required>
                    </div>
                    <div class="form-group">
                        <label for="insTerm">Term (Years)</label>
                        <input type="number" id="insTerm" value="25" min="5" max="30" required>
                    </div>
                    <div class="form-group">
                        <label for="insSumAssured">Sum Assured</label>
                        <input type="number" id="insSumAssured" value="250000" min="10000" required>
                    </div>
                    <div class="form-group">
                        <label for="insGender">Gender</label>
                        <select id="insGender" required>
                            <option value="male">Male</option>
                            <option value="female">Female</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="insSmoker">Smoker</label>
                        <select id="insSmoker" required>
                            <option value="false">No</option>
                            <option value="true">Yes</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="insFrequency">Payment Frequency</label>
                        <select id="insFrequency" required>
                            <option value="monthly">Monthly</option>
                            <option value="quarterly">Quarterly</option>
                            <option value="yearly">Yearly</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="insCurrency">Currency</label>
                        <select id="insCurrency" required>
                            <option value="EUR">EUR (€)</option>
                            <option value="USD">USD ($)</option>
                            <option value="GBP">GBP (£)</option>
                        </select>
                    </div>
                    <button type="submit" id="insuranceSubmit">Calculate Premium</button>
                </form>
                <div class="loading" id="insuranceLoading">Calculating...</div>
                <div class="error" id="insuranceError"></div>
                <div class="result" id="insuranceResult">
                    <h3>Insurance Premium</h3>
                    <div class="result-item">
                        <span>Monthly Premium:</span>
                        <span class="result-value" id="insPremium">€0</span>
                    </div>
                    <div class="result-item">
                        <span>Currency:</span>
                        <span class="result-value" id="insCurrency">EUR</span>
                    </div>
                    <div class="result-item">
                        <span>Payment Frequency:</span>
                        <span class="result-value" id="insFrequency">monthly</span>
                    </div>
                    <div class="result-item">
                        <span>Pricing Model:</span>
                        <span class="result-value" id="insModel">-</span>
                    </div>
                </div>
            </div>

            <!-- Tax Calculator Placeholder -->
            <div class="calculator-card">
                <h2>📊 Tax Calculator</h2>
                <div class="placeholder">
                    Coming Soon<br>
                    <small>Your teammate is working on this API</small>
                </div>
            </div>
        </div>
    </div>

    <script>
        // API URLs
        const LOAN_API_URL = 'https://72xiv7vsp6.execute-api.us-east-1.amazonaws.com/prod';
        const INSURANCE_API_URL = 'https://dx9lk0qa66.execute-api.us-east-1.amazonaws.com/prod';

        // Check API Health
        async function checkApiHealth() {
            // Check Loan API
            try {
                const response = await fetch(LOAN_API_URL + '/loan/health');
                if (response.ok) {
                    document.getElementById('loanStatus').textContent = 'Loan: Online';
                    document.getElementById('loanStatus').className = 'api-status api-online';
                }
            } catch (error) {
                document.getElementById('loanStatus').textContent = 'Loan: Offline';
                document.getElementById('loanStatus').className = 'api-status api-offline';
            }

            // Check Insurance API (using a test call)
            try {
                const response = await fetch(INSURANCE_API_URL + '/premium/estimate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({age: 30, termYears: 25, sumAssured: 250000, smoker: false, gender: "male", paymentFrequency: "monthly", currency: "EUR"})
                });
                if (response.ok) {
                    document.getElementById('insuranceStatus').textContent = 'Insurance: Online';
                    document.getElementById('insuranceStatus').className = 'api-status api-online';
                }
            } catch (error) {
                document.getElementById('insuranceStatus').textContent = 'Insurance: Offline';
                document.getElementById('insuranceStatus').className = 'api-status api-offline';
            }
        }

        // Format Currency
        function formatCurrency(amount, symbol) {
            return symbol + parseFloat(amount).toLocaleString('en-IN', {
                maximumFractionDigits: 2,
                minimumFractionDigits: 2
            });
        }

        // Loan Calculator
        document.getElementById('loanForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const submitBtn = document.getElementById('loanSubmit');
            const loading = document.getElementById('loanLoading');
            const error = document.getElementById('loanError');
            const result = document.getElementById('loanResult');
            
            submitBtn.disabled = true;
            loading.style.display = 'block';
            error.style.display = 'none';
            result.classList.remove('show');
            
            try {
                const response = await fetch(LOAN_API_URL + '/loan/calculate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        principal: parseFloat(document.getElementById('loanPrincipal').value),
                        annual_rate: parseFloat(document.getElementById('loanRate').value),
                        years: parseInt(document.getElementById('loanYears').value)
                    })
                });
                
                const data = await response.json();
                if (!response.ok) throw new Error(data.error || 'Calculation failed');
                
                document.getElementById('loanEmi').textContent = '₹' + data.emi.toLocaleString();
                document.getElementById('loanTotal').textContent = '₹' + data.total_payment.toLocaleString();
                document.getElementById('loanInterest').textContent = '₹' + data.total_interest.toLocaleString();
                document.getElementById('loanMonths').textContent = data.months + ' months';
                
                result.classList.add('show');
            } catch (err) {
                error.textContent = 'Error: ' + err.message;
                error.style.display = 'block';
            } finally {
                submitBtn.disabled = false;
                loading.style.display = 'none';
            }
        });

        // Insurance Calculator
        document.getElementById('insuranceForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const submitBtn = document.getElementById('insuranceSubmit');
            const loading = document.getElementById('insuranceLoading');
            const error = document.getElementById('insuranceError');
            const result = document.getElementById('insuranceResult');
            
            submitBtn.disabled = true;
            loading.style.display = 'block';
            error.style.display = 'none';
            result.classList.remove('show');
            
            try {
                const currency = document.getElementById('insCurrency').value;
                const frequency = document.getElementById('insFrequency').value;
                
                const response = await fetch(INSURANCE_API_URL + '/premium/estimate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        age: parseInt(document.getElementById('insAge').value),
                        termYears: parseInt(document.getElementById('insTerm').value),
                        sumAssured: parseInt(document.getElementById('insSumAssured').value),
                        smoker: document.getElementById('insSmoker').value === 'true',
                        gender: document.getElementById('insGender').value,
                        paymentFrequency: frequency,
                        currency: currency
                    })
                });
                
                const data = await response.json();
                if (!response.ok) throw new Error(data.error || 'Calculation failed');
                
                const symbols = {EUR: '€', USD: '$', GBP: '£'};
                document.getElementById('insPremium').textContent = symbols[currency] + data.premium.toFixed(2);
                document.getElementById('insCurrency').textContent = data.currency;
                document.getElementById('insFrequency').textContent = data.frequency;
                document.getElementById('insModel').textContent = data.pricingModel;
                
                result.classList.add('show');
            } catch (err) {
                error.textContent = 'Error: ' + err.message;
                error.style.display = 'block';
            } finally {
                submitBtn.disabled = false;
                loading.style.display = 'none';
            }
        });

        // Check health on load
        checkApiHealth();
    </script>
</body>
</html>
"""

@application.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@application.route('/health')
def health():
    return {'status': 'healthy', 'service': 'financial-calculator-frontend'}

if __name__ == '__main__':
    application.run(debug=True)
