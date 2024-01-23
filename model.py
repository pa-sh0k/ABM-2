import xgboost as xgb
import pandas as pd
from sklearn.exceptions import NotFittedError
from sklearn.metrics import accuracy_score
from AgentBasedModel import Simulator


def update_model_with_dataset(model, N, prices, *features, test_size=0.3):
    data = pd.DataFrame({f'feature{i+1}': feat for i, feat in enumerate(features)})
    data['price'] = prices

    future_prices = data['price'].shift(-N)

    data['target'] = (future_prices > data['price']).astype(int)
    data.dropna(subset=['target'], inplace=True)

    X = data.drop('target', axis=1)
    y = data['target']

    split_index = int((1 - test_size) * len(data))
    X_train, X_test = X[:split_index], X[split_index:]
    y_train, y_test = y[:split_index], y[split_index:]

    try:
        model.get_booster()
        is_trained = True
    except NotFittedError:
        is_trained = False

    if is_trained:
        model.fit(X_train, y_train, xgb_model=model.get_booster())
    else:
        model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    return model, accuracy


def iterative_training(N, M, simulator_settings):
    model = xgb.XGBClassifier(objective='binary:logistic', use_label_encoder=False, eval_metric='logloss')
    accuracies = []

    for i in range(M):
        simulator = Simulator(**simulator_settings)
        prices, features = get_data(simulator, 2000)
        model, accuracy = update_model_with_dataset(model, N, prices, *features)
        accuracies.append(accuracy)
        importance = model.feature_importances_
        for i, v in enumerate(importance):
            print('Feature: %0d, Score: %.5f' % (i, v))

    return model, accuracies


def get_data(simulator, it_num, idx=1):
    simulator.simulate(it_num, silent=False)
    prices = simulator.info.prices.copy()[idx]
    feature_names = ['ob_imbs', 'smart_pr', 'sign_vol', 'prets', 'tr_signs', 'ag_buys', 'ag_sells']
    features = [getattr(simulator.info, name).copy()[idx] for name in feature_names]
    return prices, features

