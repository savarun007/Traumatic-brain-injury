# # # import io
# # # import os
# # # import sys
# # # from fastapi import FastAPI, UploadFile, File
# # # from fastapi.middleware.cors import CORSMiddleware
# # # from PIL import Image
# # # import torch
# # # # from openrouter import OpenRouter
# # # from openrouter.client import OpenRouter
# # # from pydantic import BaseModel
# # # from dotenv import load_dotenv

# # # # Add the project root to the Python path
# # # sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# # # # Import model creation functions and transforms
# # # from backend.ml.models.hybrid_cnn import create_hybrid_cnn
# # # from backend.ml.models.vision_transformer import create_vision_transformer
# # # from backend.ml.models.high_accuracy_hybrid import create_high_accuracy_hybrid
# # # from backend.ml.utils.data_loader import val_test_transforms

# # # # --- App and Chatbot Client Setup ---
# # # app = FastAPI(title="TBI Prediction API")

# # # # Load environment variables (for API key)
# # # load_dotenv()

# # # # Initialize the OpenRouter client
# # # client = OpenRouter(
# # #   api_key=os.getenv("OPENROUTER_API_KEY"),
# # # )

# # # # Pydantic model for the request body of the summarise endpoint
# # # class SummariseRequest(BaseModel):
# # #     diagnosis: str

# # # # --- Middleware Setup ---
# # # # Allow requests from all origins (for development)
# # # app.add_middleware(
# # #     CORSMiddleware,
# # #     allow_origins=["*"],
# # #     allow_credentials=True,
# # #     allow_methods=["*"],
# # #     allow_headers=["*"],
# # # )

# # # # --- Model Loading ---
# # # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# # # CLASS_NAMES = ['any', 'epidural', 'intraparenchymal', 'intraventricular', 'subarachnoid', 'subdural']
# # # WEIGHTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'ml', 'weights')

# # # # Load all three models
# # # model_files = {
# # #     "hybrid_cnn": (create_hybrid_cnn, os.path.join(WEIGHTS_DIR, 'hybrid_cnn_model.pth')),
# # #     "vision_transformer": (create_vision_transformer, os.path.join(WEIGHTS_DIR, 'vision_transformer_model.pth')),
# # #     "high_accuracy_hybrid": (create_high_accuracy_hybrid, os.path.join(WEIGHTS_DIR, 'high_accuracy_hybrid_model.pth')),
# # # }

# # # models = {}
# # # for name, (create_fn, path) in model_files.items():
# # #     if not os.path.exists(path):
# # #         print(f"Warning: Weight file not found at {path}. The '{name}' model will not be loaded.")
# # #         continue
# # #     model = create_fn(num_classes=len(CLASS_NAMES), pretrained=False)
# # #     model.load_state_dict(torch.load(path, map_location=device))
# # #     model.to(device)
# # #     model.eval()
# # #     models[name] = model
# # #     print(f"'{name}' model loaded successfully.")

# # # # Placeholder for remedy points
# # # REMEDY_POINTS = {
# # #     "epidural": ["Immediate medical attention is crucial.", "Surgery may be required to relieve pressure.", "Medication to control swelling."],
# # #     "subdural": ["Monitoring for small hematomas.", "Surgical drainage for larger hematomas.", "Medication to manage symptoms."],
# # #     "subarachnoid": ["Hospitalization for observation.", "Procedures to stop bleeding (e.g., coiling).", "Medication to prevent vasospasm."],
# # #     "intraparenchymal": ["Medical management to control blood pressure.", "Surgery in some cases to remove the clot.", "Supportive care."],
# # #     "intraventricular": ["A shunt may be inserted to drain fluid.", "Monitoring intracranial pressure.", "Addressing the underlying cause."],
# # #     "any": ["General observation and supportive care.", "Pain management.", "Follow-up imaging as recommended by a doctor."],
# # # }

