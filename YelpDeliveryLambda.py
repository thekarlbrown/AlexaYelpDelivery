import requests

client_id = '5_i7R5wN5m042GaXgUTxPg'
client_secret = 'FOR MY EYES ONLY'

token_post_data = {'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret}
yelp_token_url = 'https://api.yelp.com/oauth2/token'
token = requests.post(yelp_token_url, token_post_data)
access_token = token.json()['access_token']
oauth_yelp_headers = {'Authorization': f'bearer {access_token}'}

business_search_base_url = 'https://api.yelp.com/v3/businesses/search'
delivery_areas = ['mclean', 'dc', 'new york city']

def lambda_handler(event, context):
    if (event["session"]["application"]["applicationId"] !=
            "amzn1.ask.skill.b5bbbfb5-ec54-452c-a8eb-8eb180eb1d3c"):
        raise ValueError("Invalid Application ID")

    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

def on_session_started(session_started_request, session):
    print ('Starting new session.')

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    if intent_name == "GetInfo":
        return get_app_info()
    elif intent_name == "GetRestaurantInfo":
        return get_restaurant_info(intent)
    elif intent_name == "AMAZON.HelpIntent":
        return get_app_info()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print ('Ending session.')
    # Cleanup goes here...

def handle_session_end_request():
    card_title = "Yelp Delivery - Thanks"
    speech_output = "Thank you for using the Yelp Delivery skill.  See you next time!"
    should_end_session = True

    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def get_app_info():
    session_attributes = {}
    card_title = "About Yelp Delivery"
    reprompt_text = ""
    should_end_session = False

    speech_output = "This is the Alexa Skill to provide you with the local delivery options for Karl Brown! Try asking about McLean! This Skill uses the Yelp API. More cities to come!"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_restaurant_info(intent):
            session_attributes = {}
            card_title = "Yelp Restaurant Info"
            speech_output = "I'm not sure which Yelp Delivery area you want. " \
                            "Please try asking about McLean, for example."
            reprompt_text = "I'm not sure which Yelp Delivery area you want. " \
                            "Please try asking about McLean, for example."
            should_end_session = False

            if "Cities" in intent["slots"]:
                current_delivery_area = intent["slots"]["Cities"]["value"].lower()

                if (current_delivery_area in delivery_areas):
                    speech_output = returnFullAlexaDeliveryResponse(current_delivery_area)
                    reprompt_text = ""

            return build_response(session_attributes, build_speechlet_response(
                card_title, speech_output, reprompt_text, should_end_session))



def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }

def returnFullAlexaDeliveryResponse(current_delivery_area):
    if (current_delivery_area == 'mclean'):
        current_delivery_area = '830 Whann Ave, McLean, VA'
    if (current_delivery_area == 'dc'):
        current_delivery_area = '806 15th St. NW, Washington, DC'
    if (current_delivery_area == 'new york city'):
        current_delivery_area = '310 West 111th St, New York, New York'
    delivery_params = {'location': current_delivery_area,
                       'term': 'Delivery',
                       'sort_by': 'rating'
                       }
    delivery_json_response = requests.get(url=business_search_base_url, params=delivery_params, headers=oauth_yelp_headers)
    return formatResponseFromJson(delivery_json_response.json()['businesses'])

def formatResponseFromJson (contents):
    result = 'Here is a list of delivery restaurants in the area. '
    for restaurant in contents:
        if (restaurant['rating'] > 2):
            result += f"{restaurant['name']}. "
            result += "Categories. "
            for category in restaurant['categories']:
                result += f"{category['title']}. "
            result += f"Rating {restaurant['rating']}"
            result += '. '
    result += 'Thank you so much for listening'
    return result
