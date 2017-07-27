import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session, url_for
from flask_wtf import FlaskForm
from wtforms import DateField, SelectField
import pandas as pd 
import numpy as np

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

DATABASEURI = "postgresql://sx2182:1234@35.185.80.252/w4111"

engine = create_engine(DATABASEURI)
conn = engine.connect()


def get_geolocation_data(address_string,country='ALL',types=False):
    final = list()
    import requests
    url="https://maps.googleapis.com/maps/api/geocode/json?address=%s" % (address_string)
    response = requests.get(url)
    if not response.status_code == 200:
        return None
    data = response.json()
    if not data['status'] == "OK":
        return None
    for one_result in data['results']:
        lat_lng_list=list()
        f_address = one_result['formatted_address']
        latitude = one_result['geometry']['location']['lat']
        longitude = one_result['geometry']['location']['lng']
        rcountry = f_address.split(", ")[-1]
        lat_lng_list=[f_address,latitude,longitude]
        
        if (types==True):
            lat_lng_list.append(one_result["types"])
        
        if (country!="ALL"):
            if (rcountry==country):
                final.append(lat_lng_list)
        else:
            final.append(lat_lng_list)
    
    if len(final)!=0:
        return final[0]
    else:
        return None

@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request 
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request.

    The variable g is globally accessible.
    """
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback; traceback.print_exc()
        g.conn = None

@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't, the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass

@app.route('/')
def index():
    return render_template("index.html")



@app.route('/recommend',methods = ['POST'])
def recommend():
    out = []
    priority = str(request.form.get('get_priority'))
    disease = request.form.get('get_disease')
    cost = request.form.get('get_cost')
    zip_code = request.form.get('get_zip')
    if priority == 'disease':
        if disease =='invalid':
            out.append('Please select a symptom.')
            context = dict(data = out)
            return render_template('index.html',**context)

        else:
            
            doc_name = []
            doc_spec = []
            hos_name = []
            locations = []
            qry = conn.execute("SELECT  D.dname as doctor, D.spec as specialization, H.name as hospital_name FROM  doctors D JOIN hospitals H ON D.hid=H.hid WHERE D.spec = '{}'".format(disease))
            
            for i in qry:
                doc_name.append(i['doctor'])
                doc_spec.append(i['specialization'])
                hos_name.append(i['hospital_name'])
                location = get_geolocation_data(i['hospital_name'])
                locations.append(location)
                
            #location = get_geolocation_data('Orange Regional Medical Center-Goshen Campus')
            #locations.append(location)
            print(locations)
            use1 = np.asarray(doc_name)
            use2 = np.asarray(doc_spec)
            use3 = np.asarray(hos_name)
            df = pd.DataFrame(list(zip(use1,use2,use3)),columns=['doctor','specialization','hospital name'])
            df.index = np.arange(1, len(df) + 1) 
            
            if cost=='invalid':
                cost = 'unspecified'
            if zip_code=='invalid':
                zip_code = 'unspecified'
            user = 'Your selected symptom ' + str(disease) + " with median cost "+ str(cost) + ' and zip code ' + str(zip_code)

            if len(df)!=0:
                rec = 'Here are our recommendations:'
            else:
                rec = 'Sorry! Our database is too small to give you any helpful recommendations.'



            qry.close()
            lat = 40.7589
            lon = -73.9851

            return render_template("index.html", user = user, rec = rec, table = df.to_html(), results_list = locations, lat= lat, lon = lon)
        
    elif priority =='zipcode':
        
        if zip_code =='invalid' or disease == 'invalid' or cost=='invalid':
            out.append('please enter a valid zipcode, a symptom and a cost range')
            context = dict(data = out)
            return render_template('index.html',**context)
        else:
            doc_name = []
            doc_spec = []
            hos_name = []
            avgcost = []
            locations = []
            lc = int(request.form.get('get_cost'))-5000
            uc = int(request.form.get('get_cost'))+5000
            qry = conn.execute("select T.dname as doc_name, T.spec as doc_spec, T.name as hos_name, avg(T.cost) as avgcost \
                 from (select D.dname, D.spec, H.name, abs(H.zipcode - {}) as dist, P.cost as cost\
                  from doctors D join hospitals H on D.hid = H.hid join pay P ON P.hid=H.hid\
                  where D.spec = '{}' and {}<P.cost and P.cost<{})T \
                 GROUP BY T.dname, T.spec, T.name, T.dist ORDER BY T.dist, avgcost".format(int(zip_code),disease,lc,uc))
            for i in qry:
                doc_name.append(i['doc_name'])
                doc_spec.append(i['doc_spec'])
                hos_name.append(i['hos_name']) 
                avgcost.append(i['avgcost'])
                location = get_geolocation_data(i['hos_name'])
                locations.append(location)   
            use1 = np.asarray(doc_name)
            use2 = np.asarray(doc_spec)
            use3 = np.asarray(hos_name)
            use4 = np.asarray(avgcost)
            df = pd.DataFrame(list(zip(use1,use2,use3,use4)),columns=['doctor','specialization','hospital name','average cost'])
            df.index = np.arange(1, len(df) + 1)  

            user = 'Your selected symptom ' + str(disease) + " with median cost "+ str(cost) + ' and zip code ' + str(zip_code)


            lat = 40.7589
            lon = -73.9851


            if len(df)!=0:
                rec = 'Here are our recommendations:'
            else:
                rec = 'Sorry! Our database is too small to give you any helpful recommendation.'           
            qry.close()
            return render_template("index.html", user = user, rec = rec, table = df.to_html(),results_list = locations, lat= lat, lon = lon)
       

    else:
        
        if cost =='invalid':
            out.append('please enter a valid price range')
            context = dict(data = out)
            return render_template('index.html',**context)
        else:
            
            lc = int(request.form.get('get_cost'))-5000
            uc = int(request.form.get('get_cost'))+5000
            hos_name = []
            avgcost = []
            locations = []
            qry = conn.execute("select T.name as hos_name, AVG(T.cost) as avgcost from (select H.name, P.cost as cost from hospitals H join pay P on P.hid=H.hid where {}<P.cost and P.cost<{}) T GROUP BY T.name ORDER BY avgcost".format(lc,uc))
            for i in qry:
                hos_name.append(i['hos_name'])
                avgcost.append(i['avgcost'])
                location = get_geolocation_data(i['hos_name'])
                locations.append(location)
            use1 = np.asarray(hos_name)
            use2 = np.asarray(avgcost)
            df = pd.DataFrame(list(zip(use1,use2)),columns=['hospital','average cost'])
            df.index = np.arange(1, len(df) + 1) 
            
            if disease=='invalid':
                disease = 'unspecified'
            if zip_code=='invalid':
                zip_code = 'unspecified'
            user = 'Your selected symptom ' + str(disease) + " with median cost "+ str(cost) + ' and zip code ' + str(zip_code)

            if len(df)!=0:
                rec = 'Here are our recommendations:'
            else:
                rec = 'Sorry! Our database is too small to give you any responsible recommendation.'

            qry.close()


            lat = 40.7589
            lon = -73.9851

            return render_template("index.html", user = user, rec = rec, table = df.to_html(),results_list = locations, lat= lat, lon = lon)




if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using:

                python server.py

        Show the help text using:

                python server.py --help

        """

        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


    run()