# # # # --- Helper Function for Predictions ---
# # # def predict_image(model, image: Image.Image):
# # #     """Transforms an image and gets a prediction from a model."""
# # #     image_tensor = val_test_transforms(image).unsqueeze(0).to(device)
# # #     with torch.no_grad():
# # #         outputs = model(image_tensor)
# # #         probabilities = torch.nn.functional.softmax(outputs, dim=1)
# # #         confidence, predicted_class_idx = torch.max(probabilities, 1)
        
# # #         predicted_class_name = CLASS_NAMES[predicted_class_idx.item()]
# # #         confidence_score = confidence.item()
        
# # #         return predicted_class_name, confidence_score

# # # # --- API Endpoints ---
# # # @app.get("/")
# # # def read_root():
# # #     return {"status": "TBI Prediction API is running."}

# # # @app.post("/predict/")
# # # async def create_upload_file(file: UploadFile = File(...)):
# # #     """
# # #     Accepts an image file and returns predictions from all loaded models.
# # #     """
# # #     if not models:
# # #         return {"error": "No models are loaded. Please train the models first."}
        
# # #     contents = await file.read()
# # #     image = Image.open(io.BytesIO(contents)).convert("RGB")
    
# # #     predictions = []
# # #     for name, model in models.items():
# # #         pred_class, confidence = predict_image(model, image)
# # #         predictions.append({
# # #             "model_name": name,
# # #             "prediction": pred_class,
# # #             "confidence": round(confidence * 100, 2),
# # #             "remedies": REMEDY_POINTS.get(pred_class, ["Consult a medical professional for advice."])
# # #         })
        
# # #     return {"results": predictions}

# # # @app.post("/summarise/")
# # # async def summarise_diagnosis(request: SummariseRequest):
# # #     """
# # #     Accepts a diagnosis and returns an AI-generated summary from OpenRouter.
# # #     """
# # #     try:
# # #         response = client.chat.completions.create(
# # #             model="meta-llama/llama-3-8b-instruct",
# # #             messages=[
# # #                 {
# # #                     "role": "system",
# # #                     "content": "You are an expert medical assistant. Your role is to explain a medical diagnosis in simple, easy-to-understand terms for a non-expert. Do not give medical advice. Focus on explaining what the diagnosis means in a clear and concise way. Start directly with the explanation.",
# # #                 },
# # #                 {
# # #                     "role": "user", 
# # #                     "content": f"Please explain what a '{request.diagnosis}' diagnosis means."
# # #                 },
# # #             ],
# # #         )
# # #         summary = response.choices[0].message.content
# # #         return {"summary": summary}
# # #     except Exception as e:
# # #         return {"error": f"Failed to get summary from AI model: {str(e)}"}
# # import io
# # import os
# # import sys
# # from fastapi import FastAPI, UploadFile, File
# # from fastapi.middleware.cors import CORSMiddleware
# # from PIL import Image
# # import torch
# # from openrouter import Client # CORRECTED IMPORT
# # from pydantic import BaseModel
# # from dotenv import load_dotenv

# # # Add the project root to the Python path
# # sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# # # Import model creation functions and transforms
# # from backend.ml.models.hybrid_cnn import create_hybrid_cnn
# # from backend.ml.models.vision_transformer import create_vision_transformer
# # from backend.ml.models.high_accuracy_hybrid import create_high_accuracy_hybrid
# # from backend.ml.utils.data_loader import val_test_transforms

# # # --- App and Chatbot Client Setup ---
# # app = FastAPI(title="TBI Prediction API")

# # # Load environment variables (for API key)
# # load_dotenv()

# # # Initialize the OpenRouter client with the correct class name
# # client = Client( # CORRECTED CLASS NAME
# #   api_key=os.getenv("OPENROUTER_API_KEY"),
# # )

# # # Pydantic model for the request body of the summarise endpoint
# # class SummariseRequest(BaseModel):
# #     diagnosis: str

# # # --- Middleware Setup ---
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )

# # # --- Model Loading ---
# # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# # CLASS_NAMES = ['any', 'epidural', 'intraparenchymal', 'intraventricular', 'subarachnoid', 'subdural']
# # WEIGHTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'ml', 'weights')

