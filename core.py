from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
from fastapi.templating import Jinja2Templates

MONGODB_URI = "mongodb://appuser:%40Abcd%4012345%40@171.244.129.23:27017/center_db?authSource=center_db"
DB_NAME = "center_db"

mongo_client = MongoClient(MONGODB_URI)
db = mongo_client[DB_NAME]

templates = Jinja2Templates(directory="templates")

# Khởi tạo model 1 lần duy nhất
model_sapbert = SentenceTransformer("cambridgeltl/SapBERT-from-PubMedBERT-fulltext")

model_clinicalbert = SentenceTransformer("emilyalsentzer/Bio_ClinicalBERT")

# facebook_model = SentenceTransformer("FacebookAI/xlm-roberta-large")

from transformers import AutoTokenizer
model_labse_tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/LaBSE")
model_labse = SentenceTransformer("sentence-transformers/LaBSE")



# vibert_tokenizer = AutoTokenizer.from_pretrained("google-bert/bert-base-multilingual-cased")
# vibert_model = SentenceTransformer("google-bert/bert-base-multilingual-cased")



#Decoder-------- core.py
# from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
# import torch
#
# # print(torch.cuda.is_available())
# # print(torch.cuda.current_device())
# # print(torch.cuda.get_device_name(torch.cuda.current_device()) if torch.cuda.is_available() else "No GPU detected")
#
# MISTRAL_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"
# mistral_pipeline = None
#
# def load_mistral_pipeline():
#     global mistral_pipeline
#     if mistral_pipeline is None:
#         try:
#             tokenizer = AutoTokenizer.from_pretrained(MISTRAL_MODEL)
#             model = AutoModelForCausalLM.from_pretrained(
#                 MISTRAL_MODEL,
#                 # torch_dtype="auto",
#                 # device_map="auto",
#
#                 torch_dtype=torch.float16,
#                 device_map="auto",
#             )
#             mistral_pipeline = pipeline(
#                 "text-generation",
#                 model=model,
#                 tokenizer=tokenizer,
#                 max_new_tokens=512,
#                 do_sample=True,
#                 temperature=0.7,
#             )
#             print("Mistral pipeline loaded")
#         except Exception as e:
#             print(f"Could not load Mistral-7B-Instruct-v0.3: {e}")
#             mistral_pipeline = None
#
# # Khởi tạo pipeline duy nhất khi core.py được import
# load_mistral_pipeline()
#
# def run_mistral_instruct(prompt, max_new_tokens=256, temperature=0.7):
#     if mistral_pipeline is None:
#         return "Mistral model not available."
#     output = mistral_pipeline(
#         prompt,
#         max_new_tokens=max_new_tokens,
#         temperature=temperature,
#         return_full_text=False
#     )
#     return output[0]['generated_text'] if output and 'generated_text' in output[0] else ""