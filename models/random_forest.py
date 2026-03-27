from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from .side_functions import feature_extraction, found_best_span


class RandomForestModel:
    def __init__(self, df, col, params={"min": None, "max": None}):
        model, pred, stats = self._train(df, col, params=params)
        self.model = model
        self.train_predictions = pred
        self.training_stats = stats
        self.features_importances = model.feature_importances_

    def _train(self, df, col, cv=False, params={"min": None, "max": None}):
        if params["min"] is not None and params["max"] is not None:
            mask = (
                (df[col] >= params["min"])
                & (df[col] <= params["max"])
                & df["ExternalTemp"].notna()
            )
        else:
            mask = df["ExternalTemp"].notna()
        feautures = feature_extraction(df[mask])
        target = df.loc[mask, col]
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(feautures, target)
        predictions = model.predict(feautures)
        mse = mean_squared_error(target, predictions)
        r2 = r2_score(target, predictions)
        stats = {
            "mse": mse,
            "r2": r2,
        }

        return model, predictions, stats

    def predict(self, df):
        feautures = feature_extraction(df)
        return self.model.predict(feautures)
