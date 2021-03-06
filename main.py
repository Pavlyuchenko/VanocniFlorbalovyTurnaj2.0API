from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from datetime import datetime, timedelta


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
cors = CORS(app)


class Tym(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    hraci = db.relationship('Hrac', backref='Tym', lazy=True, cascade="all, delete-orphan")

    nazev = db.Column(db.String(12), nullable=False)
    potvrzeno = db.Column(db.Boolean, nullable=False, default=False)
    zaplaceno = db.Column(db.Boolean, nullable=False, default=False)
    time_created = db.Column(db.DateTime, default=datetime.utcnow)

    odehrane_zapasy = db.Column(db.Integer, default=0)
    vyhry = db.Column(db.Integer, default=0)
    remizy = db.Column(db.Integer, default=0)
    prohry = db.Column(db.Integer, default=0)
    vstrelene_goly = db.Column(db.Integer, default=0)
    obdrzene_goly = db.Column(db.Integer, default=0)
    body = db.Column(db.Integer, default=0)
    skupina = db.Column(db.String(1))

    domaci = db.relationship('Zapas', backref='Domaci', lazy='dynamic', cascade="all, delete-orphan", foreign_keys='Zapas.domaci')
    hoste = db.relationship('Zapas', backref='Hoste', lazy='dynamic', cascade="all, delete-orphan", foreign_keys='Zapas.hoste')

    def __repr__(self):
        return '<Tým %r, %r>' % (self.nazev, self.zaplaceno)  # self.group_id

    def jsonify(self):
        hraci = Hrac.query.filter_by(tym_id=self.id)
        hraci_arr = []

        for hrac in hraci:
            hraci_arr.append({'jmeno': hrac.jmeno, 'trida': hrac.trida})

        return {
            "id": self.id,
            "nazev": self.nazev,
            "potvrzeno": self.potvrzeno,
            "zaplaceno": self.zaplaceno,
            "hraci": hraci_arr,
            "vyhry": self.vyhry,
            "remizy": self.remizy,
            "prohry": self.prohry,
            "vstrelene_goly": self.vstrelene_goly,
            "obdrzene_goly": self.obdrzene_goly,
            "body": self.body,
            "zapasy": self.odehrane_zapasy,
            "skupina": self.skupina
        }

    def jsonify_adming(self):
        hraci = Hrac.query.filter_by(tym_id=self.id)
        hraci_arr = []

        for hrac in hraci:
            hraci_arr.append({'jmeno': hrac.jmeno, 'trida': hrac.trida})

        return {
            "id": self.id,
            "nazev": self.nazev,
            "hraci": hraci_arr
        }


class Hrac(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    tym_id = db.Column(db.Integer, db.ForeignKey('tym.id'), nullable=False)

    jmeno = db.Column(db.String(200), nullable=False)
    trida = db.Column(db.String(5), nullable=False)


class Zapas(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    domaci = db.Column(db.Integer, db.ForeignKey('tym.id'))
    hoste = db.Column(db.Integer, db.ForeignKey('tym.id'))
    skore = skore = db.Column(db.String(10))

    order = db.Column(db.Integer, unique=True)

    def jsonify(self):
        return {
            'id': self.id,
            'domaci': self.Domaci.nazev,
            'hoste': self.Hoste.nazev,
            'order': self.order,
            'skore1': self.skore.split(":")[0],
            'skore2': self.skore.split(":")[1]
        }


class Statistika(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    navstevnici = db.Column(db.Integer, nullable=False)


class Casovac(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    cas = db.Column(db.String(100))
    pause_cas = db.Column(db.String(100))
    pause = db.Column(db.Boolean)

    current_order = db.Column(db.Integer, default=0)

    current_phase = db.Column(db.Integer, default=1)  # 1 = Registrace týmů, 2 = Skupinová fáze, 3 = Pavouk

    def jsonify(self):

        if self.cas == "0:00":
          tm = "0:0"
        elif self.pause:
            tm = self.pause_cas
        else:
            tm = datetime.strptime(self.cas, "%Y-%m-%d %H:%M:%S.%f") - datetime.now()
            tm = str(tm).split(":")
            tm = str(11 - int(tm[1])) + ":" + str(59 - int(tm[2].split(".")[0]))
            print(tm)

        return {
            'minuty': tm.split(":")[0],
            'sekundy': tm.split(":")[1],
            'order': self.current_order,
            'pause': self.pause,
        }

    def debug(self):
        return {
            'casovac': self.cas
        }


@app.route('/init', methods=['GET', 'POST'])
def init():
    casovac = Casovac(cas=datetime.today() + timedelta(minutes=11, seconds=60))
    db.session.add(casovac)
    db.session.commit()

    tymy = ['Vygrachanci', 'Antišunkofleci', 'Boney M', 'Učitelé', 'Pobo Team', 'Milanovi Kořeni']

    for i in tymy:
        tym = Tym(nazev=i, potvrzeno=False, zaplaceno=False)
        db.session.add(tym)
        db.session.commit()

    hraci = [[{'jmeno': 'Michal Pavlíček', 'trida': '6.A'}, {'jmeno': 'Tomáš Adamec', 'trida': '6.A'}, {'jmeno': 'Lukáš Procházka', 'trida': '6.A'}, {'jmeno': 'Vojta Olšr', 'trida': '6.A'}],
             [{'jmeno': 'Erik Schonwalder', 'trida': '6.A'}, {'jmeno': 'Adam Lehnert', 'trida': '1.C'}, {'jmeno': 'Šimon Benš', 'trida': '6.A'}, {'jmeno': 'Dave Langer', 'trida': '6.A'}],
             [{'jmeno': 'Tomáš Nagy', 'trida': '8.A'}, {'jmeno': 'Žirafoun Druhý', 'trida': '8.A'}, {'jmeno': 'Komiksák Druhý', 'trida': '8.A'}, {'jmeno': 'Malohoštický Zmrd', 'trida': '8.A'}],
             [{'jmeno': 'Aleš Staněk', 'trida': ''}, {'jmeno': 'Martin Kuček', 'trida': ''}, {'jmeno': 'Daniel Honka', 'trida': ''}, {'jmeno': 'Daniel Vítek', 'trida': ''}],
             [{'jmeno': 'Milan Pobořil', 'trida': ''}, {'jmeno': 'Petr Janšta', 'trida': ''}, {'jmeno': 'Fakový Loupakis', 'trida': ''}, {'jmeno': 'Marie Koutná', 'trida': ''}],
             [{'jmeno': 'Michal Pavlíček', 'trida': '6.A'}, {'jmeno': 'Tomáš Adamec', 'trida': '6.A'}, {'jmeno': 'Lukáš Procházka', 'trida': '6.A'}, {'jmeno': 'Vojta Olšr', 'trida': '6.A'}]
            ]

    tym_id = 0
    for i in hraci:
        tym_id += 1
        for j in i:
            print(j)
            plejer = Hrac(jmeno=j['jmeno'], trida=j['trida'], tym_id=tym_id)
            db.session.add(plejer)

    db.session.commit()

    for i in range(1, 5):
        zapas = Zapas(domaci=i, hoste=i+1, order=i*10, skore="0:0")
        db.session.add(zapas)
    db.session.commit()

    return 'success'


@app.route('/debug', methods=['GET', 'POST'])
@cross_origin()
def debug():
    casovac = Casovac.query.first()

    return jsonify({'casovac': casovac.debug()})


@app.route('/main', methods=['GET', 'POST'])
@cross_origin()
def main():
    casovac = Casovac.query.first()
    zapasy = Zapas.query.order_by(Zapas.order).filter(Zapas.order > casovac.current_order)
    res = []
    count = 0

    for i in zapasy:
        count += 1
        res.append(i.jsonify())
        if count == 5:
            break

    casovac = Casovac.query.first().jsonify()

    tymy = Tym.query.filter(Tym.skupina == zapasy[0].Domaci.skupina)
    tymy_res = []

    for i in tymy:
        tymy_res.append(i.jsonify())

    return jsonify({'zapasy': res, 'casovac': casovac, 'tymy': tymy_res})


@app.route('/adming', methods=['GET', 'POST'])
@cross_origin()
def adming():
    casovac = Casovac.query.first()

    zapasy = Zapas.query.order_by(Zapas.order).filter(Zapas.order > casovac.current_order)
    res = []
    count = 0

    for i in zapasy:
        count += 1
        res.append(i.jsonify())

    odehrane_zapasy = Zapas.query.order_by(Zapas.order).filter(Zapas.order <= casovac.current_order)
    od_zap_res = []
    count = 0

    for i in odehrane_zapasy:
        count += 1
        od_zap_res.append(i.jsonify())

    tymy = Tym.query.order_by(Tym.nazev)
    tymy_res = []

    for i in tymy:
        tymy_res.append(i.jsonify())

    return jsonify({'zapasy': res, 'tymy': tymy_res, 'odehrane_zapasy': od_zap_res})


@app.route('/dalsi_zapas', methods=['GET', 'POST'])
@cross_origin()
def dalsi_zapas():
    casovac = Casovac.query.first()
    zapas = Zapas.query.order_by(Zapas.order).filter(Zapas.order > casovac.current_order).first()

    casovac.current_order = zapas.order
    zapas = Zapas.query.order_by(Zapas.order).filter(Zapas.order > casovac.current_order).first()

    casovac.cas = "0:00"
    casovac.pause = True
    casovac.pause_cas = True
    db.session.commit()

    return jsonify({'zapas': zapas.jsonify()})


@app.route('/update_order', methods=['GET', 'POST'])
def update_order():
    json = request.json

    zapas = Zapas.query.filter(Zapas.id == json["id"]).first()
    zapas.order = int(json["order"])

    db.session.commit()

    return 'Success'


@app.route('/update_skore_odehrany_zapas', methods=['GET', 'POST'])
def update_skore_odehrany_zapas():
    json = request.json

    zapas = Zapas.query.filter(Zapas.id == json["id"]).first()
    zapas.skore = json["skore1"] + ":" + json["skore2"]

    db.session.commit()

    return 'Success'


@app.route('/update_tym_statistiky', methods=['GET', 'POST'])
def update_tym_statistiky():
    json = request.json
    tym = Tym.query.filter(Tym.id == json["id"]).first()
    tym.body = json["body"]
    tym.odehrane_zapasy = json["zapasy"]
    tym.vyhry = json["vyhry"]
    tym.remizy = json["remizy"]
    tym.prohry = json["prohry"]
    tym.obdrzene_goly = json["obdrzene_goly"]
    tym.vstrelene_goly = json["vstrelene_goly"]
    tym.skupina = json["skupina"]
    db.session.commit()

    return 'Success'


@app.route('/update_skore', methods=['GET', 'POST'])
def update_skore():
    json = request.json

    casovac = Casovac.query.first()
    zapas = Zapas.query.order_by(Zapas.order).filter(Zapas.order > casovac.current_order).first()
    zapas.skore = str(json['skoreDomaci']) + ":" + str(json['skoreHoste'])

    db.session.commit()

    return jsonify({"success": "success"})


@app.route('/get_teams', methods=['GET'])
def get_teams():
    tymy = Tym.query.order_by(Tym.nazev)
    res = []

    for i in tymy:
        res.append(i.jsonify())
    print(res)
    return jsonify({'tymy': res})


@app.route('/get_tym', methods=['GET', 'POST'])
@cross_origin()
def get_tym():
    json = request.json

    print(json["nazev"])

    tym = Tym.query.filter(Tym.nazev.ilike(json["nazev"])).first()

    if tym:
        tym = tym.jsonify()
    else:
        tym = "No"
    return jsonify({'tym': tym})


@app.route('/get_curr_zapas', methods=['GET'])
@cross_origin()
def get_curr_zapas():
    casovac = Casovac.query.first()

    zapas = Zapas.query.order_by(Zapas.order).filter(Zapas.order > casovac.current_order).first()

    return jsonify({'zapas': zapas.jsonify()})


@app.route('/update_casovac', methods=['GET', 'POST'])
@cross_origin()
def update_casovac():
    json = request.json

    casovac = Casovac.query.first()
    casovac.cas = datetime.today() + timedelta(minutes=11-int(json["minuty"]), seconds=60-int(json["sekundy"]))
    casovac.pause = False

    db.session.commit()

    return jsonify({"success": "success"})


@app.route('/pause_casovac', methods=['GET', 'POST'])
@cross_origin()
def pause_casovac():
    json = request.json

    casovac = Casovac.query.first()
    casovac.pause_cas = str(json["minuty"]) + ":" + str(json["sekundy"])
    casovac.pause = True

    print("heeeeey")

    db.session.commit()

    return jsonify({"success": "success"})


@app.route('/add_zapas', methods=['GET', 'POST'])
@cross_origin()
def add_zapas():
    json = request.json
    print(json)
    zapas = Zapas(domaci=json['domaci_id'], hoste=json['hoste_id'], order=json['order'], skore="0:0")
    db.session.add(zapas)
    db.session.commit()

    return jsonify({"success": "success"})


@app.route('/register', methods=['GET', 'POST'])
@cross_origin()
def register():
    json = request.json

    ''' Deletes everything
    db.session.query(Tym).delete()
    db.session.commit()'''
    tym = Tym(nazev=json['nazevTymu'], potvrzeno=False, zaplaceno=False)
    db.session.add(tym)
    db.session.commit()

    for i in json['hraci']:
        if i['jmeno']:
            hrac = Hrac(tym_id=tym.id, jmeno=i['jmeno'], trida=i['trida'])
            db.session.add(hrac)
    db.session.commit()

    return jsonify({'hello': 'react is kinda great'})


@app.route('/update_potvrzeno', methods=['GET', 'POST'])
@cross_origin()
def update_potvrzeno():
    json = request.json

    tym = Tym.query.filter_by(id=json['idTymu']).first()
    tym.potvrzeno = True
    db.session.commit()

    return jsonify({'hello': 'react is kinda great'})


@app.route('/zaplaceni_potvrzeno', methods=['GET', 'POST'])
@cross_origin()
def zaplaceni_potvrzeno():
    json = request.json

    tym = Tym.query.filter_by(id=json['idTymu']).first()
    tym.zaplaceno = not tym.zaplaceno
    db.session.commit()

    return jsonify({'hello': 'react is kinda great'})


@app.route('/delete_tym', methods=['GET', 'POST'])
@cross_origin()
def delete_tym():
    json = request.json

    tym = Tym.query.filter_by(id=json['idTymu']).first()
    db.session.delete(tym)
    db.session.commit()

    return jsonify({'hello': 'react is kinda great'})


@app.route('/admin', methods=['GET', 'POST'])
@cross_origin()
def admin():

    tymy = Tym.query.order_by(Tym.zaplaceno).order_by(Tym.nazev)

    print(tymy)

    result = []

    for i in tymy:
        result.append(i.jsonify())

    ''' Reset potvrzeno 
    tymy = Tym.query.all()

    for i in tymy:
        i.potvrzeno = False
    db.session.commit()'''

    reg_tymy = db.session.query(Tym).count()

    if db.session.query(Statistika).count() == 0:
        statistika = Statistika(navstevnici=0)
        db.session.add(statistika)
        db.session.commit()
        navstiveno = "initialized"
    else:
        navstiveno = Statistika.query.first().navstevnici

    return jsonify({'tymy': result, 'registrovane_tymy': reg_tymy, 'navstiveno': navstiveno})


@app.route('/statistika', methods=['GET', 'POST'])
@cross_origin()
def statistika():
    json = request.json

    if json['navstevnik']:
        statistika = Statistika.query.first()
        statistika.navstevnici += 1
        db.session.commit()

    return '200'


@app.route('/choose_team', methods=['GET', 'POST'])
@cross_origin()
def choose_team():
    tymy = Tym.query.order_by(Tym.zaplaceno).order_by(Tym.nazev)

    result = []

    for i in tymy:
        result.append(i.jsonify())

    return jsonify({'tymy': result})


@app.route('/get_zapasy', methods=['GET', 'POST'])
@cross_origin()
def get_zapasy():
    res = []
    odeh_res = []

    casovac = Casovac.query.first()
    zapasy = Zapas.query.order_by(Zapas.order).filter(Zapas.order > casovac.current_order)
    for i in zapasy:
        res.append(i.jsonify())

    odeh_zapasy = Zapas.query.order_by(Zapas.order).filter(Zapas.order <= casovac.current_order)
    for i in odeh_zapasy:
        odeh_res.append(i.jsonify())

    return jsonify({'zapasy': res, 'odehrane_zapasy': odeh_res})


if __name__ == '__main__':
    app.run()
