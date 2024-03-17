from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score, roc_curve
import numpy as np


def get_classification_metrics(pred_trader):
    real, predicted = pred_trader.get_target(0), pred_trader.predictions[:-1]
    predicted = [i+1 for i in predicted]
    # print(real)
    # print(predicted)

    real_data = np.array(real[pred_trader.lag:])
    predicted_data = np.array(predicted)

    average_method = 'macro'

    accuracy = accuracy_score(real_data, predicted_data)
    precision = precision_score(real_data, predicted_data, average=average_method)
    recall = recall_score(real_data, predicted_data, average=average_method)

    return accuracy, precision, recall