# # model_files = {
# #     "hybrid_cnn": (create_hybrid_cnn, os.path.join(WEIGHTS_DIR, 'hybrid_cnn_model.pth')),
# #     "vision_transformer": (create_vision_transformer, os.path.join(WEIGHTS_DIR, 'vision_transformer_model.pth')),
# #     "high_accuracy_hybrid": (create_high_accuracy_hybrid, os.path.join(WEIGHTS_DIR, 'high_accuracy_hybrid_model.pth')),
# # }

# # models = {}
# # for name, (create_fn, path) in model_files.items():
# #     if not os.path.exists(path):
# #         print(f"Warning: Weight file not found at {path}. The '{name}' model will not be loaded.")
# #         continue
# #     model = create_fn(num_classes=len(CLASS_NAMES), pretrained=False)
# #     model.load_state_dict(torch.load(path, map_location=device))
# #     model.to(device)
# #     model.eval()
# #     models[name] = model
# #     print(f"'{name}' model loaded successfully.")

# # # Placeholder for remedy points
# # REMEDY_POINTS = {
# #     "epidural": ["Immediate medical attention is crucial.", "Surgery may be required to relieve pressure.", "Medication to control swelling."],
# #     "subdural": ["Monitoring for small hematomas.", "Surgical drainage for larger hematomas.", "Medication to manage symptoms."],
# #     "subarachnoid": ["Hospitalization for observation.", "Procedures to stop bleeding (e.g., coiling).", "Medication to prevent vasospasm."],
# #     "intraparenchymal": ["Medical management to control blood pressure.", "Surgery in some cases to remove the clot.", "Supportive care."],
# #     "intraventricular": ["A shunt may be inserted to drain fluid.", "Monitoring intracranial pressure.", "Addressing the underlying cause."],
# #     "any": ["General observation and supportive care.", "Pain management.", "Follow-up imaging as recommended by a doctor."],
# # }

# # # --- Helper Function for Predictions ---
# # def predict_image(model, image: Image.Image):
# #     image_tensor = val_test_transforms(image).unsqueeze(0).to(device)
# #     with torch.no_grad():
# #         outputs = model(image_tensor)
# #         probabilities = torch.nn.functional.softmax(outputs, dim=1)
# #         confidence, predicted_class_idx = torch.max(probabilities, 1)
        
# #         predicted_class_name = CLASS_NAMES[predicted_class_idx.item()]
# #         confidence_score = confidence.item()
        
# #         return predicted_class_name, confidence_score

# # # --- API Endpoints ---
# # @app.get("/")
# # def read_root():
# #     return {"status": "TBI Prediction API is running."}

# # @app.post("/predict/")
# # async def create_upload_file(file: UploadFile = File(...)):
# #     if not models:
# #         return {"error": "No models are loaded. Please train the models first."}
        
# #     contents = await file.read()
# #     image = Image.open(io.BytesIO(contents)).convert("RGB")
    
# #     predictions = []
# #     for name, model in models.items():
# #         pred_class, confidence = predict_image(model, image)
# #         predictions.append({
# #             "model_name": name,
# #             "prediction": pred_class,
# #             "confidence": round(confidence * 100, 2),
# #             "remedies": REMEDY_POINTS.get(pred_class, ["Consult a medical professional for advice."])
# #         })
        
# #     return {"results": predictions}

# # @app.post("/summarise/")
# # async def summarise_diagnosis(request: SummariseRequest):
# #     try:
# #         response = client.chat.completions.create(
# #             model="meta-llama/llama-3-8b-instruct",
# #             messages=[
# #                 {
# #                     "role": "system",
# #                     "content": "You are an expert medical assistant. Your role is to explain a medical diagnosis in simple, easy-to-understand terms for a non-expert. Do not give medical advice. Focus on explaining what the diagnosis means in a clear and concise way. Start directly with the explanation.",
# #                 },
# #                 {
# #                     "role": "user", 
# #                     "content": f"Please explain what a '{request.diagnosis}' diagnosis means."
# #                 },
# #             ],
# #         )
# #         summary = response.choices[0].message.content
# #         return {"summary": summary}
# #     except Exception as e:
# #         return {"error": f"Failed to get summary from AI model: {str(e)}"}
# import io
# import os
# import sys
# from fastapi import FastAPI, UploadFile, File
# from fastapi.middleware.cors import CORSMiddleware
# from PIL import Image
# import torch
# import openrouter      # MODIFIED IMPORT
# from pydantic import BaseModel
# from dotenv import load_dotenv

