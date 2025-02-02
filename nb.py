'''
Author Steve G. Mwangi
2020
'''


import pandas as pd
import pandas as pd
import numpy as np
import io, sys, os, csv, logging, itertools, warnings
import xml.etree.ElementTree as et
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
from sklearn.externals import joblib
from dicttoxml import dicttoxml

warnings.filterwarnings('ignore', category=FutureWarning)
pd.set_option('mode.chained_assignment', None)

#print(sys.argv, "\n 0: ", sys.argv[0], "\n 2: ", sys.argv[2])
input_dir = str(sys.argv[2]) 
output_dir = str(sys.argv[4])
#os.chdir("..")
#print(sys.path[0])
# TESTING & TRAINING DATA
profile_test_csv = "{}/{}".format(input_dir, "/profile/profile.csv")
relation_test_csv = "{}/{}".format(input_dir, "/relation/relation.csv")
profile_train_csv = str(sys.path[0])+ "/data/training/profile/profile.csv"
relation_train_csv = str(sys.path[0]) + "/data/training/relation/relation.csv"
# str(os.path.abspath(os.curdir))

# DATA FRAMES
testing_profile_df = pd.read_csv(profile_test_csv)
testing_relation_df = pd.read_csv(relation_test_csv, converters={'like_id': lambda x: str(x)})
training_profile_df = pd.read_csv(profile_train_csv)
training_relation_df = pd.read_csv(relation_train_csv, converters={'like_id': lambda x: str(x)})
	
# Create a Column for Age Groups
training_profile_df["age_group"] = 0
training_profile_df["age_group"].loc[training_profile_df["age"] < 25] = 0
training_profile_df["age_group"].loc[(training_profile_df["age"] >= 25) & (training_profile_df["age"] < 35)] = 1
training_profile_df["age_group"].loc[(training_profile_df["age"] >= 35) & (training_profile_df["age"] < 50)] = 2
training_profile_df["age_group"].loc[training_profile_df["age"] > 50] = 3

counter = training_relation_df["like_id"].value_counts()
groups = training_relation_df[training_relation_df["like_id"].isin(counter[counter < 900].index & counter[counter > 1].index)]

merged = groups.groupby("userid",as_index=False).agg({"like_id": lambda x: "%s" % " ".join(x)})
merged_training = (pd.merge(training_profile_df, merged, left_on="userid", right_on="userid"))
merged_relation = testing_relation_df.groupby("userid", as_index=False).agg({"like_id": lambda x: "%s" % " ".join(x)})
merged_testing = (pd.merge(testing_profile_df, merged_relation, left_on="userid", right_on="userid"))

count_vect = CountVectorizer()
yy_train_gender = merged_training["gender"]
yy_train_age = merged_training["age_group"]
xx_train_age = count_vect.fit_transform(merged_training["like_id"])
xx_test_age = count_vect.transform(merged_testing["like_id"])
xx_train_gender = count_vect.fit_transform(merged_training["like_id"])
xx_test_gender = count_vect.transform(merged_testing["like_id"])

# Multinomial means more values than just binary value
# MultinomialNB assumes count data, like the number of words in a sample text
clf_age = MultinomialNB()
clf_gender = MultinomialNB()
# Training by giving the X_part, Y_Part and training the classifier
clf_age.fit(xx_train_age, yy_train_age)
clf_gender.fit(xx_train_gender, yy_train_gender)

age_predict_likes = clf_age.predict(xx_test_age)
gender_predict_likes = clf_gender.predict(xx_test_gender)

list_of_gender = []
list_of_age = []
age_set = ["xx-24", "25-34", "35-49", "50-xx"]

for x in age_predict_likes:
	list_of_age.append(age_set[x])

for x in gender_predict_likes:
    if x < 1:
        list_of_gender.append("0")
    else:
        list_of_gender.append("1")

#print(list_of_gender)
for i in testing_profile_df.userid:
    index = 0
    elem = et.Element("user", attrib={
        "\n" + "\t" + "id": i,
        "\n" + "age_group":list_of_age[index],
        "\n" + "gender": list_of_gender[index],
        "\n" + "extrovert": str(3.49),
        "\n" + "neurotic": str(2.73),
        "\n" + "agreeable": str(3.58),
        "\n" + "conscientious": str(3.45),
        "\n" + "open": str(3.91)})
    index += 1
    tree = et.ElementTree(element=elem)
    filename = "{}{}.xml".format(output_dir, i)
    with open(filename, 'wb') as f:
        tree.write(f)

