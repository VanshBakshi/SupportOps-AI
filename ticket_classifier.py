"""Training-ready SupportOps ticket category classifier."""
from pathlib import Path
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

ROOT=Path(__file__).resolve().parents[2]
MODEL_PATH=ROOT/'ai'/'models'/'ticket_classifier.joblib'

def build_model():
    return Pipeline([('tfidf',TfidfVectorizer(ngram_range=(1,2),sublinear_tf=True,max_features=50000)),('classifier',LogisticRegression(max_iter=2000,class_weight='balanced'))])

def train(texts,labels,path=MODEL_PATH):
    model=build_model(); model.fit(texts,labels); Path(path).parent.mkdir(parents=True,exist_ok=True); joblib.dump(model,path); return model

def load(path=MODEL_PATH): return joblib.load(path)

def predict(model,text,top_k=3):
    probs=model.predict_proba([text])[0]; classes=model.classes_; order=probs.argsort()[::-1][:top_k]; return [{'category':str(classes[i]),'confidence':float(probs[i])} for i in order]
