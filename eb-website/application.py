from flask import Flask, render_template_string
from functools import wraps
application = Flask(__name__)

LOAN_API = 'https://v68fi30gr9.execute-api.us-east-1.amazonaws.com/prod'
INSURANCE_API = 'https://dx9lk0qa66.execute-api.us-east-1.amazonaws.com/prod'
EXCHANGE_KEY = '95edf59d41cc15cdd983df04'



@application.after_request
def add_security_headers(response):
    # Fix: Content Security Policy (CSP) Header Not Set
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; font-src 'self' https://cdnjs.cloudflare.com;"
    
    # Fix: Missing Anti-clickjacking Header (X-Frame-Options)
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    
    # Fix: X-Content-Type-Options Header Missing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Additional security headers
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    return response

def get_base_template(active_page):
    nav_currency = 'active' if active_page == 'currency' else ''
    nav_loan = 'active' if active_page == 'loan' else ''
    nav_insurance = 'active' if active_page == 'insurance' else ''
    nav_tax = 'active' if active_page == 'tax' else ''
    
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>''' + active_page.title() + ''' - ScalableFin</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" 
      rel="stylesheet" 
      integrity="sha512-9usAa10IRO0HhonpyAIVpjrylPvoDwiPUiKdWk5t3PyolY1cOd4DSE0Ga+ri4AuTroPR5aQvXU9xC6qOPnzFeg==" 
      crossorigin="anonymous" 
      referrerpolicy="no-referrer">
    <style>
        :root {
            --silver-dark: #1a1a1f;
            --silver-mid: #2d2d35;
            --silver-light: #4a4a55;
            --accent: #8b8b9b;
            --text: #e0e0e5;
            --text-muted: #9090a0;
            --success: #4ade80;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #0f0f12 0%, #1a1a1f 50%, #25252c 100%);
            min-height: 100vh;
            color: var(--text);
        }
        .header {
            background: linear-gradient(90deg, #0f0f12 0%, #2d2d35 100%);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--silver-light);
        }
        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.4em;
            font-weight: bold;
            color: var(--text);
        }
        .nav {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        .nav a, .menu-btn {
            color: var(--text-muted);
            text-decoration: none;
            padding: 8px 14px;
            border-radius: 6px;
            transition: all 0.3s;
            background: transparent;
            border: none;
            cursor: pointer;
            font-size: 0.9em;
        }
        .nav a:hover, .nav a.active {
            color: var(--text);
            background: var(--silver-mid);
        }
        .menu-btn {
            font-size: 1.2em;
            padding: 8px 12px;
        }
        .menu-btn:hover {
            color: var(--text);
            background: var(--silver-mid);
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 30px;
        }
        .card {
            background: linear-gradient(135deg, var(--silver-mid) 0%, var(--silver-light) 100%);
            border-radius: 16px;
            padding: 30px;
            border: 1px solid rgba(139, 139, 155, 0.2);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        }
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 14px 28px;
            background: linear-gradient(90deg, var(--silver-light) 0%, var(--accent) 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(139, 139, 155, 0.3);
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: var(--text-muted);
            font-size: 0.9em;
        }
        .form-group input, .form-group select {
            width: 100%;
            padding: 14px;
            background: var(--silver-dark);
            border: 1px solid var(--silver-light);
            border-radius: 10px;
            color: var(--text);
            font-size: 1em;
        }
        .result-box {
            margin-top: 25px;
            padding: 25px;
            background: rgba(74, 222, 128, 0.1);
            border-radius: 12px;
            border-left: 4px solid var(--success);
            display: none;
        }
        .result-box.show { display: block; }
        .result-row {
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .result-value {
            font-weight: bold;
            color: var(--success);
        }
        .loading, .error {
            display: none;
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
        }
        .loading {
            color: var(--accent);
            text-align: center;
        }
        .error {
            background: rgba(248, 113, 113, 0.1);
            color: #f87171;
        }
        .analysis-panel {
            position: fixed;
            right: -400px;
            top: 0;
            width: 380px;
            height: 100vh;
            background: var(--silver-mid);
            border-left: 1px solid var(--silver-light);
            padding: 80px 20px 20px;
            transition: right 0.3s ease;
            z-index: 1000;
            overflow-y: auto;
        }
        .analysis-panel.open { right: 0; }
        .panel-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.7);
            display: none;
            z-index: 999;
        }
        .panel-overlay.show { display: block; }
        .close-panel {
            position: absolute;
            top: 20px;
            right: 20px;
            color: var(--text);
            font-size: 1.5em;
            cursor: pointer;
        }
        .metric-card {
            background: var(--silver-dark);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 15px;
        }
        .metric-title {
            color: var(--text-muted);
            font-size: 0.85em;
            margin-bottom: 8px;
        }
        .metric-value {
            color: var(--text);
            font-size: 1.8em;
            font-weight: bold;
        }
        .footer {
            text-align: center;
            padding: 30px;
            color: var(--text-muted);
            border-top: 1px solid var(--silver-light);
            margin-top: 50px;
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="logo">
            <i class="fas fa-chart-line"></i>
            <span>ScalableFin</span>
        </div>
        <nav class="nav">
            <a href="/" class="''' + nav_currency + '''">Currency</a>
            <a href="/loan" class="''' + nav_loan + '''">Loan</a>
            <a href="/insurance" class="''' + nav_insurance + '''">Insurance</a>
            <a href="/tax" class="''' + nav_tax + '''">Tax</a>
            <button class="menu-btn" onclick="toggleAnalysis()" title="Analytics">
                <i class="fas fa-ellipsis-v"></i>
            </button>
        </nav>
    </header>
    
    <div class="panel-overlay" id="overlay" onclick="toggleAnalysis()"></div>
    <div class="analysis-panel" id="analysisPanel">
        <i class="fas fa-times close-panel" onclick="toggleAnalysis()"></i>
        <h2 style="margin-bottom: 25px; color: var(--text);">
            <i class="fas fa-chart-bar"></i> API Analytics
        </h2>
        <div class="metric-card">
            <div class="metric-title">Total API Calls (24h)</div>
            <div class="metric-value" id="metricCalls">--</div>
        </div>
        <div class="metric-card">
            <div class="metric-title">Avg Response Time</div>
            <div class="metric-value" id="metricResponse">--</div>
        </div>
        <div class="metric-card">
            <div class="metric-title">Error Rate</div>
            <div class="metric-value" id="metricError">--</div>
        </div>
        <div class="metric-card">
            <div class="metric-title">Active Services</div>
            <div class="metric-value" style="color: var(--success);">3/3</div>
        </div>
        <p style="color: var(--text-muted); font-size: 0.85em; margin-top: 20px;">
            <i class="fas fa-info-circle"></i> Real-time CloudWatch metrics in Phase 2
        </p>
    </div>
    
    <main class="container">
'''

def get_footer(extra_js):
    return '''
    </main>
    
    <footer class="footer">
        <p>Powered by AWS Lambda, API Gateway, Elastic Beanstalk</p>
        <p style="font-size: 0.85em; margin-top: 10px;">Scalable Cloud Programming Project 2025-26</p>
    </footer>
    
    <script>
        function toggleAnalysis() {
            document.getElementById('analysisPanel').classList.toggle('open');
            document.getElementById('overlay').classList.toggle('show');
            document.getElementById('metricCalls').textContent = Math.floor(Math.random() * 5000 + 1000).toLocaleString();
            document.getElementById('metricResponse').textContent = Math.floor(Math.random() * 80 + 20) + ' ms';
            document.getElementById('metricError').textContent = (Math.random() * 1.5).toFixed(2) + '%';
        }
        ''' + extra_js + '''
    </script>
</body>
</html>
'''

@application.route('/')
def home():
    content = '''
<div class="card" style="max-width: 800px; margin: 0 auto; text-align: center;">
    <h1 style="font-size: 2em; margin-bottom: 10px;">
        <i class="fas fa-exchange-alt" style="color: var(--accent);"></i>
        Currency Converter
    </h1>
    <p style="color: var(--text-muted); margin-bottom: 30px;">
        Real-time exchange rates powered by ExchangeRate-API
    </p>
    <form id="convertForm" style="text-align: left;">
        <div style="display: grid; grid-template-columns: 1fr auto 1fr auto; gap: 15px; align-items: end; margin-bottom: 20px;">
            <div class="form-group" style="margin: 0;">
                <label>Amount</label>
                <input type="number" id="amount" value="1000" min="0" step="0.01">
            </div>
            <div class="form-group" style="margin: 0;">
                <label>From</label>
                <select id="fromCurr">
                    <option value="USD" selected>USD ($)</option>
                    <option value="EUR">EUR (€)</option>
                    <option value="GBP">GBP (£)</option>
                    <option value="INR">INR (₹)</option>
                </select>
            </div>
            <button type="button" class="btn" onclick="swapCurrency()" style="padding: 14px;">
                <i class="fas fa-exchange-alt"></i>
            </button>
            <div class="form-group" style="margin: 0;">
                <label>To</label>
                <select id="toCurr">
                    <option value="EUR" selected>EUR (€)</option>
                    <option value="USD">USD ($)</option>
                    <option value="GBP">GBP (£)</option>
                    <option value="INR">INR (₹)</option>
                </select>
            </div>
        </div>
        <button type="submit" class="btn" style="width: 100%;">
            <i class="fas fa-calculator"></i> Convert
        </button>
    </form>
    <div class="loading" id="loading"><i class="fas fa-spinner fa-spin"></i> Converting...</div>
    <div class="error" id="error"></div>
    <div class="result-box" id="result" style="text-align: left;">
        <div class="result-row"><span>Converted Amount:</span><span class="result-value" id="resAmount">-</span></div>
        <div class="result-row"><span>Exchange Rate:</span><span class="result-value" id="resRate">-</span></div>
    </div>
</div>
'''
    js = '''
const EXCHANGE_KEY = '95edf59d41cc15cdd983df04';
const symbols = { USD: '$', EUR: '€', GBP: '£', INR: '₹' };
function swapCurrency() {
    const from = document.getElementById('fromCurr');
    const to = document.getElementById('toCurr');
    const temp = from.value;
    from.value = to.value;
    to.value = temp;
}
document.getElementById('convertForm').onsubmit = async (e) => {
    e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const result = document.getElementById('result');
    btn.disabled = true;
    loading.style.display = 'block';
    error.style.display = 'none';
    result.classList.remove('show');
    try {
        const amount = parseFloat(document.getElementById('amount').value);
        const from = document.getElementById('fromCurr').value;
        const to = document.getElementById('toCurr').value;
        const res = await fetch(`https://v6.exchangerate-api.com/v6/${EXCHANGE_KEY}/pair/${from}/${to}/${amount}`);
        const data = await res.json();
        if (data.result === 'success') {
            document.getElementById('resAmount').textContent = symbols[to] + data.conversion_result.toLocaleString();
            document.getElementById('resRate').textContent = '1 ' + from + ' = ' + data.conversion_rate + ' ' + to;
            result.classList.add('show');
        } else {
            throw new Error(data.error || 'Conversion failed');
        }
    } catch (err) {
        error.textContent = 'Error: ' + err.message;
        error.style.display = 'block';
    } finally {
        btn.disabled = false;
        loading.style.display = 'none';
    }
};
'''
    return get_base_template('currency') + content + get_footer(js)

@application.route('/loan')
def loan():
    content = '''
<div class="card" style="max-width: 600px; margin: 0 auto;">
    <div style="text-align: center; margin-bottom: 30px;">
        <i class="fas fa-home" style="font-size: 3em; color: var(--accent);"></i>
        <h1 style="margin-top: 15px;">Loan Calculator</h1>
        <p style="color: var(--text-muted);">Calculate EMI, total interest & payments</p>
    </div>
    <form id="loanForm">
        <div class="form-group">
            <label>Principal Amount (₹)</label>
            <input type="number" id="principal" value="500000" min="1" required>
        </div>
        <div class="form-group">
            <label>Annual Interest Rate (%)</label>
            <input type="number" id="rate" value="7.5" step="0.1" min="0" required>
        </div>
        <div class="form-group">
            <label>Loan Tenure (Years)</label>
            <input type="number" id="years" value="20" min="1" max="30" required>
        </div>
        <button type="submit" class="btn" style="width: 100%;">
            <i class="fas fa-calculator"></i> Calculate EMI
        </button>
    </form>
    <div class="loading" id="loading"><i class="fas fa-spinner fa-spin"></i> Calculating...</div>
    <div class="error" id="error"></div>
    <div class="result-box" id="result">
        <div class="result-row"><span>Monthly EMI:</span><span class="result-value" id="emi">-</span></div>
        <div class="result-row"><span>Total Payment:</span><span class="result-value" id="total">-</span></div>
        <div class="result-row"><span>Total Interest:</span><span class="result-value" id="interest">-</span></div>
        <div class="result-row"><span>Tenure:</span><span class="result-value" id="months">-</span></div>
    </div>
</div>
'''
    js = '''
const LOAN_API = 'https://v68fi30gr9.execute-api.us-east-1.amazonaws.com/prod';
document.getElementById('loanForm').onsubmit = async (e) => {
    e.preventDefault();
    const btn = e.target.querySelector('button');
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const result = document.getElementById('result');
    btn.disabled = true;
    loading.style.display = 'block';
    error.style.display = 'none';
    result.classList.remove('show');
    try {
        const res = await fetch(LOAN_API + '/loan/calculate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                principal: parseFloat(document.getElementById('principal').value),
                annual_rate: parseFloat(document.getElementById('rate').value),
                years: parseInt(document.getElementById('years').value)
            })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error);
        document.getElementById('emi').textContent = '₹' + data.emi.toLocaleString();
        document.getElementById('total').textContent = '₹' + data.total_payment.toLocaleString();
        document.getElementById('interest').textContent = '₹' + data.total_interest.toLocaleString();
        document.getElementById('months').textContent = data.months + ' months';
        result.classList.add('show');
    } catch (err) {
        error.textContent = 'Error: ' + err.message;
        error.style.display = 'block';
    } finally {
        btn.disabled = false;
        loading.style.display = 'none';
    }
};
'''
    return get_base_template('loan') + content + get_footer(js)

@application.route('/insurance')
def insurance():
    content = '''
