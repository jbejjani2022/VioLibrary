from surprise import KNNBasic, Dataset, Reader

from collections import defaultdict
from operator import itemgetter
import heapq 

import os
import csv

# load in the movie ratings and return dataset
def load_dataset():
    reader = Reader(line_format = 'user item rating timestamp', sep=',', skip_lines=1)
    ratings_dataset = Dataset.load_from_file('ml-latest-small/ratings.csv', reader=reader)
    
    # Lookup a movie's name with its Movielens ID as key
    movieID_to_name = {}
    with open('ml-latest-small/movies.csv', newline='', encoding='ISO-8859-1') as csvfile:
        movie_reader = csv.reader(csvfile)
        next(movie_reader)
        for row in movie_reader:
            movieID = int(row[0])
            movie_name = row[1]
            movieID_to_name[movieID] = movie_name
            
    # Return both the dataset and the lookup table
    return ratings_dataset, movieID_to_name

dataset, movieID_to_name = load_dataset()
# Build full Surprise training set from dataset
trainset = dataset.build_full_trainset()

sim_options = {
    'name': 'cosine',
    'user_based': False # using item-based collaborative filtering
}

algo = KNNBasic(sim_options=sim_options)
algo.fit(trainset)
similarity_matrix = algo.compute_similarities()

# Pick a user ID (numeric string)
# Find the recommendations for that user
test_user = '500'

# Get recommended items based off of similarity to the user's K top-rated items
k = 20

# to find a user inside the trainset, need to convert their RAW ID
# to their INNER ID
test_user_iid = trainset.to_inner_uid(test_user)

test_user_ratings = trainset.ur[test_user_iid]
k_neighbors = heapq.nlargest(k, test_user_ratings, key=lambda t: t[1])

# default dict is a standard dict except a new entry is made when 
# trying to access a key that does not exist
candidates = defaultdict(float)

# find the items most similar to k_neighbors - these are our recommendation candidates
for itemID, rating in k_neighbors:
    try:
        similarities = similarity_matrix[itemID]
        for innerID, score in enumerate(similarities):
            candidates[innerID] += score * (rating / 5.0) # the higher the rating, the more we weight the similar candidate
    except:
        continue
    
    
def getMovieName(movieID):
    if int(movieID) in movieID_to_name:
        return movieID_to_name[int(movieID)]
    else:
        return ""
    
# Build dictionary of movies the user has watched
watched = {}
for itemID, rating in trainset.ur[test_user_iid]:
    watched[itemID] = 1
    
# Add items to user's list of recommendations,
# if they are similar to their favorite movies AND 
# have not been watched already
recommendations = []

count = 0
for itemID, rating_sum in sorted(candidates.items(), key=itemgetter(1), reverse=True):
    if not itemID in watched:
        recommendations.append(getMovieName(trainset.to_raw_iid(itemID)))
        count += 1
        if (count == 10): break # Stop after finding top 10 recommendations

for rec in recommendations:
    print("Movie: ", rec)