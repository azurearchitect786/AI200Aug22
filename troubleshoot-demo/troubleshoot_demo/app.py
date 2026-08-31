from flask import Flask, render_template_string, jsonify
import os

app = Flask(__name__)

# Complete mock database catalog
# Items marked with 'is_recommendation_only: True' will not appear in the original main product catalog list.
PRODUCTS = {
    "1": {"name": "Premium Wireless Headphones", "price": "₹4,999", "img_id": "101", "similar": ["101", "102", "103"], "is_recommendation_only": False},
    "2": {"name": "Pro Bluetooth Speaker", "price": "₹2,499", "img_id": "201", "similar": ["104", "105", "106"], "is_recommendation_only": False},
    "3": {"name": "Active Smart Watch", "price": "₹3,999", "img_id": "301", "similar": ["101", "105", "104"], "is_recommendation_only": False},
    
    # Exclusively recommended items (Hidden entirely from the original catalog view)
    "101": {"name": "Noise Cancelling Earbuds", "price": "₹6,999", "img_id": "11", "similar": [], "is_recommendation_only": True},
    "102": {"name": "Hard Shell Travel Case", "price": "₹999", "img_id": "22", "similar": [], "is_recommendation_only": True},
    "103": {"name": "Premium Audio Cable", "price": "₹599", "img_id": "33", "similar": [], "is_recommendation_only": True},
    "104": {"name": "Waterproof Sports Pouch", "price": "₹799", "img_id": "44", "similar": [], "is_recommendation_only": True},
    "105": {"name": "Heavy Bass Subwoofer Accessory", "price": "₹1,899", "img_id": "55", "similar": [], "is_recommendation_only": True},
    "106": {"name": "Fast Wireless Charging Dock", "price": "₹1,499", "img_id": "66", "similar": [], "is_recommendation_only": True}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Isolated Recommendation Engine</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f7f6; color: #333; }
        .container { max-width: 900px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; margin-top: 20px; }
        .product-card { border: 1px solid #e0e0e0; padding: 15px; border-radius: 8px; background: #fff; cursor: pointer; transition: all 0.2s ease-in-out; text-align: center; }
        .product-card:hover { border-color: #0078d4; transform: translateY(-3px); box-shadow: 0 4px 10px rgba(0,120,212,0.1); background: #fbfdff; }
        .product-img { width: 100%; height: 160px; object-fit: cover; border-radius: 6px; background-color: #eee; margin-bottom: 10px; }
        .recommendations { margin-top: 40px; padding-top: 25px; border-top: 3px dashed #0078d4; display: none; }
        .rec-grid { display: flex; gap: 20px; overflow-x: auto; padding-bottom: 10px; }
        .rec-card { border: 2px solid #e1f0fc; padding: 15px; border-radius: 8px; flex: 1; min-width: 200px; background: #fff; text-align: center; }
        .rec-img { width: 100%; height: 110px; object-fit: cover; border-radius: 6px; margin-bottom: 8px; }
        .price { color: #0078d4; font-weight: bold; font-size: 1.1em; margin: 5px 0; }
    </style>
</head>
<body>
<div class="container">
    <h2>🛍️ Premium Product Store</h2>
    <p>Select an original item to display its standalone, exclusive add-on recommendations:</p>
    
    <div class="grid">
        {% for id, prod in products.items() %}
        {% if not prod.is_recommendation_only %}
        <div class="product-card" onclick="fetchIsolatedRecommendations('{{ id }}', '{{ prod.name }}')">
            <img class="product-img" src="https://picsum.photos{{ prod.img_id }}/300/200" alt="{{ prod.name }}">
            <h3>{{ prod.name }}</h3>
            <p class="price">{{ prod.price }}</p>
        </div>
        {% endif %}
        {% endfor %}
    </div>

    <div id="rec-section" class="recommendations">
        <h3>✨ Top 3 Recommended Matchings for <span id="target-product" style="color:#0078d4;"></span>:</h3>
        <div id="rec-list" class="rec-grid"></div>
    </div>
</div>

<script>
function fetchIsolatedRecommendations(id, name) {
    document.getElementById('target-product').innerText = name;
    fetch('/recommend/' + id)
        .then(response => response.json())
        .then(data => {
            const list = document.getElementById('rec-list');
            list.innerHTML = '';
            data.forEach(item => {
                list.innerHTML += `
                    <div class="rec-card">
                        <img class="rec-img" src="https://picsum.photos${item.img_id}/200/150" alt="${item.name}">
                        <h4>${item.name}</h4>
                        <p class="price">${item.price}</p>
                    </div>`;
            });
            document.getElementById('rec-section').style.display = 'block';
            document.getElementById('rec-section').scrollIntoView({ behavior: 'smooth' });
        });
}
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, products=PRODUCTS)

@app.route('/recommend/<product_id>')
def recommend(product_id):
    target = PRODUCTS.get(product_id)
    if not target:
        return jsonify([])
    recs = [PRODUCTS[rec_id] for rec_id in target["similar"] if rec_id in PRODUCTS]
    return jsonify(recs)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