# # Add the project root to the Python path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# # Import model creation functions and transforms
# from backend.ml.models.hybrid_cnn import create_hybrid_cnn
# from backend.ml.models.vision_transformer import create_vision_transformer
# from backend.ml.models.high_accuracy_hybrid import create_high_accuracy_hybrid
# from backend.ml.utils.data_loader import val_test_transforms

# # --- App and Chatbot Client Setup ---
# app = FastAPI(title="TBI Prediction API")

# # Load environment variables (for API key)
# load_dotenv()

# # Initialize the OpenRouter client with the correct class name
# client = openrouter.Client( # MODIFIED INSTANTIATION
#   api_key=os.getenv("OPENROUTER_API_KEY"),
# )

# # Pydantic model for the request body of the summarise endpoint
# class SummariseRequest(BaseModel):
#     diagnosis: str

# # --- Middleware Setup ---
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # --- Model Loading ---
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# CLASS_NAMES = ['any', 'epidural', 'intraparenchymal', 'intraventricular', 'subarachnoid', 'subdural']
# WEIGHTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'ml', 'weights')

# model_files = {
#     "hybrid_cnn": (create_hybrid_cnn, os.path.join(WEIGHTS_DIR, 'hybrid_cnn_model.pth')),
#     "vision_transformer": (create_vision_transformer, os.path.join(WEIGHTS_DIR, 'vision_transformer_model.pth')),
#     "high_accuracy_hybrid": (create_high_accuracy_hybrid, os.path.join(WEIGHTS_DIR, 'high_accuracy_hybrid_model.pth')),
# }

# models = {}
# for name, (create_fn, path) in model_files.items():
#     if not os.path.exists(path):
#         print(f"Warning: Weight file not found at {path}. The '{name}' model will not be loaded.")
#         continue
#     model = create_fn(num_classes=len(CLASS_NAMES), pretrained=False)
#     model.load_state_dict(torch.load(path, map_location=device))
#     model.to(device)
#     model.eval()
#     models[name] = model
#     print(f"'{name}' model loaded successfully.")

# # Placeholder for remedy points
# REMEDY_POINTS = {
#     "epidural": ["Immediate medical attention is crucial.", "Surgery may be required to relieve pressure.", "Medication to control swelling."],
#     "subdural": ["Monitoring for small hematomas.", "Surgical drainage for larger hematomas.", "Medication to manage symptoms."],
#     "subarachnoid": ["Hospitalization for observation.", "Procedures to stop bleeding (e.g., coiling).", "Medication to prevent vasospasm."],
#     "intraparenchymal": ["Medical management to control blood pressure.", "Surgery in some cases to remove the clot.", "Supportive care."],
#     "intraventricular": ["A shunt may be inserted to drain fluid.", "Monitoring intracranial pressure.", "Addressing the underlying cause."],
#     "any": ["General observation and supportive care.", "Pain management.", "Follow-up imaging as recommended by a doctor."],
# }

# # --- Helper Function for Predictions ---
# def predict_image(model, image: Image.Image):
#     image_tensor = val_test_transforms(image).unsqueeze(0).to(device)
#     with torch.no_grad():
#         outputs = model(image_tensor)
#         probabilities = torch.nn.functional.softmax(outputs, dim=1)
#         confidence, predicted_class_idx = torch.max(probabilities, 1)
        
#         predicted_class_name = CLASS_NAMES[predicted_class_idx.item()]
#         confidence_score = confidence.item()
        
#         return predicted_class_name, confidence_score

# # --- API Endpoints ---
# @app.get("/")
# def read_root():
#     return {"status": "TBI Prediction API is running."}

# @app.post("/predict/")
# async def create_upload_file(file: UploadFile = File(...)):
#     if not models:
#         return {"error": "No models are loaded. Please train the models first."}
        
