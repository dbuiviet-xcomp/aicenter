from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
# from core import run_mistral_instruct
from core import model_sapbert,model_clinicalbert, model_labse
import time
router = APIRouter()

def is_valid_api_key(api_key: str) -> bool:
    valid_key = "civ-26787654356gjhgjd87ey87hihihi"
    return api_key == valid_key

class AskRequest_Type1(BaseModel):
    api_key: str
    service: str
    question: str

class AskResponse_Type1(BaseModel):
    answer: str
    result: str = "Ok"

@router.post("/api/nlp_api_type1", response_model=AskResponse_Type1)
async def api_ask(payload: AskRequest_Type1, request: Request):
    start_total = time.time()
    try:
        api_key = payload.api_key.strip()
        service = payload.service.strip()
        question = payload.question.strip()

        if not is_valid_api_key(api_key):
            return AskResponse_Type1(answer="", result="Key invalid")

        if service == "mistral":
            answer ="Not supported!"
            # answer = run_mistral_instruct(question, 512, 0.7)
        else:
            total_time = round(time.time() - start_total, 3)
            print(f"Processed in {total_time}s for question: {service} Service Invalid!  {question}")
            return AskResponse_Type1(answer="", result=f"Service '{service}' không được hỗ trợ.")

        total_time = round(time.time() - start_total, 3)
        print(f"Processed in {total_time}s for question: {service} : {question} \n\n {answer}")

        return AskResponse_Type1(answer=answer, result="Ok")

    except Exception as e:
        return AskResponse_Type1(answer="", result=f"Error: {str(e)}")


class AskRequest_Type2(BaseModel):
    api_key: str
    service: str
    question: str

class AskResponse_Type2(BaseModel):
    embedding: list[float] = []
    result: str = "Ok"

@router.post("/api/nlp_api_type2", response_model=AskResponse_Type2)
async def api_encode_question(payload: AskRequest_Type2, request: Request):
    start_total = time.time()
    try:
        api_key = payload.api_key.strip()
        service = payload.service.strip()
        question = payload.question.strip()

        if not is_valid_api_key(api_key):
            return AskResponse_Type2(embedding=[], result="Key invalid")

        if service == "sapbert":
            embedding = model_sapbert.encode([question])[0].tolist()
        elif service == "clinicalbert":
            embedding = model_clinicalbert.encode([question])[0].tolist()
        elif service == "labse":
            embedding = model_labse.encode([question])[0].tolist()
        else:
            total_time = round(time.time() - start_total, 3)
            print(f"Processed in {total_time}s for question: {service} Service Invalid!  {question}")

            return AskResponse_Type2(embedding=[], result=f"Service '{service}' không được hỗ trợ.")

        total_time = round(time.time() - start_total, 3)
        print(f"Processed in {total_time}s for question: {service} : {question}")

        return AskResponse_Type2(embedding=embedding, result="Ok")

    except Exception as e:
        return AskResponse_Type2(embedding=[], result=f"Error: {str(e)}")
