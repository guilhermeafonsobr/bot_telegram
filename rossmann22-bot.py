import json
import os
import pandas as pd
import requests 

from flask import Flask, request, Response

# constants 
token = '5919692325:AAHk1sy3K0Q9SZ5aEVY5sdrT0gUWYHIW_JI'

# info about the bot 
#https://api.telegram.org/bot5919692325:AAHk1sy3K0Q9SZ5aEVY5sdrT0gUWYHIW_JI/getMe

#get update
#https://api.telegram.org/bot5919692325:AAHk1sy3K0Q9SZ5aEVY5sdrT0gUWYHIW_JI/getUpdates

#webhoook localhostrun
#https://api.telegram.org/bot5919692325:AAHk1sy3K0Q9SZ5aEVY5sdrT0gUWYHIW_JI/setWebhook?url=faltaurl

# webhook render
#https://api.telegram.org/bot5919692325:AAHk1sy3K0Q9SZ5aEVY5sdrT0gUWYHIW_JI/setWebhook?url=https://bot-telegram-rossmann-4ssz.onrender.com

#send message 
#https://api.telegram.org/bot5919692325:AAHk1sy3K0Q9SZ5aEVY5sdrT0gUWYHIW_JI/sendMessage?chat_id=873125626&text=Hi, Sabrina. I am doing good, thanks!

def send_message(chat_id, text): 
    url = 'https://api.telegram.org/bot{}/'.format(token) 
    url = url + 'sendMessage?chat_id={}'.format(chat_id)
    
    requests.post(url, json={'text': text})
    print('Status Code {}'.format(r.status_code))

    return  None

def load_dataset(store_id): 
    #loading test dataset
    df10= pd.read_csv('test.csv')
    df_store_raw= pd.read_csv('store.csv')

    # merge test dataset + store
    df_test = pd.merge(df10, df_store_raw, how='left', on='Store' )

    # choosse store for prediction
    df_test = df_test[df_test['Store'] == store_id]

    if not df_test.empty:   
        # remove closed days
        df_test= df_test[df_test['Open'] !=0]
        df_test= df_test[~df_test['Open'].isnull()]
        df_test = df_test.drop('Id', axis=1)

        #convert dataframe to json
        data = json.dumps(df_test.to_dict(orient='records'))
    else:
        data = 'error'

    return data 

def predict (data): 
    #API call
    url='https://teste-rossmann-api-u8lb.onrender.com/rossmann22/predict' 
    header= {'Content-type': 'application/json'}
    data= data

    r = requests.post( url, data=data, headers=header)
    print('Status Code {}'.format(r.status_code))

    d1=pd.DataFrame(r.json(), columns=r.json()[0].keys())

    return d1

def parse_message(message): 
    chat_id = message['message']['chat']['id']
    store_id = message['message']['text']
    
    store_id=store_id.replace('/', '')


    return chat_id, store_id


#API initialize
app= Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index(): 
    if request.method == 'POST': 
        message = request.get_json()

        chat_id, store_id = parse_message(message)
    
        if store_id != 'error': 
        #loading data
            data=load_dataset(store_id)
        
            if data != 'error':
            #prediction 
                d1=predict(data)

            #calculation 
                d2 = d1[['store', 'prediction']].groupby('store').sum().reset_index()
            #send message
                msg = 'Store number {} will sell R${:,.2f} in the next 6 weeks'.format(d2['store'].values[0], d2['prediction'].values[0])

                send_message(chat_id, msg) 
                return Response('Ok', status=200)
            #send message
            else:
                 send_message(chat_id, 'Store not available')
                 return Response('Ok', status=200)
        else: 
             send_message(chat_id, 'Store ID is Wrong') 
             return Response ('OK', status=200) 
    else:
         return '<h1> Rossmann Telegram BOT <h1>'

if __name__== '__main__':
    port = os.environ.get('PORT', 5000)
    app.run(host='0.0.0.0', port=port)

