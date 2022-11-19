import joblib
from flask import Flask , request, render_template
from math import ceil
import requests

# NOTE: you must manually set API_KEY below using information retrieved from your IBM Cloud account.
API_KEY = "ACsP3Bo6BnmCyRBl66ImEMRM6P3BbdmHMeuQcxVBCMBw"
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey": API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]

header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}
app = Flask(__name__)
model = joblib.load("model.pkl")

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/predict',methods = ['GET','POST'])
def admin():
    gre=(eval(request.form["gre"])-290)/(340-290)
    tofl=(eval(request.form["tofl"])-92)/(120-92)
    rating=(eval(request.form["rating"])-1.0)/4.0
    sop=(float(request.form["sop"])-1.0)/4.0
    lor=(float(request.form["lor"])-1.0)/4.0
    cgpa=(float(request.form["cgpa"])-5.5)/(10-5.6)
    research=request.form["research"]
    if (research=="Yes"):
        research=1
    else:
        research=0

    array_of_input_fields = ['gre', 'tofl', 'rating', 'sop', 'lor', 'cgpa', 'research']
    array_of_values_to_be_scored = [gre, tofl, rating, sop, lor, cgpa, research]
    payload_scoring = {"input_data": [{"fields": [array_of_input_fields], "values": [array_of_values_to_be_scored]}]}
    response_scoring = requests.post('https://us-south.ml.cloud.ibm.com/ml/v4/deployments/8244ff58-07bb-481d-becc-c4ad94411dc5/predictions?version=2022-11-18', json=payload_scoring, headers={'Authorization': 'Bearer ' + mltoken})
    prediction = response_scoring.json()['predictions'][0]['values'][0][0]

    if (prediction > 0.5):
        return render_template("chance.html",p=str(ceil(prediction *100)) +" %")
    return render_template("nochance.html")
if __name__ == '__main__':
    app.run(debug = True, port=5500)