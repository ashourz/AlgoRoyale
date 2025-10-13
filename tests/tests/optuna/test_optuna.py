import optuna


def objective(trial):
    x = trial.suggest_float("x", -10, 10)
    return (x - 2) ** 2


def test_optuna():
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=50)

    print("Best value:", study.best_value)
    print("Best params:", study.best_params)
    assert study.best_value < 1e-2
