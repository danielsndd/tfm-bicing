from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

def perform_random_forest(data):
    X = data[['hour', 'day_of_week', 'lat', 'lon', 'altitude']]
    y = data['num_bikes_available']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    return model, X_test, y_test