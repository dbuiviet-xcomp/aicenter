from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
# from core import run_mistral_instruct
import time
import base64
import json
from datetime import datetime

from vietvoicetts import synthesize_to_bytes

router = APIRouter()

def convert_bytes_base64(text_bytes):
    base64_bytes = base64.b64encode(text_bytes)
    base64_string = base64_bytes.decode('utf-8')

    json_payload = {
        'fileName': 'audio.wav',
        'encoding': 'base64',
        'audioContent': base64_string
    }
    json_message = json.dumps(json_payload, indent=2)

    # print(json_message)
    return json_message

# text_bytes_tuple = synthesize_to_bytes(text="Xin chào anh Minh", gender="male", area="northern", emotion="neutral")
# text_bytes = text_bytes_tuple[0]
# convert_bytes_base64(text_bytes)

def is_valid_api_key(api_key: str) -> bool:
    valid_key = "civ-26787654356gjhgjd87ey87hihihi"
    return api_key == valid_key


class AskRequest_TTS_Type1(BaseModel):
    api_key: str
    service: str
    gender: str = "female"
    area: str = "southern"
    emotion: str = "neutral"
    lang: str = "vi"
    text: str

class AskResponse_TTS_Type1(BaseModel):
    text_audio: str
    result: str = "Ok" # status.HTTP_200_CODE

@router.post("/api/tts_api_type1", response_model= AskResponse_TTS_Type1)
async def api_ask(payload: AskRequest_TTS_Type1, request: Request):
    start_total = time.time()

    print ("api_ask called")

    try:
        api_key = payload.api_key.strip()
        service = payload.service.strip()
        gender = payload.gender.strip()
        area = payload.area.strip()
        emotion = payload.emotion.strip()
        text = payload.text.strip()

        if not is_valid_api_key(api_key):
            return AskResponse_TTS_Type1(text_audio="", result="API Key invalid")

        text_bytes_tuple = synthesize_to_bytes(text=text, gender=gender, area=area, emotion=emotion)
        text_bytes = text_bytes_tuple[0]
        answer = convert_bytes_base64(text_bytes)

        total_time = round(time.time() - start_total, 3)

        return AskResponse_TTS_Type1(text_audio=answer, result="Ok")

    except Exception as e:
        return AskResponse_TTS_Type1(text_audio="", result=f"Error: {str(e)}")