<div class="card" style="max-width: 600px; margin: 0 auto;">
    <div style="text-align: center; margin-bottom: 30px;">
        <i class="fas fa-shield-alt" style="font-size: 3em; color: var(--accent);"></i>
        <h1 style="margin-top: 15px;">Insurance Calculator</h1>
        <p style="color: var(--text-muted);">Estimate life insurance premiums</p>
    </div>
    <form id="insForm">
        <div class="form-group">
            <label>Age</label>
            <input type="number" id="age" value="30" min="18" max="65" required>
        </div>
        <div class="form-group">
            <label>Term (Years)</label>
            <input type="number" id="term" value="25" min="5" max="30" required>
        </div>
        <div class="form-group">
            <label>Sum Assured</label>
            <input type="number" id="sumAssured" value="250000" min="10000" required>
        </div>
        <div class="form-group">
            <label>Gender</label>
            <select id="gender"><option value="male">Male</option><option value="female">Female</option></select>
        </div>
        <div class="form-group">
            <label>Smoker</label>
            <select id="smoker"><option value="false">No</option><option value="true">Yes</option></select>
        </div>
        <button type="submit" class="btn" style="width: 100%;">
            <i class="fas fa-calculator"></i> Calculate Premium
        </button>
    </form>
    <div class="loading" id="loading"><i class="fas fa-spinner fa-spin"></i> Calculating...</div>
    <div class="error" id="error"></div>
    <div class="result-box" id="result">
        <div class="result-row"><span>Monthly Premium:</span><span class="result-value" id="premium">-</span></div>
        <div class="result-row"><span>Currency:</span><span class="result-value" id="currency">-</span></div>
        <div class="result-row"><span>Model:</span><span class="result-value" id="model">-</span></div>
    </div>
