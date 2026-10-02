# Model Artifact

`rf_model.joblib` is the serialized Random Forest artifact used by the current demo.

Important compatibility note: scikit-learn/joblib serialized models can be
sensitive to library-version differences. A future training pipeline will record
the exact environment and regenerate the model reproducibly.

Do not treat untrusted `.joblib` or pickle-based model files as safe input.
