import pandas as pd
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.tree import DecisionTreeClassifier, _tree
from sklearn.metrics import accuracy_score

data = pd.read_csv('processed_data.csv')

# Split into features and labels
X = data.iloc[:, [6, 12, 13]]
y = data.iloc[:, -1]

# Shuffle the data
data = data.sample(frac=1).reset_index(drop=True)

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
y_test
# Define the parameter grid
param_grid = {
    'max_depth': [2, 5, 6, 7, 8, 9],
    'min_samples_leaf': [2, 5, 8, 10, 20 ,30],
    'min_samples_split': [5, 8, 10, 20, 100],
    'ccp_alpha' : [0.001, 0.01, 0.015 ],

}
# Initialize GridSearchCV
grid_search = GridSearchCV(DecisionTreeClassifier(), param_grid, cv=5, scoring='accuracy')

# Train the models
grid_search.fit(X_train, y_train)

# Function to convert a tree to code
def tree_to_code(tree, feature_names):
    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
        for i in tree_.feature
    ]

    lines = []

    def recurse(node, depth):
        indent = "  " * depth
        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            name = feature_name[node]
            threshold = tree_.threshold[node]
            lines.append(f"{indent}if {name} <= {threshold}:")
            recurse(tree_.children_left[node], depth + 1)
            lines.append(f"{indent}else:  # if {name} > {threshold}")
            recurse(tree_.children_right[node], depth + 1)
        else:
            lines.append(f"{indent}return {tree_.value[node]}")

    recurse(0, 0)
    return lines

# Evaluate each model and count the lines of code
def count_thresholds(tree):
    return sum(node != _tree.TREE_UNDEFINED for node in tree.feature)

results = []
for params in grid_search.cv_results_['params']:
    clf = DecisionTreeClassifier(**params).fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    code_lines = tree_to_code(clf, feature_names=X.columns)
    threshold_count = count_thresholds(clf.tree_)
    # Extracting key parameter values
    param_values = f"Depth: {params['max_depth']}, Min Leaf: {params['min_samples_leaf']}, Min Split: {params['min_samples_split']}, Alpha: {params['ccp_alpha']}"
    results.append({'params': param_values, 'accuracy': accuracy, 'code_lines': len(code_lines), 'threshold_count': threshold_count})

results_df = pd.DataFrame(results)
results_df.sort_values(by=['accuracy', 'code_lines'], ascending=[False, True], inplace=True)
results_csv = 'results.csv'
results_df.to_csv(results_csv, index=False)
print(results_df)


def is_dominated(row, skyline_rows):
    """
    Check if the given row is dominated by any row in the skyline.
    """
    for skyline_row in skyline_rows:
        if (skyline_row['accuracy'] >= row['accuracy'] and 
            skyline_row['threshold_count'] <= row['threshold_count']):
            return True
    return False

# Load data
data = pd.read_csv(results_csv)

# Apply skyline filtering
skyline_rows = [data.iloc[0].to_dict()]

for _, row in data.iloc[1:].iterrows():
    row_dict = row.to_dict()
    if not is_dominated(row_dict, skyline_rows):
        skyline_rows.append(row_dict)

skyline = pd.DataFrame(skyline_rows)

skyline.to_csv('skyline_results.csv', index=False)