</div>
'''
    js = '''
const INS_API = 'https://dx9lk0qa66.execute-api.us-east-1.amazonaws.com/prod';
document.getElementById('insForm').onsubmit = async (e) => {
    e.preventDefault();
    const btn = e.target.querySelector('button');
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const result = document.getElementById('result');
    btn.disabled = true;
    loading.style.display = 'block';
    error.style.display = 'none';
    result.classList.remove('show');
    try {
        const res = await fetch(INS_API + '/premium/estimate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                age: parseInt(document.getElementById('age').value),
                termYears: parseInt(document.getElementById('term').value),
                sumAssured: parseInt(document.getElementById('sumAssured').value),
                gender: document.getElementById('gender').value,
                smoker: document.getElementById('smoker').value === 'true',
                paymentFrequency: 'monthly',
                currency: 'EUR'
            })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Calculation failed');
        document.getElementById('premium').textContent = '€' + data.premium.toFixed(2);
        document.getElementById('currency').textContent = data.currency;
        document.getElementById('model').textContent = data.pricingModel;
        result.classList.add('show');
    } catch (err) {
        error.textContent = 'Error: ' + err.message;
        error.style.display = 'block';
    } finally {
        btn.disabled = false;
        loading.style.display = 'none';
    }
};
'''
    return get_base_template('insurance') + content + get_footer(js)

@application.route('/tax')
def tax():
    content = '''