#     contents = await file.read()
#     image = Image.open(io.BytesIO(contents)).convert("RGB")
    
#     predictions = []
#     for name, model in models.items():
#         pred_class, confidence = predict_image(model, image)
#         predictions.append({
#             "model_name": name,
#             "prediction": pred_class,
#             "confidence": round(confidence * 100, 2),
#             "remedies": REMEDY_POINTS.get(pred_class, ["Consult a medical professional for advice."])
#         })
        
#     return {"results": predictions}

# @app.post("/summarise/")
# async def summarise_diagnosis(request: SummariseRequest):
#     try:
#         response = client.chat.completions.create(
#             model="meta-llama/llama-3-8b-instruct",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": "You are an expert medical assistant. Your role is to explain a medical diagnosis in simple, easy-to-understand terms for a non-expert. Do not give medical advice. Focus on explaining what the diagnosis means in a clear and concise way. Start directly with the explanation.",
#                 },
#                 {
#                     "role": "user", 
#                     "content": f"Please explain what a '{request.diagnosis}' diagnosis means."
#                 },
#             ],
#         )
#         summary = response.choices[0].message.content
#         return {"summary": summary}
#     except Exception as e:
#         return {"error": f"Failed to get summary from AI model: {str(e)}"}
import io
import os
import sys
from fastapi import FastAPI, UploadFile, File, HTTPException # Added HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import torch
import httpx # ADDED THIS
from pydantic import BaseModel
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import model creation functions and transforms
from backend.ml.models.hybrid_cnn import create_hybrid_cnn
from backend.ml.models.vision_transformer import create_vision_transformer
from backend.ml.models.high_accuracy_hybrid import create_high_accuracy_hybrid
from backend.ml.utils.data_loader import val_test_transforms

# --- App Setup ---
app = FastAPI(title="TBI Prediction API")

# Load environment variables (for API key)
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") # Use os.getenv

# Pydantic model for the request body of the summarise endpoint
class SummariseRequest(BaseModel):
    diagnosis: str

# --- Middleware Setup ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Model Loading ---
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
CLASS_NAMES = ['any', 'epidural', 'intraparenchymal', 'intraventricular', 'subarachnoid', 'subdural']
WEIGHTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'ml', 'weights')

model_files = {
    "hybrid_cnn": (create_hybrid_cnn, os.path.join(WEIGHTS_DIR, 'hybrid_cnn_model.pth')),
    "vision_transformer": (create_vision_transformer, os.path.join(WEIGHTS_DIR, 'vision_transformer_model.pth')),
    "high_accuracy_hybrid": (create_high_accuracy_hybrid, os.path.join(WEIGHTS_DIR, 'high_accuracy_hybrid_model.pth')),
}

models = {}
for name, (create_fn, path) in model_files.items():
    if not os.path.exists(path):
        print(f"Warning: Weight file not found at {path}. The '{name}' model will not be loaded.")
        continue
    model = create_fn(num_classes=len(CLASS_NAMES), pretrained=False)
    model.load_state_dict(torch.load(path, map_location=device))
    model.to(device)
    model.eval()
    models[name] = model
    print(f"'{name}' model loaded successfully.")

