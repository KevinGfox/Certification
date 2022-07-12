# Import libraries
import pandas as pd
import numpy as np
import time
import os
import mlflow
from mlflow.models.signature import infer_signature

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import  OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression



if __name__ == "__main__":

    ### MLFLOW Experiment setup
    experiment_name="CarPrice_predictor"
    mlflow.set_experiment(experiment_name)
    experiment = mlflow.get_experiment_by_name(experiment_name)
    
    client = mlflow.tracking.MlflowClient()
    run = client.create_run(experiment.experiment_id)

    print("training model...")
    
    # Time execution
    start_time = time.time()

    # Call mlflow autolog
    mlflow.sklearn.autolog()

    # Import dataset
    data = pd.read_csv('data/get_around_pricing_project.csv')

    # Remove useless column
    data = data.iloc[: , 1:]

    # Define X and y
    features = data.columns.values[:-1]
    target = data.columns.values[-1]
    X = data.loc[:,features]
    y = data.loc[:,target]

    # Train test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, random_state = 0)

    # Preprocessing
    numeric_features = [1,2]
    categorical_features = [0,3,4,8,6,7,8,9,10,11,12]
    num_transformer = Pipeline(steps = [('scaler', StandardScaler())])
    cat_transformer = Pipeline(steps = [('encoder', OneHotEncoder(handle_unknown = 'ignore'))])
    ''' handle_unknown = ignore : When an unknown category is encountered during transform,
    the resulting one-hot encoded columns for this feature will be all zeros. 
    '''
    preprocess = ColumnTransformer(
            transformers=[
                    ('num', num_transformer, numeric_features),
                    ('cat', cat_transformer, categorical_features)
                    ])

    model = Pipeline(steps=[("Preprocessing", preprocess),
                            ("Regressor", LinearRegression())
                            ])                 

    # Log experiment to MLFlow
    with mlflow.start_run(run_id = run.info.run_id) as run:
        model.fit(X_train, y_train)
        predictions = model.predict(X_train)

    # Log model seperately to have more flexibility on setup 
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="CarPrice_predictor",
            registered_model_name="CarPrice_predictor_LineReg",
            signature=infer_signature(X_train, predictions)
            )
            
        print("...Done!")
        print(f"---Total training time: {time.time()-start_time}")