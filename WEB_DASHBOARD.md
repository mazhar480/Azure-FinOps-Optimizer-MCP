# 🌐 Web Dashboard Guide

**Access Azure FinOps Elite through a beautiful web interface!**

---

## 🚀 Quick Start

### Step 1: Install Flask

```powershell
pip install flask
```

### Step 2: Start the Dashboard

```powershell
python web_dashboard.py
```

### Step 3: Open in Browser

Navigate to: **http://localhost:5000**

---

## 📊 Features

### ⚙️ Configuration Tab
- Configure Azure credentials (Tenant ID, Client ID, Subscription IDs)
- Set anomaly detection threshold
- Configure log level
- Save settings to `.env` file

### 🔍 Anomaly Detection Tab
- Run cost anomaly detection
- Adjust detection threshold
- View results in real-time
- See excess spend and variance percentages

### 🏢 CSP Audit Tab
- Audit subscriptions for wasteful resources
- Identify unattached disks
- Find idle public IPs
- Calculate potential savings

### 🛡️ Governance Tab
- Get Azure Advisor recommendations
- Filter by risk score (1-10)
- View ISO 27001 and NIA Qatar compliance mappings
- See remediation steps and effort estimates

### 📊 Executive Summary Tab
- Generate Markdown-formatted ROI reports
- Choose monthly or annual period
- Download reports for stakeholder presentations
- View summary metrics

### 📁 Reports Tab
- Browse all generated reports
- Download reports
- See creation timestamps
- Manage report history

---

## 🎨 Dashboard Features

- **Beautiful UI**: Modern gradient design with smooth animations
- **Responsive**: Works on desktop, tablet, and mobile
- **Real-time**: Live updates as tools run
- **Easy Configuration**: No need to edit files manually
- **Report Management**: Download and share executive summaries

---

## 🔧 Advanced Usage

### Custom Port

```powershell
# Edit web_dashboard.py, change the last line:
app.run(debug=True, host='0.0.0.0', port=8080)
```

### Remote Access

```powershell
# Allow access from other machines on your network
# The dashboard is already configured for 0.0.0.0
# Access from other machines: http://YOUR_IP:5000
```

### Production Deployment

For production use, deploy with a proper WSGI server:

```powershell
pip install gunicorn

# Run with gunicorn (Linux/Mac)
gunicorn -w 4 -b 0.0.0.0:5000 web_dashboard:app

# Run with waitress (Windows)
pip install waitress
waitress-serve --port=5000 web_dashboard:app
```

---

## 📸 Screenshots

The dashboard includes:
- **Purple gradient theme** for a premium look
- **Tab-based navigation** for easy access to all tools
- **Loading animations** while processing
- **JSON results display** for detailed data
- **Download links** for generated reports

---

## 🔐 Security Notes

- The dashboard runs on **localhost by default** (127.0.0.1)
- For remote access, ensure proper firewall rules
- Use HTTPS in production (configure with nginx/Apache)
- Protect with authentication if exposing publicly

---

## 🐛 Troubleshooting

### Issue: "Address already in use"

**Solution:**
```powershell
# Change the port in web_dashboard.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Issue: "Module 'flask' not found"

**Solution:**
```powershell
pip install flask
```

### Issue: "Template not found"

**Solution:**
Ensure the `templates` folder exists with `dashboard.html` inside.

---

## 🎯 Next Steps

1. **Start the dashboard**: `python web_dashboard.py`
2. **Configure credentials**: Go to Configuration tab
3. **Run your first analysis**: Try Anomaly Detection
4. **Generate a report**: Create an Executive Summary
5. **Share with stakeholders**: Download and present reports

---

**Enjoy your GUI-powered FinOps experience! 🎉**
