@app.get("/emi", tags=["Tools"])
async def emi_page():
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
<title>EMI Calculator</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:Arial;background:#0f172a;color:white;text-align:center;padding:20px}
.card{background:#1e293b;padding:20px;border-radius:12px;max-width:500px;margin:auto}
input{width:90%;padding:10px;margin:8px;border-radius:8px;border:none}
button{padding:12px 20px;border:none;border-radius:8px;background:#2563eb;color:white}
</style>
</head>
<body>
<div class="card">
<h1>💰 EMI Calculator</h1>
<p>This is the first customer-facing tool.</p>
<p>API Endpoint:</p>
<code>/api/loan-emi?principal=1000000&annual_rate=8.5&years=20</code>
<br><br>
<a href="/docs"><button>Open API Docs</button></a>
</div>
</body>
</html>
""")
