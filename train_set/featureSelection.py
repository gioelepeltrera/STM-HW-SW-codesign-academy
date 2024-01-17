import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from sklearn.tree import _tree

data = pd.read_csv('./processed_data.csv')

X = data.iloc[:, :-1]  # all columns except the last one
y = data.iloc[:, -1]   # the last column

# Shuffle the data
data = data.sample(frac=1).reset_index(drop=True)

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Create a Decision Tree Classifier
clf = DecisionTreeClassifier()

clf.fit(X_train, y_train)

# Predict on the test set
y_pred = clf.predict(X_test)
# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)

#tree_to_code(clf, feature_names=X.columns)
print("Feature importances: ",clf.feature_importances_)
print(f"Accuracy: {accuracy}")
