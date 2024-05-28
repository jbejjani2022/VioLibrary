import pandas as pd
import os
from compute_similarities import compute_similarity_matrix
from utilities import convert_db_to_csv
import heapq
import csv


class Recommender():
    def __init__(self, k):
        # How many recommendations to make
        self.k = k
        
        if not os.path.exists('data/similarity_matrix.csv'):
            # Compute similarities between works
            self.similarity_matrix = compute_similarity_matrix()
            # Save the similarity matrix to a CSV file
            self.similarity_matrix.to_csv('data/similarity_matrix.csv', index=False)
        else:
            self.similarity_matrix = pd.read_csv('data/similarity_matrix.csv')
            
        # Lookup a work's name with its ID as key
        self.workID_to_name = {}
        with open('data/works.csv', newline='', encoding='ISO-8859-1') as csvfile:
            work_reader = csv.reader(csvfile)
            next(work_reader)
            for row in work_reader:
                workID = int(row[0])
                work_name = row[2]
                self.workID_to_name[workID] = work_name
                
    def getWorkName(self, workID):
        if int(workID) in self.workID_to_name:
            return self.workID_to_name[int(workID)]
        else:
            return ""
    
    def get_user_recommendations(self, user):
        """Get the k works that are most similar to 
        the user's current favorited works and are not
        already favorited

        Args:
            user (int): user id
        """
        # Construct the relative path to api.db file
        db = os.path.join("..", "api.db")
        convert_db_to_csv(db, 'favorites')
        
        favorites_df = pd.read_csv('data/favorites.csv')
        # List of `work_id`s in the `user`'s favorites
        favorited_works = favorites_df.loc[favorites_df['user_id'] == user, 'work_id'].values
        
        # Get the similarities of each work to each of the favorited works
        # list of lists
        similarities = [self.similarity_matrix.iloc[id] for id in favorited_works]
        
        # Flatten the list while keeping track of the original index of each work 
        flattened_similarities = []
        for i, ls in enumerate(similarities):
            for j, score in enumerate(ls):
                flattened_similarities.append((i, j, score))
        
        # Sort the neighboring works in descending order based on the similarity score
        neighbors = sorted(flattened_similarities, key=lambda x: x[2], reverse=True)
        
        count = 0
        k_nearest = []
        for work in neighbors:
            # Only recommend a work if it is not already in favorites
            if not work[1] in favorited_works:
                k_nearest.append(work)
                count += 1
                if count == self.k: break
        
        # Find the works with the top k largest similarity scores
        # k_nearest = heapq.nlargest(k, flattened_similarities, key=lambda x: x[2])
        # print([entry[2] for entry in k_nearest])
        
        # Recommendations are a list of (source, rec) tuples,
        # where source is the favorited work that is closest to the rec
        recommendations = [(self.getWorkName(favorited_works[neighbor[0]]), self.getWorkName(neighbor[1])) for neighbor in k_nearest]

        return recommendations
    

if __name__ == '__main__':
    recommender = Recommender(5)
    recommendations = recommender.get_user_recommendations(2)
    for i, rec in enumerate(recommendations):
        print(f'Rec {i}: {rec[1]}, from {rec[0]}')