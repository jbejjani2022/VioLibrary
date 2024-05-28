from surprise import KNNBasic, Dataset, Reader
from collections import defaultdict
from operator import itemgetter

import sqlite3
import csv
import pandas as pd
import os


def convert_db_to_csv(db, table_name):
    # Connect to the SQLite database
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # Execute a query to select all data from the specified table
    cursor.execute(f"SELECT * FROM {table_name}")

    # Fetch all results
    rows = cursor.fetchall()

    # Get column names
    column_names = [description[0] for description in cursor.description]

    data_folder = 'data'
    
    # Create the data folder if it doesn't exist
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
        
    # Specify the CSV file path
    csv_file = os.path.join(data_folder, f'{table_name}.csv')

    # Write data to CSV file
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow(column_names)
        # Write rows
        writer.writerows(rows)

    # Close the cursor and connection
    cursor.close()
    conn.close()


class Recommender():
    def __init__(self, data):
        # Load in dataset
        self.data = data
        reader = Reader(line_format = 'user item rating', sep=',', skip_lines=1)
        self.dataset = Dataset.load_from_file(data, reader=reader)
        # Build full Surprise training set from dataset
        self.trainset = self.dataset.build_full_trainset()
        
        # Define similarity measure
        self.sim_options = {
            'name': 'cosine',
            'user_based': False # using item-based collaborative filtering
        }
        
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
        
    def train(self):
        algo = KNNBasic(sim_options=self.sim_options)
        algo.fit(self.trainset)
        self.similarity_matrix = algo.compute_similarities()
        print(self.similarity_matrix)
        
    def get_user_recommendations(self, user : str):
        # Return a list of work recommendations for the given user
        # Get recommended items based off of similarity to 'neighbors': the works
        # the user has already added to favorites
        
        # To find a user inside the trainset, need to convert their RAW ID to their INNER ID
        user_iid = self.trainset.to_inner_uid(user)
        user_favorites = self.trainset.ur[user_iid]
        
        # Default dict is a standard dict except a new entry is made when 
        # trying to access a key that does not exist
        candidates = defaultdict(float)

        # Find the items most similar to user_favorites - these are our recommendation candidates
        for workID, rating in user_favorites:
            try:
                print("neighbor: ", workID, rating)
                similarities = self.similarity_matrix[workID]
                print(f'{len(similarities)} similarities')
                print("similarity scores: ", similarities)
                for innerID, score in enumerate(similarities):
                    candidates[innerID] += score # * (rating / 5.0) # the higher the rating, the more we weight the similar candidate
            except:
                continue
        print("candidates: ", candidates)
        # Add items to user's list of recommendations,
        # if they are similar to their favorite movies AND 
        # have not been watched already
        recommendations = []
        
        # Get list of WorkIDs that are in user's favorites
        favorited = [favorite[0] for favorite in user_favorites]
        
        count = 0
        for workID, rating_sum in sorted(candidates.items(), key=itemgetter(1), reverse=True):
            #if not workID in favorited:
                recommendations.append(self.getWorkName(self.trainset.to_raw_iid(workID)))
                count += 1
                if (count == 10): break # Stop after finding top 10 recommendations
        print("recommendations: ", recommendations)
        return recommendations


def recommendFavorites(user):
    convert_db_to_csv('api.db', 'favorites')
    data_path = 'data/favorites.csv'
    
    # Clean up favorites.csv so it follows 'user item rating' format
    # i.e. remove year,month,day,hour,minute,second cols and add rating col 
    # Read the CSV file into a DataFrame
    df = pd.read_csv(data_path)

    # Remove the columns year, month, day, hour, minute, second
    df = df.drop(columns=['year', 'month', 'day', 'hour', 'minute', 'second'])

    # Add a new column called 'rating' with value 5.0 for each row
    # i.e. we equate the user favoriting a work to giving it a rating of 5.0
    # simplifying assumption: all favorites are 'favored' equally
    df['rating'] = 5.0

    # Overwrite the CSV file with the modified DataFrame
    df.to_csv(data_path, index=False)
    
    # Initialize and train a Recommender object
    recommender = Recommender(data_path)
    recommender.train()
    
    return recommender.get_user_recommendations(user)


if __name__ == '__main__':
    convert_db_to_csv('api.db', 'works')
    convert_db_to_csv('api.db', 'composers')
    convert_db_to_csv('api.db', 'favorites')
    convert_db_to_csv('api.db', 'libraries')
    user = '2'
    recommendations = recommendFavorites(user)
    for rec in recommendations:
        print("Work: ", rec)
        