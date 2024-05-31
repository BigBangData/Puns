# one-time script to download w2v model
import os
import gensim.downloader as api

# Download a pre-trained Word2Vec model
model_name = 'word2vec-google-news-300'
word2vec_model = api.load(model_name)

if not os.path.exists('models'):
    os.makedirs('models')

# Save the model to a file for future use
model_path = os.path.join('models', model_name)
word2vec_model.save(model_path)
