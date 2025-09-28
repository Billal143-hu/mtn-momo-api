from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import time

app = FastAPI(title="MTN Mobile Money API", version="1.0")

# Store data
agent_data = {
    "balance": 10000.00,
    "transactions": [],
    "agent_id": "MTN_AGENT_001"
}

class TransactionRequest(BaseModel):
    customer_phone: str
    amount: float
    transaction_type: str

@app.get("/")
async def home():
    return {"message": "🚀 MTN Mobile Money API is LIVE!", "status": "active"}

@app.get("/api/balance")
async def get_balance():
    return {
        "success": True,
        "balance": agent_data["balance"],
        "currency": "GHS"
    }

@app.post("/api/transaction")
async def process_transaction(request: TransactionRequest):
    # Validate input
    if not request.customer_phone or len(request.customer_phone) < 10:
        raise HTTPException(status_code=400, detail="Invalid phone number")
    
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    if request.transaction_type not in ["deposit", "withdraw"]:
        raise HTTPException(status_code=400, detail="Invalid transaction type")
    
    # Process transaction
    transaction_id = f"MTN{int(time.time())}"
    old_balance = agent_data["balance"]
    
    if request.transaction_type == "deposit":
        if agent_data["balance"] < request.amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        agent_data["balance"] -= request.amount
        message = "Cash deposit successful"
        sms_message = f"MTN MoMo: Deposited GH¢{request.amount:.2f}. Ref: {transaction_id}"
    else:
        agent_data["balance"] += request.amount
        message = "Cash withdrawal successful"
        sms_message = f"MTN MoMo: Withdrew GH¢{request.amount:.2f}. Ref: {transaction_id}"
    
    # Record transaction
    transaction_record = {
        "id": transaction_id,
        "phone": request.customer_phone,
        "amount": request.amount,
        "type": request.transaction_type,
        "timestamp": time.time(),
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "sms_message": sms_message
    }
    
    agent_data["transactions"].append(transaction_record)
    
    # Simulate SMS (will show in logs)
    print(f"📱 SMS SENT to {request.customer_phone}: {sms_message}")
    
    return {
        "success": True,
        "message": message,
        "transaction_id": transaction_id,
        "amount": request.amount,
        "new_balance": agent_data["balance"],
        "sms_sent": True,
        "sms_message": sms_message
    }

@app.get("/api/transactions")
async def get_transactions():
    return {
        "success": True,
        "transactions": agent_data["transactions"][-10:][::-1]
    }

@app.get("/dashboard")
async def dashboard():
    return HTMLResponse("""
<html>
<head>
    <title>MTN Mobile Money</title>
    <style>
        body { font-family: Arial; margin: 40px; background: #f0f0f0; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        .header { background: #ffcc00; padding: 20px; border-radius: 10px; text-align: center; }
        .balance { background: #4CAF50; color: white; padding: 15px; border-radius: 5px; text-align: center; margin: 15px 0; }
        .form-group { margin: 10px 0; }
        input, select, button { width: 100%; padding: 10px; margin: 5px 0; box-sizing: border-box; }
        button { background: #2196F3; color: white; border: none; padding: 12px; border-radius: 5px; cursor: pointer; }
        .result { padding: 10px; border-radius: 5px; margin: 10px 0; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 MTN Mobile Money Agent</h1>
            <p>Real Transaction System</p>
        </div>
        
        <div class="balance">
            <h3>Current Balance</h3>
            <h2 id="balance">GH¢ 0.00</h2>
        </div>
        
        <div class="form-group">
            <h3>Process Transaction</h3>
            <input type="text" id="phone" placeholder="Customer Phone (0551234567)" value="0551234567">
            <input type="number" id="amount" placeholder="Amount (GH¢)" value="100" step="0.01">
            <select id="type">
                <option value="deposit">Cash Deposit</option>
                <option value="withdraw">Cash Withdrawal</option>
            </select>
            <button onclick="processTransaction()">Process Transaction + SMS</button>
        </div>
        
        <div id="result"></div>
        
        <h3>Recent Transactions</h3>
        <div id="transactions"></div>
    </div>

    <script>
        async function loadData() {
            try {
                const balanceResponse = await fetch('/api/balance');
                const balanceData = await balanceResponse.json();
                document.getElementById('balance').textContent = 'GH¢ ' + balanceData.balance.toFixed(2);
                
                const txnResponse = await fetch('/api/transactions');
                const txnData = await txnResponse.json();
                
                let html = '';
                txnData.transactions.forEach(txn => {
                    html += `<div style="padding: 8px; border-bottom: 1px solid #eee; font-size: 14px;">
                        <strong>${txn.phone}</strong> - GH¢ ${txn.amount.toFixed(2)} - ${txn.type}<br>
                        <small>${txn.date} | ${txn.sms_message}</small>
                    </div>`;
                });
                document.getElementById('transactions').innerHTML = html || 'No transactions yet';
            } catch (error) {
                console.error('Error:', error);
            }
        }
        
        async function processTransaction() {
            const phone = document.getElementById('phone').value;
            const amount = parseFloat(document.getElementById('amount').value);
            const type = document.getElementById('type').value;
            
            if (!phone || !amount) {
                alert('Please fill all fields');
                return;
            }
            
            try {
                const response = await fetch('/api/transaction', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        customer_phone: phone,
                        amount: amount,
                        transaction_type: type
                    })
                });
                
                const result = await response.json();
                const resultDiv = document.getElementById('result');
                
                if (result.success) {
                    resultDiv.className = 'result success';
                    resultDiv.innerHTML = `
                        <h4>✅ Transaction Successful!</h4>
                        <p><strong>ID:</strong> ${result.transaction_id}</p>
                        <p><strong>Amount:</strong> GH¢ ${result.amount.toFixed(2)}</p>
                        <p><strong>New Balance:</strong> GH¢ ${result.new_balance.toFixed(2)}</p>
                        <p><strong>SMS:</strong> ${result.sms_message}</p>
                    `;
                } else {
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = `<strong>❌ Error:</strong> ${result.detail}`;
                }
                
                loadData();
            } catch (error) {
                document.getElementById('result').innerHTML = '<div class="result error">❌ Network error</div>';
            }
        }
        
        // Load initial data
        loadData();
    </script>
</body>
</html>
""")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)