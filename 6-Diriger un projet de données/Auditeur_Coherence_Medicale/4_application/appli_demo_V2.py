import pandas as pd
import torch
import streamlit as st
from pathlib import Path
import math
from PIL import Image
from health_multimodal.image.inference_engine import ImageInferenceEngine
from health_multimodal.image.model.pretrained import get_biovil_t_image_encoder
from health_multimodal.image.data.transforms import create_chest_xray_transform_for_inference
from transformers import AutoTokenizer, AutoModel
import os
import io

# 1. Configuration de la page
st.set_page_config(page_title="MIROIR", layout="wide")
st.markdown("### 🩺 MIROIR : Modèle d'Intelligence pour le Rapprochement d'Observations, d'Images et de Rapports")

# Configuration du chemin MLflow
BASE_DIR = Path(__file__).resolve().parent
LOCAL_WEIGHTS_PATH = os.path.join(BASE_DIR, "mon_modele", "data", "model.pt2")

IS_HUGGINGFACE = "SPACE_ID" in os.environ

if IS_HUGGINGFACE:
    CSV_NAME = "chexpert_matches_sample_demo.csv"
    IMAGE_PREFIX = "" 
else:
    CSV_NAME = "chexpert_matches_sample.csv"
    IMAGE_PREFIX = "CheXpert/CheXpert-v1.0-small/"


class SafeMLflowUnpickler(torch.serialization.pickle.Unpickler):
    def find_class(self, module, name):
        if "cloudpickle" in module or "_make_skeleton_class" in name:
            return object
        try:
            return super().find_class(module, name)
        except Exception:
            return object

def custom_safe_load(filepath, device):
    """Lit le fichier MLmodel de manière brute sans exécuter le code obsolète"""
    with open(filepath, 'rb') as f:
        return torch.load(f, map_location=device, weights_only=False, pickle_module=torch.serialization.pickle)

@st.cache_resource
def load_models():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # 1. Encodeur d'images
    image_encoder = get_biovil_t_image_encoder()
    transform = create_chest_xray_transform_for_inference(resize=512, center_crop_size=448)
    image_inference_engine = ImageInferenceEngine(image_encoder, transform)

    # 2. Tokenizer
    tokenizer = AutoTokenizer.from_pretrained("microsoft/BiomedVLP-BioViL-T", trust_remote_code=True)
    
    # 3. Architecture du Modèle Textuel
    try:
        new_text_model = AutoModel.from_pretrained("microsoft/BiomedVLP-BioViL-T", trust_remote_code=True)
    except Exception as e:
        st.error(f"Impossible d'initialiser l'architecture : {e}")
        new_text_model = None


    if new_text_model is not None and os.path.exists(LOCAL_WEIGHTS_PATH):
        try:
            state_dict = torch.load(LOCAL_WEIGHTS_PATH, map_location=device, weights_only=False)
            
            if isinstance(state_dict, dict):
                # Extraction si c'est encapsulé
                if "state_dict" in state_dict:
                    state_dict = state_dict["state_dict"]
                
                cleaned_state_dict = {}
                for k, v in state_dict.items():
                    name = k.replace("model.", "").replace("text_model.", "")
                    if isinstance(v, torch.Tensor):
                        cleaned_state_dict[name] = v
                
                new_text_model.load_state_dict(cleaned_state_dict, strict=False)
            else:
                st.warning("⚠️ Les poids du fichier MLflow étaient corrompus par la version de Python. Exécution sur l'architecture BioViL-T de base.")
                
        except Exception as e:
            st.error(f"Erreur d'application des poids : {e}")            


    if new_text_model is not None and hasattr(new_text_model, "eval"):
        new_text_model.eval()
            
    return image_inference_engine, tokenizer, new_text_model, device



# Chargement du dataset principal
#@st.cache_data
#def load_dataset():
#    try:
#        return pd.read_csv("./chexpert_matches_sample.csv", index_col=0)
#    except Exception:
#        return None
 

@st.cache_data
def load_dataset():
    csv_path = BASE_DIR / CSV_NAME
    try:
        return pd.read_csv(csv_path, index_col=0)
    except Exception as e:
        st.error(f"Fichier `{CSV_NAME}` introuvable à l'emplacement {csv_path} : {e}")
        return None    


# Initialisation des composants
image_engine, tokenizer, new_text_model, device = load_models()
df_matches = load_dataset()

