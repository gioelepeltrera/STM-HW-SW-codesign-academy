import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from sklearn.tree import _tree

def tree_to_code(tree, feature_names):
    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
        for i in tree_.feature
    ]

    def recurse(node, depth):
        indent = "  " * depth
        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            name = feature_name[node]
            threshold = tree_.threshold[node]
            print(f"{indent}if {name} <= {threshold}:")
            recurse(tree_.children_left[node], depth + 1)
            print(f"{indent}else:  # if {name} > {threshold}")
            recurse(tree_.children_right[node], depth + 1)
        else:
            print(f"{indent}return {tree_.value[node]}")

    recurse(0, 0)

# Load the dataset
data = pd.read_csv('./processed_data.csv')

# Split into features and labels
X = data.iloc[:, [6, 12, 13]]
y = data.iloc[:, -1]

# Shuffle the data
data = data.sample(frac=1).reset_index(drop=True)

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Create a Decision Tree Classifier
clf = DecisionTreeClassifier(
    max_depth=5, 
    min_samples_leaf=2, 
    min_samples_split=5, 
    ccp_alpha=0.01
)
# Train the model
clf.fit(X_train, y_train)

# Predict on the test set
y_pred = clf.predict(X_test)
# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)

tree_to_code(clf, feature_names=X.columns)
print("Feature importances: ",clf.feature_importances_)
print(f"Accuracy: {accuracy}")
