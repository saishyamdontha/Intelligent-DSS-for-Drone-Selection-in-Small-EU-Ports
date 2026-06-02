fetch('http://localhost:8000/ai/overview', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({prompt: 'Say hello in one sentence.'})
}).then(r => r.json()).then(d => console.log(JSON.stringify(d))).catch(e => console.error(e))