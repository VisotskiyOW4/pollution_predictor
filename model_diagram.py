from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.utils import plot_model

model = Sequential([
    Dense(32, activation='relu', input_shape=(4,), name='Input_Layer'),
    Dense(16, activation='relu', name='Hidden_Layer'),
    Dense(1, activation='sigmoid', name='Output_Layer')
])

plot_model(model, to_file='model_architecture.png', show_shapes=True, show_layer_names=True)