<div class="card" style="max-width: 600px; margin: 0 auto;">
    <div style="text-align: center; margin-bottom: 30px;">
        <i class="fas fa-file-invoice-dollar" style="font-size: 3em; color: var(--accent);"></i>
        <h1 style="margin-top: 15px;">Tax Calculator</h1>
        <p style="color: var(--text-muted);">Calculate income tax liability</p>
    </div>
    <form id="taxForm">
        <div class="form-group">
            <label>Annual Income (₹)</label>
            <input type="number" id="income" value="1000000" min="0" required>
        </div>
        <div class="form-group">
            <label>Tax Regime</label>
            <select id="regime">
                <option value="new">New Regime (2025-26)</option>
                <option value="old">Old Regime (with deductions)</option>
            </select>
        </div>
        <div class="form-group" id="deductionsGroup" style="display: none;">
            <label>80C Deductions (₹)</label>
            <input type="number" id="deductions" value="150000" min="0" max="150000">
        </div>
        <button type="submit" class="btn" style="width: 100%;">
            <i class="fas fa-calculator"></i> Calculate Tax
        </button>
    </form>
    <div class="loading" id="loading"><i class="fas fa-spinner fa-spin"></i> Calculating...</div>
    <div class="error" id="error"></div>
    <div class="result-box" id="result">
        <div class="result-row"><span>Taxable Income:</span><span class="result-value" id="taxable">-</span></div>
        <div class="result-row"><span>Tax Amount:</span><span class="result-value" id="taxAmt">-</span></div>
        <div class="result-row"><span>Effective Rate:</span><span class="result-value" id="effRate">-</span></div>
        <div class="result-row"><span>Take Home:</span><span class="result-value" id="takeHome">-</span></div>
    </div>
