from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/urbanaperu'
db = SQLAlchemy(app)

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, nullable=False)
    district = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    property_type = data['propertyType']
    bedrooms = int(data['bedrooms'])
    bathrooms = int(data['bathrooms'])
    phone = data['phone']
    location = data['location']

    # Extraer distrito y ciudad de la ubicación
    location_parts = location.split(',')
    district = location_parts[0].strip() if len(location_parts) > 0 else None
    city = location_parts[1].strip() if len(location_parts) > 1 else None

    if district and city:
        # Realizar la búsqueda en la base de datos
        result = db.session.execute(text(
            """SELECT AVG(price) as avg_price, COUNT(*) as count 
               FROM property 
               WHERE type = :type 
               AND bedrooms = :bedrooms 
               AND bathrooms = :bathrooms 
               AND district = :district 
               AND city = :city"""
        ), {
            "type": property_type,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "district": district,
            "city": city
        }).fetchone()
        
        if result and result.count > 0:
            response = f"Hemos encontrado {result.count} propiedades que coinciden con tu búsqueda. "
            response += f"El precio promedio de un/a {property_type} con {bedrooms} habitaciones y {bathrooms} baños "
            response += f"en {district}, {city} es de ${result.avg_price:.2f}. "
            response += f"Te enviaremos las mejores opciones al número {phone}."
        else:
            response = f"Lo siento, no tenemos propiedades que coincidan exactamente con tus criterios en {district}, {city}. "
            response += "Te sugerimos ampliar tu búsqueda o contactarnos para opciones personalizadas."
    else:
        response = "Por favor, especifica el distrito y la ciudad en el campo de ubicación."
    
    return jsonify({"result": response})

if __name__ == '__main__':
    app.run(debug=True)
