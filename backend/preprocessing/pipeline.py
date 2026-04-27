"""
preprocessing/pipeline.py
8-step preprocessing pipeline as described in ARCHITECTURE.MD §3.3
"""

import io
import json
import pandas as pd
import numpy as np
from scipy import stats


class PreprocessingPipeline:
    """
    Chains 8 preprocessing steps and produces:
      - cleaned DataFrame
      - preprocessing summary report (dict → JSON-serialisable)
    """

    def __init__(
        self,
        missing_strategy: str = "mean",   # mean | median | mode | drop
        outlier_method: str = "iqr",      # iqr | zscore | none
        encoding_method: str = "onehot",  # onehot | label
        scaling_method: str = "standard", # standard | minmax | none
        outlier_threshold: float = 1.5,   # IQR multiplier OR Z-score cutoff
        missing_col_threshold: float = 0.5,  # drop column if > 50 % missing
    ):
        self.missing_strategy = missing_strategy
        self.outlier_method = outlier_method
        self.encoding_method = encoding_method
        self.scaling_method = scaling_method
        self.outlier_threshold = outlier_threshold
        self.missing_col_threshold = missing_col_threshold

        self.report: dict = {}
        self._encoder_columns: list = []
        self._scaler_params: dict = {}

    # ── Public API ────────────────────────────────────────────────────────────

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        self.report = {
            "original_shape": list(df.shape),
            "steps": [],
        }

        df = df.copy()
        df = self._step1_schema(df)
        df = self._step2_missing(df)
        df = self._step3_duplicates(df)
        df = self._step4_outliers(df)
        df = self._step5_dtype_normalise(df)
        df = self._step6_encode(df)
        df = self._step7_scale(df)
        self._step8_report(df)

        return df

    def get_report(self) -> dict:
        return self.report

    # ── Step 1: Schema Detection ──────────────────────────────────────────────

    def _step1_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        schema = {
            col: str(df[col].dtype) for col in df.columns
        }
        missing_per_col = df.isnull().sum().to_dict()

        self.report["schema"] = schema
        self.report["missing_per_column"] = {
            k: int(v) for k, v in missing_per_col.items()
        }
        self.report["duplicate_rows"] = int(df.duplicated().sum())
        self.report["steps"].append("schema_detection")
        return df

    # ── Step 2: Missing Value Handler ─────────────────────────────────────────

    def _step2_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        # Drop columns with too many missing values
        threshold = int(self.missing_col_threshold * len(df))
        cols_before = set(df.columns)
        df = df.dropna(axis=1, thresh=threshold)
        dropped_cols = list(cols_before - set(df.columns))

        imputed = {}
        for col in df.columns:
            n_missing = df[col].isnull().sum()
            if n_missing == 0:
                continue
            if df[col].dtype in [np.float64, np.int64, float, int] or pd.api.types.is_numeric_dtype(df[col]):
                if self.missing_strategy == "mean":
                    fill_val = df[col].mean()
                elif self.missing_strategy == "median":
                    fill_val = df[col].median()
                else:
                    fill_val = df[col].mode()[0] if not df[col].mode().empty else 0
                df[col] = df[col].fillna(fill_val)
                imputed[col] = {"strategy": self.missing_strategy, "fill_value": float(fill_val), "n_imputed": int(n_missing)}
            else:
                fill_val = df[col].mode()[0] if not df[col].mode().empty else "Unknown"
                df[col] = df[col].fillna(fill_val)
                imputed[col] = {"strategy": "mode", "fill_value": str(fill_val), "n_imputed": int(n_missing)}

        self.report["missing_value_handling"] = {
            "dropped_columns": dropped_cols,
            "imputed_columns": imputed,
        }
        self.report["steps"].append("missing_value_handler")
        return df

    # ── Step 3: Duplicate Remover ─────────────────────────────────────────────

    def _step3_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        n_before = len(df)
        df = df.drop_duplicates()
        n_removed = n_before - len(df)
        self.report["duplicates_removed"] = int(n_removed)
        self.report["steps"].append("duplicate_remover")
        return df

    # ── Step 4: Outlier Detector ──────────────────────────────────────────────

    def _step4_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.outlier_method == "none":
            self.report["outliers"] = {"method": "none", "rows_removed": 0}
            return df

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        n_before = len(df)
        mask = pd.Series([True] * len(df), index=df.index)

        if self.outlier_method == "iqr":
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - self.outlier_threshold * IQR
                upper = Q3 + self.outlier_threshold * IQR
                mask &= (df[col] >= lower) & (df[col] <= upper)
        elif self.outlier_method == "zscore":
            z_scores = np.abs(stats.zscore(df[numeric_cols].fillna(0)))
            mask &= (z_scores < self.outlier_threshold).all(axis=1)

        df = df[mask]
        self.report["outliers"] = {
            "method": self.outlier_method,
            "rows_removed": int(n_before - len(df)),
        }
        self.report["steps"].append("outlier_detector")
        return df

    # ── Step 5: Data Type Normalizer ──────────────────────────────────────────

    def _step5_dtype_normalise(self, df: pd.DataFrame) -> pd.DataFrame:
        parsed = []
        for col in df.columns:
            if df[col].dtype == object:
                # Try parse as datetime
                try:
                    parsed_col = pd.to_datetime(df[col])
                    df[col] = parsed_col
                    parsed.append(col)
                except Exception:
                    pass
        self.report["datetime_parsed"] = parsed
        self.report["steps"].append("dtype_normaliser")
        return df

    # ── Step 6: Feature Encoder ───────────────────────────────────────────────

    def _step6_encode(self, df: pd.DataFrame) -> pd.DataFrame:
        cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        # Exclude datetime columns
        cat_cols = [c for c in cat_cols if not pd.api.types.is_datetime64_any_dtype(df[c])]
        self._encoder_columns = cat_cols

        if not cat_cols:
            self.report["encoding"] = {"method": self.encoding_method, "columns": []}
            self.report["steps"].append("feature_encoder")
            return df

        if self.encoding_method == "label":
            label_maps = {}
            for col in cat_cols:
                df[col] = df[col].astype("category")
                label_maps[col] = dict(enumerate(df[col].cat.categories))
                df[col] = df[col].cat.codes
            self.report["encoding"] = {
                "method": "label",
                "columns": cat_cols,
                "label_maps": label_maps,
            }
        else:  # onehot
            df = pd.get_dummies(df, columns=cat_cols, drop_first=False)
            new_cols = [c for c in df.columns if c not in self._encoder_columns]
            self.report["encoding"] = {
                "method": "onehot",
                "original_columns": cat_cols,
                "new_columns": list(df.select_dtypes(exclude=[np.number]).columns),
            }

        self.report["steps"].append("feature_encoder")
        return df

    # ── Step 7: Feature Scaler ────────────────────────────────────────────────

    def _step7_scale(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.scaling_method == "none":
            self.report["scaling"] = {"method": "none", "columns": []}
            self.report["steps"].append("feature_scaler")
            return df

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        if self.scaling_method == "standard":
            for col in numeric_cols:
                mean = df[col].mean()
                std = df[col].std()
                if std == 0:
                    continue
                df[col] = (df[col] - mean) / std
                self._scaler_params[col] = {"mean": float(mean), "std": float(std)}
        elif self.scaling_method == "minmax":
            for col in numeric_cols:
                col_min = df[col].min()
                col_max = df[col].max()
                rng = col_max - col_min
                if rng == 0:
                    continue
                df[col] = (df[col] - col_min) / rng
                self._scaler_params[col] = {"min": float(col_min), "max": float(col_max)}

        self.report["scaling"] = {
            "method": self.scaling_method,
            "columns": numeric_cols,
            "params": self._scaler_params,
        }
        self.report["steps"].append("feature_scaler")
        return df

    # ── Step 8: Preprocessing Report ─────────────────────────────────────────

    def _step8_report(self, df: pd.DataFrame):
        self.report["cleaned_shape"] = list(df.shape)
        self.report["steps"].append("report_generator")
        self.report["summary"] = (
            f"Original: {self.report['original_shape'][0]} rows × "
            f"{self.report['original_shape'][1]} cols  →  "
            f"Cleaned: {self.report['cleaned_shape'][0]} rows × "
            f"{self.report['cleaned_shape'][1]} cols"
        )
