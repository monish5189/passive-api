#!/bin/bash

declare -A titles=(
["gst"]="🧾 GST Calculator"
["sip"]="📈 SIP Calculator"
["qr"]="📱 QR Generator"
["crypto"]="₿ Crypto Dashboard"
["weather"]="🌦 Weather Tool"
["bmi"]="⚖ BMI Calculator"
["networth"]="💰 Net Worth Calculator"
["roi"]="📊 ROI Calculator"
["password"]="🔐 Password Tool"
["email"]="📧 Email Validator"
["forex"]="💱 Forex Converter"
)

for tool in "${!titles[@]}"
do
cat > templates/${tool}.html <<HTML

<!DOCTYPE html><html>
<head>
<title>${titles[$tool]}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{
    font-family:Arial;
    background:#0f172a;
    color:white;
    text-align:center;
    padding:20px;
}
.card{
    background:#1e293b;
    padding:20px;
    border-radius:12px;
    max-width:600px;
    margin:auto;
}
.btn{
    display:inline-block;
    padding:12px 20px;
    background:#2563eb;
    color:white;
    text-decoration:none;
    border-radius:8px;
}
</style>
</head>
<body><div class="card">
<h1>${titles[$tool]}</h1><p>This tool is under development.</p><p>Frontend page is ready.</p><p>Backend API already exists.</p><a class="btn" href="/docs">
Open API Docs
</a></div></body>
</html>
HTML
doneecho "All pages generated."