# Fonction de calcul de similarité
def compute_similarity(image_path, text_content):
    local_device = "cuda" if torch.cuda.is_available() else "cpu"
    
    if new_text_model is None:
        st.error("Le modèle de cross-attention n'est pas chargé.")
        return 0.0
    
    try:
        path_object = Path(image_path)
        
        # Extraction de l'embedding d'image
        with torch.no_grad():
            image_embedding = image_engine.get_projected_global_embedding(path_object)
            if not isinstance(image_embedding, torch.Tensor):
                image_embedding = torch.tensor(image_embedding).to(local_device)
            else:
                image_embedding = image_embedding.to(local_device)
                
            if image_embedding.ndim == 1:
                image_embedding = image_embedding.unsqueeze(0)
            image_embedding = image_embedding / image_embedding.norm(dim=-1, keepdim=True)

        # Tokenisation du rapport textuel
        inputs = tokenizer(text_content, return_tensors="pt", padding="max_length", truncation=True, max_length=512).to(local_device)
        
        # Inférence via ton modèle personnalisé
        with torch.no_grad():
            if hasattr(new_text_model, "get_projected_text_embeddings"):
                text_embedding = new_text_model.get_projected_text_embeddings(
                    input_ids=inputs["input_ids"],
                    attention_mask=inputs["attention_mask"]
                )
            else:
                outputs = new_text_model(input_ids=inputs["input_ids"], attention_mask=inputs["attention_mask"])
                text_embedding = outputs.pooler_output if hasattr(outputs, "pooler_output") else outputs[0][:, 0, :]
            
            if text_embedding.ndim == 1:
                text_embedding = text_embedding.unsqueeze(0)
            text_embedding = text_embedding / text_embedding.norm(dim=-1, keepdim=True)

        # Calcul du score
        similarity = torch.mm(image_embedding, text_embedding.t()).item()
        similarity_prob = 1 / (1 + math.exp(-similarity * 4))
        return similarity_prob

    except Exception as e:
        st.error(f"Erreur lors de l'exécution du modèle : {e}")
        return 0.0

# --- RECHERCHE ET SELECTION DE DONNÉES ---
if "current_pair" not in st.session_state:
    st.session_state.current_pair = None
if "last_loaded_patient" not in st.session_state:
    st.session_state.last_loaded_patient = None
if "reset_counter" not in st.session_state:
    st.session_state.reset_counter = 0

col_action1, col_action2 = st.columns([1, 1])

with col_action1:
    st.markdown("##### 🎲 Option 1 : Génération aléatoire")
    if st.button("✅ Générer une paire CORRECTE (Match)", use_container_width=True):
        if df_matches is not None:
            st.session_state.current_pair = df_matches.sample(1).iloc[0]
            st.session_state.last_loaded_patient = "random"
            st.session_state.reset_counter += 1
            
            if "patient_input_key" in st.session_state:
                st.session_state.patient_input_key = ""
                
            st.rerun()
        else:
            st.error("Fichier `chexpert_matches_sample.csv` introuvable.")

with col_action2:
    st.markdown("##### 🔍 Option 2 : Recherche par Patient")
    
    col_saisie, col_bouton = st.columns([0.7, 0.3])
    
    with col_saisie:
        patient_id = st.text_input(
            "Saisir l'ID du Patient (ex: patient64541) :", 
            placeholder="patientXXXXX",
            key="patient_input_key",
            label_visibility="collapsed" # Masque le label pour un alignement parfait avec le bouton
        )
    
    with col_bouton:
        bouton_reset = st.button("🔄 Réinitialiser", use_container_width=True)
    
    if bouton_reset:
        st.session_state.reset_counter += 1
        st.session_state.last_loaded_patient = None # Force le rechargement des widgets du bas
        st.rerun()
        
    if patient_id and df_matches is not None:
        patient_records = df_matches[df_matches['path_to_image'].str.contains(patient_id, na=False, case=False)]
        
        if not patient_records.empty:
            if len(patient_records) > 1:
                st.success(f"🎵 {len(patient_records)} observation(s) trouvée(s) pour le `{patient_id}`.")
                choices = [f"Observation {i+1} - Image: {Path(row['path_to_image']).name}" for i, row in patient_records.iterrows()]
                
                selected_index = st.selectbox(
                    "Sélectionnez l'examen à analyser :", 
                    range(len(choices)), 
                    format_func=lambda x: choices[x],
                    key=f"select_{patient_id}"
                )
                
                nouvelle_paire = patient_records.iloc[selected_index]
                identifiant_unique = f"{patient_id}_{selected_index}"
                
                if st.session_state.last_loaded_patient != identifiant_unique:
                    st.session_state.current_pair = nouvelle_paire
                    st.session_state.last_loaded_patient = identifiant_unique
                    st.rerun()
            else:
                if st.session_state.last_loaded_patient != patient_id:
                    st.session_state.current_pair = patient_records.iloc[0]
                    st.session_state.last_loaded_patient = patient_id
                    st.rerun() 
        else:
            st.warning(f"Aucun enregistrement trouvé pour l'ID `{patient_id}`.")


