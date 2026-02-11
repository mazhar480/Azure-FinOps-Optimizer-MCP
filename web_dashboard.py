"""
Web Dashboard for Azure FinOps Elite
Simple Flask-based GUI for viewing reports and configuring settings
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from datetime import datetime
from dotenv import load_dotenv, set_key

# Import FinOps tools
from tools.anomaly_detector import get_enterprise_anomalies
from tools.csp_auditor import csp_tenant_audit
from tools.budget_validator import validate_deployment_budget
from tools.governance_advisor import governance_remediation_advisor
from tools.executive_summary import generate_executive_summary
from tools.compliance_overlay import apply_compliance_overlay

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Store for generated reports
REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)


@app.route('/')
def index():
    """Dashboard home page"""
    return render_template('dashboard.html')


@app.route('/api/config', methods=['GET', 'POST'])
def config():
    """Get or update configuration"""
    if request.method == 'GET':
        config_data = {
            'AZURE_TENANT_ID': os.getenv('AZURE_TENANT_ID', ''),
            'AZURE_CLIENT_ID': os.getenv('AZURE_CLIENT_ID', ''),
            'AZURE_SUBSCRIPTION_IDS': os.getenv('AZURE_SUBSCRIPTION_IDS', ''),
            'ANOMALY_THRESHOLD': os.getenv('ANOMALY_THRESHOLD', '1.5'),
            'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
        }
        return jsonify(config_data)
    
    elif request.method == 'POST':
        data = request.json
        env_file = '.env'
        
        for key, value in data.items():
            if value:  # Only update non-empty values
                set_key(env_file, key, value)
        
        return jsonify({'status': 'success', 'message': 'Configuration updated'})


@app.route('/api/anomalies', methods=['POST'])
def detect_anomalies():
    """Run anomaly detection"""
    try:
        threshold = float(request.json.get('threshold', 1.5))
        result = get_enterprise_anomalies(threshold=threshold)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/csp-audit', methods=['POST'])
def run_csp_audit():
    """Run CSP tenant audit"""
    try:
        result = csp_tenant_audit()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/validate-budget', methods=['POST'])
def validate_budget():
    """Validate deployment budget"""
    try:
        template = request.json.get('template', {})
        budget_limit = request.json.get('budget_limit')
        region = request.json.get('region', 'eastus')
        
        result = validate_deployment_budget(template, budget_limit, region)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/governance', methods=['POST'])
def get_governance():
    """Get governance recommendations"""
    try:
        min_risk_score = int(request.json.get('min_risk_score', 5))
        result = governance_remediation_advisor(min_risk_score=min_risk_score)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/executive-summary', methods=['POST'])
def create_executive_summary():
    """Generate executive summary"""
    try:
        period = request.json.get('period', 'monthly')
        result = generate_executive_summary(period=period)
        
        # Save report to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"executive_summary_{period}_{timestamp}.md"
        filepath = os.path.join(REPORTS_DIR, filename)
        
        with open(filepath, 'w') as f:
            f.write(result['markdown_report'])
        
        result['report_file'] = filename
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/compliance-check', methods=['POST'])
def check_compliance():
    """Check compliance impact"""
    try:
        recommendations = request.json.get('recommendations', [])
        check_iso27001 = request.json.get('check_iso27001', True)
        check_nia_qatar = request.json.get('check_nia_qatar', True)
        
        result = apply_compliance_overlay(recommendations, check_iso27001, check_nia_qatar)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reports')
def list_reports():
    """List all generated reports"""
    try:
        reports = []
        for filename in os.listdir(REPORTS_DIR):
            if filename.endswith('.md'):
                filepath = os.path.join(REPORTS_DIR, filename)
                stat = os.stat(filepath)
                reports.append({
                    'filename': filename,
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'size': stat.st_size
                })
        
        reports.sort(key=lambda x: x['created'], reverse=True)
        return jsonify(reports)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reports/<filename>')
def download_report(filename):
    """Download a report"""
    try:
        filepath = os.path.join(REPORTS_DIR, filename)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404


if __name__ == '__main__':
    print("🚀 Starting Azure FinOps Elite Web Dashboard")
    print("📊 Dashboard URL: http://localhost:5000")
    print("Press Ctrl+C to stop")
    app.run(debug=True, host='0.0.0.0', port=5000)
