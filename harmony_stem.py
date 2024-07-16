import base64, json

instrument_serialised_as_json = json.dumps({
    "instrument_name": "Smoking behaviour",
    "questions": [
        {
            "question_no": "1",
            "question_text": "Do you currently smoke or have you ever smoked?"
        },
        {
            "question_no": "2",
            "question_text": "[Do you currently use] nicotine replacement therapy?"
        }
    ]
})
instrument_json_b64_encoded_bytes = base64.urlsafe_b64encode(instrument_serialised_as_json.encode('utf-8'))
instrument_json_b64_encoded_str = instrument_json_b64_encoded_bytes.decode("utf-8")

url = f"https://harmonydata.ac.uk/app/#/import/{instrument_json_b64_encoded_str}"
print ("DEBUG Harmony setup:\n", url)
