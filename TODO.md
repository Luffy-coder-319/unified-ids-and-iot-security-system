# TODO: Fix combine_predictions to use retrained models

- [x] Modify `combine_predictions` method to accept features as input and internally generate predictions from retrained RF and DL models
- [x] Update `predict_threat` method to use `combine_predictions` for ensemble logic instead of manual combination
- [x] Test the changes to ensure predictions use retrained models correctly
