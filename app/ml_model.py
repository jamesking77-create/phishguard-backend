import pickle

def load_ml_model(model_path, vectorizer_path):
    with open(model_path, 'rb') as model_file, open(vectorizer_path, 'rb') as vectorizer_file:
        model = pickle.load(model_file)
        vectorizer = pickle.load(vectorizer_file)
    return model, vectorizer
