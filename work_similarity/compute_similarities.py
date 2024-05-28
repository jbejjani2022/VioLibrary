import os
import pandas as pd

from sklearn.metrics import jaccard_score
from sklearn.preprocessing import LabelEncoder

from work_similarity.utilities import convert_db_to_csv


# Calculate the similarity of each pair of works
# Use the following similarity metric. Assign
# - 1 if the `solo`, `form`, or `epoch` match, 0 otherwise
# - for `name`, use Jaccard string similarity


def compute_similarity_matrix():
    # Load the works and composers .csv files as dataframes
    works_df = pd.read_csv('work_similarity/data/works.csv')
    composers_df = pd.read_csv('work_similarity/data/composers.csv')
    
    # Rename the id col to 'work_id'
    works_df = works_df.rename(columns={'id': 'work_id'})
    
    # Merge works_df with composers_df on composer_id to get the 'epoch' column
    works_df = works_df.merge(composers_df[['id', 'epoch']], left_on='composer_id', right_on='id', how='left')

    # Drop the 'id' column after merge since it's redundant
    works_df = works_df.drop(columns=['id'])

    # Display the first few rows of the updated works_df
    works_df.head()
    
    # Encode categorical variables to facilitate numerical comparison
    label_encoders = {col: LabelEncoder().fit(works_df[col]) for col in ['form', 'epoch']}
    works_df_encoded = works_df.copy()
    for col, le in label_encoders.items():
        works_df_encoded[col] = le.transform(works_df[col])
    
    # Initialize the similarity matrix
    similarity_matrix = pd.DataFrame(0, index=works_df.index, columns=works_df.index, dtype=float)
    
    # Compute similarity scores
    for i in range(len(works_df)):
        for j in range(i, len(works_df)):
            if i == j:
                similarity_matrix.iloc[i, j] = 1.0
            else:
                name_similarity = jaccard_similarity(works_df.iloc[i]['name'], works_df.iloc[j]['name'])
                solo_similarity = 1 if works_df.iloc[i]['solo'] == works_df.iloc[j]['solo'] else 0
                form_similarity = 1 if works_df_encoded.iloc[i]['form'] == works_df_encoded.iloc[j]['form'] else 0
                epoch_similarity = 1 if works_df_encoded.iloc[i]['epoch'] == works_df_encoded.iloc[j]['epoch'] else 0

                # Combine similarities (simple average)
                total_similarity = (name_similarity + solo_similarity + form_similarity + epoch_similarity) / 4

                similarity_matrix.iloc[i, j] = total_similarity
                similarity_matrix.iloc[j, i] = total_similarity  # because the matrix is symmetric
    
    
    return similarity_matrix


# Compute Jaccard similarity for work names
def jaccard_similarity(str1, str2):
    set1, set2 = set(str1.split()), set(str2.split())
    return len(set1.intersection(set2)) / len(set1.union(set2))


if __name__ == '__main__':
    # Construct the relative path to api.db file
    db = os.path.join("..", "api.db")
    convert_db_to_csv(db, 'works')
    convert_db_to_csv(db, 'composers')
    
    similarity_matrix = compute_similarity_matrix()

    # Save the similarity matrix to a CSV file
    similarity_matrix.to_csv('data/similarity_matrix.csv', index=False)