# Placeholder for remedy points
# REMEDY_POINTS = {
#     "epidural": ["Immediate medical attention is crucial.", "Surgery may be required to relieve pressure.", "Medication to control swelling."],
#     "subdural": ["Monitoring for small hematomas.", "Surgical drainage for larger hematomas.", "Medication to manage symptoms."],
#     "subarachnoid": ["Hospitalization for observation.", "Procedures to stop bleeding (e.g., coiling).", "Medication to prevent vasospasm."],
#     "intraparenchymal": ["Medical management to control blood pressure.", "Surgery in some cases to remove the clot.", "Supportive care."],
#     "intraventricular": ["A shunt may be inserted to drain fluid.", "Monitoring intracranial pressure.", "Addressing the underlying cause."],
#     "any": ["General observation and supportive care.", "Pain management.", "Follow-up imaging as recommended by a doctor."],
# }
TBI_INFO = {
    "epidural": {
        "description": "A bleeding event that occurs between the skull and the dura mater (the brain's outer protective layer).",
        "cause": "Typically caused by a skull fracture that tears an underlying artery.",
        "treatment": "This is often a medical emergency requiring immediate surgery to drain the hematoma and relieve pressure on the brain."
    },
    "subdural": {
        "description": "A crescent-shaped collection of blood that forms beneath the dura mater.",
        "cause": "Results from the tearing of veins that cross the subdural space, often due to a head injury.",
        "treatment": "Small hematomas may be monitored, while larger ones require surgical drainage to reduce pressure."
    },
    "subarachnoid": {
        "description": "Bleeding into the space between the brain and the tissues that cover it (the subarachnoid space).",
        "cause": "Can be caused by trauma or a ruptured cerebral aneurysm.",
        "treatment": "Treatment focuses on stabilizing the patient, controlling blood pressure, and performing procedures like coiling or clipping to repair the source of bleeding."
    },
    "intraparenchymal": {
        "description": "Bleeding that occurs directly within the brain tissue (parenchyma) itself.",
        "cause": "Often caused by uncontrolled high blood pressure, trauma, or vascular malformations.",
        "treatment": "Medical management to control blood pressure and swelling. Surgery may be required in some cases to remove the clot."
    },
    "intraventricular": {
        "description": "Bleeding into the brain’s ventricular system, where cerebrospinal fluid is produced and circulates.",
        "cause": "Can result from trauma or as an extension from a nearby intraparenchymal hemorrhage.",
        "treatment": "A shunt may be inserted to drain excess fluid and blood. Focus is on monitoring intracranial pressure and treating the underlying cause."
    },
    "any": {
        "description": "This category indicates that a form of hemorrhage is visible on the CT scan.",
        "cause": "The specific cause depends on the underlying hemorrhage type detected.",
        "treatment": "General observation, supportive care, pain management, and follow-up imaging are typically recommended to determine the specific nature of the injury."
    },
}

# Also, update the loop inside the /predict endpoint to use the new dictionary.
# Find this line in the /predict endpoint:
# "remedies": REMEDY_POINTS.get(pred_class, ["Consult a medical professional for advice."])
# And replace it with this:
# "info": TBI_INFO.get(pred_class)
# --- Helper Function for Predictions ---
def predict_image(model, image: Image.Image):
    image_tensor = val_test_transforms(image).unsqueeze(0).to(device)
    with torch.no_grad():
        outputs = model(image_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        confidence, predicted_class_idx = torch.max(probabilities, 1)
        
        predicted_class_name = CLASS_NAMES[predicted_class_idx.item()]
        confidence_score = confidence.item()
        
        return predicted_class_name, confidence_score

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"status": "TBI Prediction API is running."}

@app.post("/predict/")
async def create_upload_file(file: UploadFile = File(...)):
    if not models:
        return {"error": "No models are loaded. Please train the models first."}
        
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    
    predictions = []
    for name, model in models.items():
        pred_class, confidence = predict_image(model, image)
        predictions.append({
            "model_name": name,
            "prediction": pred_class,
            "confidence": round(confidence * 100, 2),
            "info": TBI_INFO.get(pred_class) # This line is updated
        })
        
    return {"results": predictions}

@app.post("/summarise/")
async def summarise_diagnosis(request: SummariseRequest):
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY is not set.")

    # ... inside the /summarise endpoint ...
    messages=[
    {
        "role": "system",
        "content": "You are an expert medical assistant specializing ONLY in Traumatic Brain Injury (TBI). Your role is to explain TBI-related diagnoses and topics in simple terms for a non-expert. Do not give medical advice. If the user asks about anything other than TBI (like other medical conditions or general topics), you MUST politely decline and state that your expertise is limited to Traumatic Brain Injury.",
    },
    {
        "role": "user", 
        "content": f"Please explain what a '{request.diagnosis}' diagnosis means."
    },
]
# ...

    payload = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": messages,
    }
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers, timeout=30.0)
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
            
            summary = response.json()['choices'][0]['message']['content']
            return {"summary": summary}
            
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Error from OpenRouter API: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
        