if st.session_state.current_pair is not None:
    pair = st.session_state.current_pair
    col1, col2 = st.columns([0.6, 1.4])    
    
    v_id = st.session_state.reset_counter
    vient_de_la_recherche = "patient_input_key" in st.session_state and st.session_state.patient_input_key != ""
    
    with col1:
        st.markdown("#### 🖼️ Radiographie Thoracique :")
        
        cle_dynamique_radio = f"radio_{pair['path_to_image']}_v{v_id}"
        
        img_source = st.radio(  
            "Source de l'image :", 
            ["Image de la paire sélectionnée", "Uploader une autre image"],
            key=cle_dynamique_radio
        )



        image_to_process = None
        if img_source == "Image de la paire sélectionnée":
            raw_path = str(pair["path_to_image"])
            clean_path = raw_path.replace("\\", "/")
            image_path = IMAGE_PREFIX + clean_path
            if "CheXpert-v1.0-small/CheXpert-v1.0-small" in image_path:
                image_path = image_path.replace("CheXpert/CheXpert-v1.0-small/CheXpert-v1.0-small", "CheXpert/CheXpert-v1.0-small")
            
            st.caption(f"`{image_path}`")    
            
            try:
                image_to_process = image_path
                img_display = Image.open(image_path)
                st.image(img_display, width=250)
            except FileNotFoundError:
                st.warning("⚠️ Image absente de l'arborescence. Bascule automatique sur l'upload.")
                img_source = "Uploader une autre image"
                image_to_process = None



                
        if img_source == "Uploader une autre image":
            cle_dynamique_upload = f"upload_{pair['path_to_image']}_v{v_id}"
            
            uploaded_file = st.file_uploader(
                "Choisissez une radiographie (JPG/PNG)", 
                type=["jpg", "jpeg", "png"],
                key=cle_dynamique_upload
            )
            
            if uploaded_file is not None:
                img_display = Image.open(uploaded_file)
                st.image(img_display, width=250)
                image_to_process = "temp_uploaded_img.jpg"
                img_display.convert("RGB").save(image_to_process)

    with col2:
        st.markdown("#### 📝 Compte Rendu (Analyse Cross-Attention) :")
        default_text = pair["section_impression"] if pd.notna(pair["section_impression"]) else pair.get("report", "")
        
        edited_text = st.text_area(
            "Texte éditable :", 
            value=str(default_text), 
            height=300, 
            key=f"text_area_{pair['path_to_image']}_v{v_id}"
        )
        
        if image_to_process is not None and edited_text:
            with st.spinner("Analyse de la cohérence..."):
                score = compute_similarity(image_to_process, edited_text)
            
            st.markdown("#### 📊 Résultat de l'analyse :")
            
            SEUIL = 0.50
            is_match = score >= SEUIL

            if is_match:
                st.markdown(
                    f"""
                    <div style="background-color: #d4edda; color: #155724; padding: 20px; border-radius: 10px; border-left: 8px solid #28a745; text-align: center;">
                        <span style="font-size: 30px; font-weight: bold; letter-spacing: 2px;">✅ MATCH</span>
                        <div style="margin-top: 10px; font-size: 18px; font-weight: 500;">
                            Score de similarité cosinus : <span style="font-size: 24px; font-weight: bold; font-family: monospace;">{score:.4f}</span>
                        </div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div style="background-color: #f8d7da; color: #721c24; padding: 20px; border-radius: 10px; border-left: 8px solid #dc3545; text-align: center;">
                        <span style="font-size: 30px; font-weight: bold; letter-spacing: 2px;">🚨 MISMATCH</span>
                        <div style="margin-top: 10px; font-size: 18px; font-weight: 500;">
                            Score de similarité cosinus : <span style="font-size: 24px; font-weight: bold; font-family: monospace;">{score:.4f}</span>
                        </div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
        else:
            st.info("Fournissez une image et un texte pour exécuter l'analyse.")
else:
    st.write("👈 Chargez un exemple ou recherchez un patient pour commencer.")