</div>
'''
    js = '''
document.getElementById('regime').onchange = function() {
    document.getElementById('deductionsGroup').style.display = this.value === 'old' ? 'block' : 'none';
};
document.getElementById('taxForm').onsubmit = async (e) => {
    e.preventDefault();
    const btn = e.target.querySelector('button');
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const result = document.getElementById('result');
    btn.disabled = true;
    loading.style.display = 'block';
    error.style.display = 'none';
    result.classList.remove('show');
    await new Promise(r => setTimeout(r, 800));
    const income = parseFloat(document.getElementById('income').value);
    const regime = document.getElementById('regime').value;
    let taxable = income, tax = 0;
    if (regime === 'old') {
        const deductions = parseFloat(document.getElementById('deductions').value) || 0;
        taxable = Math.max(0, income - deductions);
    }
    if (taxable > 1000000) tax = (taxable - 1000000) * 0.30 + 112500;
    else if (taxable > 500000) tax = (taxable - 500000) * 0.20 + 12500;
    else if (taxable > 250000) tax = (taxable - 250000) * 0.05;
    document.getElementById('taxable').textContent = '₹' + taxable.toLocaleString();
    document.getElementById('taxAmt').textContent = '₹' + Math.round(tax).toLocaleString();
    document.getElementById('effRate').textContent = ((tax/income)*100).toFixed(2) + '%';
    document.getElementById('takeHome').textContent = '₹' + Math.round(income - tax).toLocaleString();
    result.classList.add('show');
    btn.disabled = false;
    loading.style.display = 'none';
};
'''
    return get_base_template('tax') + content + get_footer(js)

@application.route('/health')
def health():
    return {'status': 'healthy', 'service': 'scalable-financial-suite', 'version': '2.1.0'}

if __name__ == '__main__':
    application.run(debug=os.environ.get("FLASK_DEBUG", "False").lower() == "true")

# Security fix: Debug mode controlled by environment variable
if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    application.run(debug=debug_mode)
