import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
import pickle

# Load dataset
data = {
    'text': [
        'Click this link to win a prize!',
        'Your account has been hacked, reset your password.',
        'Congratulations, you have won a lottery.',
        'Monthly report attached.',
        'Meeting tomorrow at 10 AM.',
        'Please review the attached document.'
    ],
    'label': [
        'phishing', 'phishing', 'phishing', 'not_phishing', 'not_phishing', 'not_phishing'
    ]
}

df = pd.DataFrame(data)

# Vectorize text data
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df['text'])
y = df['label']

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a model
model = MultinomialNB()
model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
print(f'Accuracy: {accuracy_score(y_test, y_pred)}')

# Save the model and vectorizer
with open('models/phishing_detection_model.pkl', 'wb') as model_file:
    pickle.dump(model, model_file)

with open('models/vectorizer.pkl', 'wb') as vectorizer_file:
    pickle.dump(vectorizer, vectorizer_file)
