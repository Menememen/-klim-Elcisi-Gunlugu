from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import random # Rastgele öneriler için ekledik

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# İklim Önerileri Listesi
tips = [
    "Bugün plastik pipet kullanmayarak deniz kaplumbağalarını korudun!",
    "Kısa mesafeleri yürüyerek karbon ayak izini azalttığın için teşekkürler.",
    "Gereksiz yanan bir ışığı söndürmek, küçük ama dev bir adımdır.",
    "Geri dönüşüm yaparak dünyanın nefes almasına yardımcı oldun!"
]

# Tablo Modeli (score sütununu ekledik)
class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    score = db.Column(db.Integer, default=0) # Eko-Puan alanı

    def __repr__(self):
        return f'<Card {self.id}>'

@app.route('/')
def index():
    cards = Card.query.order_by(Card.id.desc()).all() # En yeni en üstte
    random_tip = random.choice(tips) # Rastgele bir öneri seç
    return render_template('index.html', cards=cards, tip=random_tip)

@app.route('/card/<int:id>')
def card(id):
    card = Card.query.get_or_404(id)
    return render_template('card.html', card=card)

@app.route('/create')
def create():
    return render_template('create_card.html')

@app.route('/form_create', methods=['GET','POST'])
def form_create():
    if request.method == 'POST':
        title = request.form['title']
        subtitle = request.form['subtitle']
        text = request.form['text']

        # --- EKO-PUAN ANALİZİ (GÖREV #1) ---
        score = 0
        eco_keywords = {
            "bisiklet": 20, "yürüdüm": 15, "fidan": 50, 
            "plastik": 10, "tasarruf": 20, "geri dönüşüm": 30
        }
        
        lower_text = text.lower()
        for word, points in eco_keywords.items():
            if word in lower_text:
                score += points
        # -----------------------------------

        card = Card(title=title, subtitle=subtitle, text=text, score=score)

        db.session.add(card)
        db.session.commit()
        return redirect('/')
    else:
        return render_template('create_card.html')

if __name__ == "__main__":
    with app.app_context(): # Veritabanını otomatik oluşturur
        db.create_all()
    app.run(debug=True)