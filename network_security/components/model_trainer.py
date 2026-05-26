import os
import sys
from network_security.exception.exception import NetworkSecurityException
from network_security.logging.logger import logger
from network_security.entity.config_entity import TrainingPipelineConfig, DataTransformationConfig, ModelTrainerConfig
from network_security.entity.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact
from network_security.constant.training_pipeline import MODEL_TRAINER_EXPECTED_SCORE, MODEL_TRAINER_OVER_FITTING_UNDER_FITTING_THRESHOLD

from network_security.utils.main_utils.utils import save_object, load_object
from network_security.utils.main_utils.utils import save_numpy_array_data, load_numpy_array_data, evaluate_model
from network_security.utils.ml_utils.model.estimator import NetworkModel
from network_security.utils.ml_utils.metric.classification_metric import get_classification_score
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier )
import mlflow

class ModelTrainer:
    def __init__(self, model_trainer_config: ModelTrainerConfig, data_transformation_artifact: DataTransformationArtifact):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def mlflow_tracking(self, model, train_metric, test_metric, model_report):
        # Asegúrate de que el servidor esté corriendo si usas http://localhost:5000
        # O usa una ruta local: mlflow.set_tracking_uri("file:///path/to/mlruns")
        mlflow.set_tracking_uri("http://localhost:5000") 
        mlflow.set_experiment("Network_Security_Experiment")
        with mlflow.start_run(run_name="Model_Trainer_Run"):
            mlflow.log_param("model_name", type(model).__name__)
            
            # Registrar métricas de Entrenamiento
            mlflow.log_metric("train_f1_score", train_metric.f1_score)
            mlflow.log_metric("train_precision_score", train_metric.precision_score)
            mlflow.log_metric("train_recall_score", train_metric.recall_score)

            # Registrar métricas de Prueba (Test)
            mlflow.log_metric("test_f1_score", test_metric.f1_score)
            mlflow.log_metric("test_precision_score", test_metric.precision_score)
            mlflow.log_metric("test_recall_score", test_metric.recall_score)

            for model_name, f1_score in model_report.items():
                mlflow.log_metric(f"{model_name}_f1_score", f1_score)
            
            # Logueamos el modelo de sklearn
            mlflow.sklearn.log_model(model, "sklearn_model")
        
    def train_model(self, x_train, y_train, x_test, y_test):
        try:
            models = {
                "Logistic Regression": LogisticRegression(),
                "K-Nearest Neighbors": KNeighborsClassifier(),
                "Decision Tree": DecisionTreeClassifier(),
                "Random Forest": RandomForestClassifier(),
                "Gradient Boosting": GradientBoostingClassifier(),
                "AdaBoost": AdaBoostClassifier()
            }

            parameters = {
                "Logistic Regression": {},
                "K-Nearest Neighbors": {"n_neighbors": [3, 5, 7], "weights": ["uniform", "distance"]},
                "Decision Tree": {"criterion": ["gini", "entropy"], "max_depth": [None, 10, 20]},
                "Random Forest": {"n_estimators": [100, 200], "max_depth": [None, 10, 20]},
                "Gradient Boosting": {"n_estimators": [100, 200], "learning_rate": [0.01, 0.1]},
                "AdaBoost": {"n_estimators": [100, 200], "learning_rate": [0.01, 0.1]}
            }


            model_report :dict = evaluate_model(x_train=x_train, y_train=y_train, x_test=x_test, y_test=y_test, models=models, param=parameters)
            best_model_score = max(model_report.values())
            best_model_name = list(model_report.keys())[list(model_report.values()).index(best_model_score)]
            best_model = models[best_model_name]

            if best_model_score < self.model_trainer_config.expected_accuracy:
                raise Exception(f"Best model found: {best_model_name} with score {best_model_score} "
                                f"is below the threshold of {self.model_trainer_config.expected_accuracy}")

            logger.info(f"Best model found: {best_model_name} with score: {best_model_score}")

            y_train_pred = best_model.predict(x_train)

            classification_train_metric = get_classification_score(y_true=y_train, y_pred=y_train_pred)   

            y_test_pred = best_model.predict(x_test)
            classification_test_metric = get_classification_score(y_true=y_test, y_pred=y_test_pred)
            # Check for Overfitting/Underfitting
            diff = abs(classification_train_metric.f1_score - classification_test_metric.f1_score)
            if diff > self.model_trainer_config.overfitting_underfitting_threshold:
                raise Exception(f"Model is overfitted/underfitted. F1-score difference: {diff} "
                                f"exceeds threshold {self.model_trainer_config.overfitting_underfitting_threshold}")

            preprocessor = load_object(file_path=self.data_transformation_artifact.preprocessed_object_file_path)
            model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
            os.makedirs(model_dir_path, exist_ok=True)
            model = NetworkModel(preprocessor=preprocessor, model=best_model)
            save_object(file_path=self.model_trainer_config.trained_model_file_path, obj=model)
            
            ## Sincronizar con MLflow: Ahora registramos las métricas y el modelo
            self.mlflow_tracking(best_model, classification_train_metric, classification_test_metric, model_report)
            # Opcional: Registrar también el objeto NetworkModel completo (con preprocesador) en MLflow
            mlflow.log_artifact(self.model_trainer_config.trained_model_file_path, artifact_path="final_model")

            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                train_metric_artifact=classification_train_metric,
                test_metric_artifact=classification_test_metric
            )
            
            logger.info(f"Model trainer artifact: {model_trainer_artifact}")
            return model_trainer_artifact   
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        try:
            logger.info("Loading transformed training and testing data")
            transformed_train_file_path = self.data_transformation_artifact.transformed_train_file_path
            transformed_test_file_path = self.data_transformation_artifact.transformed_test_file_path
            x_train = load_numpy_array_data(transformed_train_file_path)
            x_test = load_numpy_array_data(transformed_test_file_path)
            y_train = x_train[:, -1]
            y_test = x_test[:, -1]
            x_train = x_train[:, :-1]
            x_test = x_test[:, :-1]
            
            model_trainer_artifact = self.train_model(x_train, y_train, x_test, y_test)
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
           